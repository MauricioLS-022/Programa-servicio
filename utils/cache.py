"""
Sistema de caché en memoria con TTL para métricas del dashboard.
"""
import time
import threading

_dashboard_cache = {}
_cache_lock = threading.Lock()
_CACHE_TTL = 300  # 5 minutos


def _get_cache(key):
    """Retorna valor si existe y no expiró, o None."""
    try:
        from flask import current_app
        if current_app and (current_app.config.get('DEBUG') or current_app.config.get('FLASK_ENV') == 'development'):
            return None
    except Exception:
        pass

    with _cache_lock:
        entry = _dashboard_cache.get(key)
        if entry and (time.time() - entry['ts']) < _CACHE_TTL:
            return entry['data']
    return None


def _set_cache(key, data):
    """Almacena valor en caché con timestamp."""
    with _cache_lock:
        _dashboard_cache[key] = {'data': data, 'ts': time.time()}


def invalidate_dashboard_cache():
    """Vacía toda la caché del dashboard (llamar al enviar un reporte)."""
    with _cache_lock:
        _dashboard_cache.clear()
    print("[CACHE] Dashboard cache invalidado")


def get_cached_value(key):
    """Obtiene un valor de la caché si existe y no expiró."""
    return _get_cache(key)


def set_cached_value(key, data):
    """Almacena un valor en caché con TTL."""
    _set_cache(key, data)