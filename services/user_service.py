"""Obtención de usuarios para la administración."""
from flask import current_app

from database import get_db_connection
from db_queries import get_usuarios
from mock_data import get_mock_usuarios
from services.dashboard_service import mock_mode_enabled


def get_usuarios_context(search='', rol='', page=1, per_page=10):
    """Retorna usuarios reales o demo junto con la metadata de paginación."""
    conn = get_db_connection()
    if conn:
        try:
            usuarios, total, total_activos = get_usuarios(conn, search, rol, page, per_page)
        except Exception as error:
            current_app.logger.error('Error obteniendo usuarios: %s', error)
            usuarios, total, total_activos = [], 0, 0
        finally:
            conn.close()
    elif mock_mode_enabled():
        usuarios = get_mock_usuarios()
        if search:
            search_lower = search.lower()
            usuarios = [
                usuario for usuario in usuarios
                if search_lower in ' '.join([
                    usuario['nombre'], usuario['apellido'], usuario['username']
                ]).lower()
            ]
        if rol:
            usuarios = [usuario for usuario in usuarios if usuario['rol'] == rol]
        total = len(usuarios)
        total_activos = sum(usuario['is_active'] for usuario in usuarios)
        start = (page - 1) * per_page
        usuarios = usuarios[start:start + per_page]
    else:
        usuarios, total, total_activos = [], 0, 0

    pages = max((total + per_page - 1) // per_page, 1)
    return {
        'usuarios': usuarios,
        'total_usuarios': total,
        'total_activos': total_activos,
        'page': page,
        'pages': pages,
        'search': search,
        'rol': rol,
    }