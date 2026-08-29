"""Obtención de líderes para el directorio administrativo."""
from flask import current_app

from database import get_db_connection
from db_queries import get_lideres
from mock_data import get_mock_lideres, get_redes_demo, get_casas_demo
from services.dashboard_service import mock_mode_enabled


def get_lideres_context(search='', rol='', red_id='', cdp_id='', page=1, per_page=5, supervisor_red_id=None):
    """Retorna líderes reales o mock junto con filtros y paginación."""
    conn = get_db_connection()
    if conn:
        try:
            lideres, total, redes, casas = get_lideres(
                conn, search, rol, red_id, cdp_id, supervisor_red_id, page, per_page
            )
        except Exception as error:
            current_app.logger.error('Error obteniendo líderes: %s', error)
            lideres, total, redes, casas = [], 0, [], []
        finally:
            conn.close()
    elif mock_mode_enabled():
        lideres = get_mock_lideres()
        if supervisor_red_id is not None:
            lideres = [leader for leader in lideres if leader['red_id'] == supervisor_red_id]
        if search:
            search_lower = search.lower()
            lideres = [leader for leader in lideres if search_lower in (
                f"{leader['nombre']} {leader['apellido']} {leader['telefono']}"
            ).lower()]
        if rol:
            lideres = [leader for leader in lideres if leader['rol'] == rol]
        if red_id:
            lideres = [leader for leader in lideres if str(leader['red_id']) == str(red_id)]
        if cdp_id:
            lideres = [leader for leader in lideres if str(leader['cdp_id']) == str(cdp_id)]
        total = len(lideres)
        redes = get_redes_demo()
        casas = get_casas_demo()
        start = (page - 1) * per_page
        lideres = lideres[start:start + per_page]
    else:
        lideres, total, redes, casas = [], 0, [], []

    if supervisor_red_id is not None:
        redes = [red for red in redes if str(red['id']) == str(supervisor_red_id)]
        casas = [casa for casa in casas if str(casa['red_id']) == str(supervisor_red_id)]

    pages = max((total + per_page - 1) // per_page, 1)
    return {
        'lideres': lideres,
        'total_lideres': total,
        'redes_lideres': redes,
        'casas_lideres': casas,
        'page': page,
        'pages': pages,
        'search': search,
        'rol': rol,
        'red_id': red_id,
        'cdp_id': cdp_id,
    }