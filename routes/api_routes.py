"""
Rutas de API: /api/dashboard/datos
"""
from flask import Blueprint, request, jsonify
from services.dashboard_service import get_metricas
from database import get_db_connection
from utils.cache import get_cached_value, set_cached_value

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/dashboard/datos')
def api_dashboard_datos():
    """Endpoint AJAX que retorna métricas en JSON para filtros dinámicos."""
    nivel = request.args.get('nivel', 'general')
    red_id_str = request.args.get('red_id', '')
    cdp_id_str = request.args.get('cdp_id', '')

    try:
        red_id = int(red_id_str) if red_id_str and red_id_str.isdigit() else None
    except (ValueError, TypeError):
        red_id = None

    try:
        cdp_id = int(cdp_id_str) if cdp_id_str and cdp_id_str.isdigit() else None
    except (ValueError, TypeError):
        cdp_id = None

    db_connected = get_db_connection() is not None
    cache_key = f'metricas_{nivel}_{red_id}_{cdp_id}'

    # Verificar caché primero
    cached = get_cached_value(cache_key)
    if cached:
        return jsonify(cached)

    # Obtener métricas
    metricas = get_metricas(nivel, red_id, cdp_id)
    
    if metricas:
        set_cached_value(cache_key, metricas)

    return jsonify(metricas)