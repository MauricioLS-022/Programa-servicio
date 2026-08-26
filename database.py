"""
Módulo de conexión a MySQL con Circuit Breaker.
Maneja reintentos automáticos cuando la base de datos no está disponible.
"""
import pymysql
import time
import threading
from flask import current_app


# Estado global del circuit breaker
DB_AVAILABLE = False
_last_db_attempt = 0.0
_db_fail_count = 0
_DB_RETRY_INTERVAL = 15  # segundos entre reintentos si la BD falla
_DB_TIMEOUT = 0.5  # timeout de conexión en segundos (falla instantánea)
_db_lock = threading.Lock()


def get_db_connection():
    """
    Conexión a MySQL con circuit breaker. 
    Si falla, reintenta cada _DB_RETRY_INTERVAL segundos.
    """
    global DB_AVAILABLE, _last_db_attempt, _db_fail_count

    with _db_lock:
        ahora = time.time()

        # Si falló recientemente, NO intentar conectar (evita lag de 2-15s)
        if _db_fail_count > 0 and (ahora - _last_db_attempt) < _DB_RETRY_INTERVAL:
            DB_AVAILABLE = False
            return None

        try:
            from flask import current_app
            conn = pymysql.connect(
                host=current_app.config['DB_HOST'],
                port=current_app.config['DB_PORT'],
                user=current_app.config['DB_USER'],
                password=current_app.config['DB_PASSWORD'],
                database=current_app.config['DB_NAME'],
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=_DB_TIMEOUT,
                read_timeout=_DB_TIMEOUT,
            )
            DB_AVAILABLE = True
            _db_fail_count = 0
            _last_db_attempt = ahora
            return conn
        except Exception as e:
            _db_fail_count += 1
            _last_db_attempt = ahora
            DB_AVAILABLE = False
            current_app.logger.warning(
                "[DB] No disponible (reintentando en %ss): %s",
                _DB_RETRY_INTERVAL,
                e,
            )
            return None


def is_db_available():
    """Retorna el estado actual de la conexión a la base de datos."""
    return DB_AVAILABLE