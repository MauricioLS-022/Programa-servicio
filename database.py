"""
Módulo de conexión a MySQL con Circuit Breaker y Reutilización por Request Context.
Maneja reintentos automáticos cuando la base de datos no está disponible
y mantiene una única conexión por petición para minimizar la latencia de red.
"""
import pymysql
import time
import threading
from flask import current_app, g, has_request_context


# Estado global del circuit breaker
DB_AVAILABLE = False
_last_db_attempt = 0.0
_db_fail_count = 0
_DB_RETRY_INTERVAL = 15  # segundos entre reintentos si la BD falla
_DB_TIMEOUT = 5.0  # timeout de conexión en segundos
_db_lock = threading.Lock()


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
    """
    global DB_AVAILABLE, _last_db_attempt, _db_fail_count

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

        # Si falló recientemente, NO intentar conectar (evita lag de reintentos continuos)
        if _db_fail_count > 0 and (ahora - _last_db_attempt) < _DB_RETRY_INTERVAL:
            DB_AVAILABLE = False
            return None

        try:
            conn = _create_raw_connection()
            DB_AVAILABLE = True
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
            DB_AVAILABLE = False
            try:
                if current_app:
                    current_app.logger.warning(
                        "[DB] No disponible (reintentando en %ss): %s",
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
    return DB_AVAILABLE