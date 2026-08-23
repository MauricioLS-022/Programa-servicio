"""
Context processors para inyectar funciones helper en las plantillas Jinja2.
"""
from flask import session


def has_role(role_name):
    """Verifica si el usuario actual tiene el rol especificado."""
    return session.get("rol") == role_name


def has_any_role(*role_names):
    """Verifica si el usuario actual tiene alguno de los roles especificados."""
    user_role = session.get("rol")
    return user_role in role_names


def get_usuario_id():
    """Obtiene el ID del usuario actual para generación de URLs."""
    return session.get("usuario_id")


def get_usuario():
    """Obtiene el nombre de usuario actual."""
    return session.get("usuario")


# Diccionario de funciones para registrar como context processors
context_functions = {
    'has_role': has_role,
    'has_any_role': has_any_role,
    'get_usuario_id': get_usuario_id,
    'get_usuario': get_usuario,
}