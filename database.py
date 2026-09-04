"""
Módulo de conexión a MySQL con Circuit Breaker y Reutilización por Request Context.
Maneja reintentos automáticos cuando la base de datos no está disponible
y mantiene una única conexión por petición para minimizar la latencia de red.
Cuando MOCK_MODE está activo, aísla por completo el sistema de la BD (cero conexiones).
"""
import os
import pymysql
import time
import threading
from dotenv import load_dotenv
from flask import current_app, g, has_request_context

load_dotenv()


# Estados del Circuit Breaker
STATE_CLOSED = "CLOSED"        # Operación normal con base de datos
STATE_OPEN = "OPEN"            # Circuito abierto tras fallos; fast-fail sin intentar conexión
STATE_HALF_OPEN = "HALF_OPEN"  # Prueba de reconexión tras expirar el intervalo de espera

# Estado global del circuit breaker
DB_AVAILABLE = False
_circuit_state = STATE_CLOSED
_last_db_attempt = 0.0
_db_fail_count = 0
_DB_RETRY_INTERVAL = 15  # segundos entre reintentos si la BD falla
_DB_TIMEOUT = 5.0        # timeout de conexión en segundos
_FAIL_THRESHOLD = 1      # fallos consecutivos requeridos para abrir el circuito
_db_lock = threading.Lock()


def is_mock_mode():
    """
    Determina si el modo mock está activado en la app o por entorno.
    Permite omitir cualquier intento de conexión hacia la BD.
    """
    if has_request_context() or current_app:
        try:
            return bool(current_app.config.get('MOCK_MODE', False))
        except RuntimeError:
            pass
    return os.getenv('MOCK_MODE', 'False').lower() in ('true', '1', 't', 'yes')


class _RequestScopedConnection:
    """
    Wrapper transparente sobre pymysql.Connection.
    Intercepta close() durante la petición para permitir que múltiples servicios
    reutilicen la misma conexión SSL/TCP. La conexión real se cierra al finalizar
    el ciclo de vida de la solicitud (teardown_appcontext).
    """
    def __init__(self, real_conn):
        self._real_conn = real_conn

    def close(self):
        # No cerramos la conexión subyacente para permitir reutilización en la misma petición
        pass

    def _actual_close(self):
        try:
            if self._real_conn and getattr(self._real_conn, 'open', False):
                self._real_conn.close()
        except Exception:
            pass

    def __getattr__(self, name):
        return getattr(self._real_conn, name)


def _create_raw_connection():
    db_host = current_app.config.get('DB_HOST', 'localhost')
    timeout = current_app.config.get('DB_TIMEOUT', _DB_TIMEOUT)
    use_ssl = current_app.config.get('DB_SSL', True) and db_host not in ('localhost', '127.0.0.1')
    ssl_kwargs = {'ssl': {'ssl_mode': 'REQUIRED'}} if use_ssl else {}

    return pymysql.connect(
        host=db_host,
        port=current_app.config.get('DB_PORT', 3306),
        user=current_app.config.get('DB_USER', 'root'),
        password=current_app.config.get('DB_PASSWORD', ''),
        database=current_app.config.get('DB_NAME', 'serv_comunitario'),
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=timeout,
        read_timeout=timeout,
        write_timeout=timeout,
        charset='utf8mb4',
        **ssl_kwargs
    )


def get_db_connection():
    """
    Obtiene la conexión a MySQL reutilizando la del request actual si existe,
    o creando una nueva si es necesario, protegida por circuit breaker.
    Si MOCK_MODE está activado, retorna None de inmediato sin abrir sockets de red.
    """
    global DB_AVAILABLE, _circuit_state, _last_db_attempt, _db_fail_count

    # 1. Cero intentos de conexión cuando el modo mock está activado
    if is_mock_mode():
        return None

    # 2. Reutilización por request context
    if has_request_context():
        scoped = getattr(g, '_db_conn', None)
        if scoped is not None:
            try:
                if getattr(scoped._real_conn, 'open', False):
                    return scoped
            except Exception:
                pass

    with _db_lock:
        ahora = time.time()

        # 3. Circuito Abierto: Fast-fail no bloqueante si falló recientemente
        if _circuit_state == STATE_OPEN:
            if (ahora - _last_db_attempt) < _DB_RETRY_INTERVAL:
                DB_AVAILABLE = False
                return None
            # El intervalo expiró -> pasar a HALF_OPEN para probar la conexión
            _circuit_state = STATE_HALF_OPEN

        try:
            conn = _create_raw_connection()
            DB_AVAILABLE = True
            _circuit_state = STATE_CLOSED
            _db_fail_count = 0
            _last_db_attempt = ahora

            if has_request_context():
                scoped = _RequestScopedConnection(conn)
                g._db_conn = scoped
                return scoped
            return conn
        except Exception as e:
            _db_fail_count += 1
            _last_db_attempt = ahora
            if _db_fail_count >= _FAIL_THRESHOLD:
                _circuit_state = STATE_OPEN
            DB_AVAILABLE = False
            try:
                if current_app:
                    current_app.logger.warning(
                        "[DB] No disponible (Circuit Breaker %s, reintentando en %ss): %s",
                        _circuit_state,
                        _DB_RETRY_INTERVAL,
                        e,
                    )
            except Exception:
                pass
            return None


def close_db_connection(e=None):
    """Cierra la conexión al finalizar el ciclo de vida del request."""
    if has_request_context():
        scoped = getattr(g, '_db_conn', None)
        if scoped is not None:
            scoped._actual_close()
            g._db_conn = None


def is_db_available():
    """Retorna el estado actual de la conexión a la base de datos."""
    if is_mock_mode():
        return False
    return DB_AVAILABLE and _circuit_state == STATE_CLOSED


def get_circuit_breaker_status():
    """Retorna métricas y estado actual del circuit breaker."""
    return {
        'state': _circuit_state,
        'db_available': DB_AVAILABLE,
        'fail_count': _db_fail_count,
        'last_attempt': _last_db_attempt,
        'retry_interval': _DB_RETRY_INTERVAL,
        'mock_mode': is_mock_mode()
    }


def reset_circuit_breaker():
    """Reinicia el estado del circuit breaker (útil para tests o mantenimiento)."""
    global DB_AVAILABLE, _circuit_state, _db_fail_count, _last_db_attempt
    with _db_lock:
        DB_AVAILABLE = False
        _circuit_state = STATE_CLOSED
        _db_fail_count = 0
        _last_db_attempt = 0.0