"""Obtención de reportes para el módulo administrativo y de supervisión."""
from flask import current_app

from database import get_db_connection
from db_queries import get_reportes
from mock_data import get_mock_reportes, get_redes_demo, get_casas_demo
from services.dashboard_service import mock_mode_enabled


def get_reportes_context(search='', red_id='', cdp_id='', fecha_desde='', fecha_hasta='', page=1, per_page=5, supervisor_red_id=None):
    """Retorna reportes reales o mock junto con filtros y paginación."""
    conn = get_db_connection()
    if conn:
        try:
            reportes, total, redes, casas = get_reportes(
                conn, search, red_id, cdp_id, fecha_desde, fecha_hasta, supervisor_red_id, page, per_page
            )
        except Exception as error:
            current_app.logger.error('Error obteniendo reportes: %s', error)
            reportes, total, redes, casas = [], 0, [], []
        finally:
            conn.close()
    elif mock_mode_enabled():
        reportes = get_mock_reportes()
        if supervisor_red_id is not None:
            reportes = [rep for rep in reportes if rep.get('red_id') == supervisor_red_id]
        if search:
            search_lower = search.lower()
            reportes = [rep for rep in reportes if search_lower in (
                f"{rep['lider_nombre']} {rep['cdp_nombre']} {rep['tema']} {rep['observaciones']}"
            ).lower()]
        if red_id:
            reportes = [rep for rep in reportes if str(rep.get('red_id', '')) == str(red_id)]
        if cdp_id:
            reportes = [rep for rep in reportes if str(rep.get('cdp_id', '')) == str(cdp_id)]
        if fecha_desde:
            reportes = [rep for rep in reportes if rep.get('fecha', '') >= fecha_desde]
        if fecha_hasta:
            reportes = [rep for rep in reportes if rep.get('fecha', '') <= fecha_hasta]

        total = len(reportes)
        redes = get_redes_demo()
        casas = get_casas_demo()
        start = (page - 1) * per_page
        reportes = reportes[start:start + per_page]
    else:
        reportes, total, redes, casas = [], 0, [], []

    if supervisor_red_id is not None:
        redes = [red for red in redes if str(red['id']) == str(supervisor_red_id)]
        casas = [casa for casa in casas if str(casa.get('red_id', '')) == str(supervisor_red_id)]

    pages = max((total + per_page - 1) // per_page, 1)
    return {
        'reportes': reportes,
        'total_reportes': total,
        'redes': redes,
        'casas': casas,
        'page': page,
        'pages': pages,
        'search': search,
        'red_id': red_id,
        'cdp_id': cdp_id,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    }

