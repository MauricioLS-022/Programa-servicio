"""
Context processors para inyectar funciones helper en las plantillas Jinja2.
"""
from flask import session, url_for


def has_role(role_name):
    """Verifica si el usuario actual tiene el rol especificado."""
    current_role = session.get("rol")
    if role_name in ("lider_cdp", "cdp") and current_role in ("lider_cdp", "cdp"):
        return True
    return current_role == role_name


def has_any_role(*role_names):
    """Verifica si el usuario actual tiene alguno de los roles especificados."""
    current_role = session.get("rol")
    for r in role_names:
        if has_role(r):
            return True
    return False


def get_usuario_id():
    """Obtiene el ID del usuario actual para generación de URLs."""
    return session.get("usuario_id")


def get_usuario():
    """Obtiene el nombre de usuario actual."""
    return session.get("usuario")


def get_home_url():
    """Retorna la URL del dashboard según el rol, o login si no hay sesión."""
    user_id = session.get("usuario_id")
    rol = session.get("rol")

    if not user_id or not rol:
        return url_for("auth.login")

    role_routes = {
        "admin": "admin.dashboard",
        "supervisor": "supervisor.dashboard",
        "lider_cdp": "lider_cdp.dashboard",
        "cdp": "lider_cdp.dashboard",
    }

    endpoint = role_routes.get(rol)
    if endpoint:
        return url_for(endpoint)

    return url_for("auth.login")


# Diccionario de funciones para registrar como context processors
context_functions = {
    'has_role': has_role,
    'has_any_role': has_any_role,
    'get_usuario_id': get_usuario_id,
    'get_usuario': get_usuario,
    'get_home_url': get_home_url,
}