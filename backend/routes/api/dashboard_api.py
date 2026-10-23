"""
routes/api/dashboard_api.py - Endpoints REST protegidos para métricas temporales de dashboard.
"""
from flask import request, jsonify, session
from services.dashboard_service import get_metricas, mock_mode_enabled, get_supervisor_red_id
from utils.cache import get_cached_value, set_cached_value
from utils.auth import login_required, role_required
from .base import api_bp, _serialize_item


@api_bp.route('/dashboard/datos')
@login_required
@role_required("admin", "supervisor")
def api_dashboard_datos():
    """Endpoint AJAX protegido que retorna métricas en JSON para filtros dinámicos."""
    rol = session.get('rol')
    usuario_id = session.get('usuario_id')
    nivel = request.args.get('nivel', 'general')
    red_id_str = request.args.get('red_id', '')
    cdp_id_str = request.args.get('cdp_id', '')
    periodo_raw = request.args.get('periodo', 'semana').strip().lower() if request.args.get('periodo') else 'semana'
    periodo = periodo_raw if periodo_raw in ('semana', 'mes', 'anio') else 'semana'

    try:
        red_id = int(red_id_str) if red_id_str and red_id_str.isdigit() else None
    except (ValueError, TypeError):
        red_id = None

    try:
        cdp_id = int(cdp_id_str) if cdp_id_str and cdp_id_str.isdigit() else None
    except (ValueError, TypeError):
        cdp_id = None

    mes_str = request.args.get('mes', '').strip()
    anio_str = request.args.get('anio', '').strip()
    mes = int(mes_str) if mes_str and mes_str.isdigit() and 1 <= int(mes_str) <= 12 else None
    anio = int(anio_str) if anio_str and anio_str.isdigit() else None

    # Aislamiento defensivo de rol supervisor:
    # No puede consultar nivel 'general' ni redes ajenas
    if rol == 'supervisor':
        sup_red = get_supervisor_red_id(usuario_id)
        if not sup_red:
            return jsonify({})
        if nivel not in ('red', 'cdp'):
            nivel = 'red'
        red_id = sup_red

        if nivel == 'cdp' and cdp_id:
            from services.dashboard_service import get_selectores
            _, casas = get_selectores()
            casas_de_red = [c['id'] for c in casas if c.get('red_id') == sup_red]
            if cdp_id not in casas_de_red:
                return jsonify({}), 403

    cache_key = f'metricas_{nivel}_{red_id}_{cdp_id}_{periodo}_{mes}_{anio}_{mock_mode_enabled()}'

    # Verificar caché primero
    cached = get_cached_value(cache_key)
    if cached:
        return jsonify(_serialize_item(cached))

    # Obtener métricas
    kwargs = {}
    if 'periodo' in request.args:
        kwargs['periodo'] = periodo
    if mes is not None:
        kwargs['mes'] = mes
    if anio is not None:
        kwargs['anio'] = anio

    if kwargs:
        metricas = get_metricas(nivel, red_id, cdp_id, **kwargs)
    else:
        metricas = get_metricas(nivel, red_id, cdp_id)
    
    if metricas and not (metricas.get('total_casas', 0) == 0 and metricas.get('total_asistencia', 0) == 0 and metricas.get('casas_activas', 0) == 0):
        set_cached_value(cache_key, metricas)

    return jsonify(_serialize_item(metricas))
