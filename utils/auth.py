"""
Decoradores de autenticación y autorización.
"""
from functools import wraps
from flask import redirect, url_for, session, abort, flash, current_app
import uuid


def login_required(f):
    """Decorador que verifica que el usuario esté autenticado."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """Decorador que valida que el usuario tenga uno de los roles requeridos."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "usuario_id" not in session:
                return redirect(url_for("auth.login"))
            if session.get("rol") not in roles:
                flash("No tienes permiso para acceder a esta página", "error")
                return abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator


def owner_required(param_name="id"):
    """
    Decorador que valida que el parámetro URL coincida con el ID del usuario en sesión.
    TODOS los usuarios deben tener su ID en la URL coincidencia con su sesión.
    
    Args:
        param_name: Nombre del parámetro URL que contiene el UUID (default: "id")
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Obtener el ID del parámetro URL
            url_id = kwargs.get(param_name)
            session_id = session.get("usuario_id")
            
            # Convertir a string para comparación (UUID objects de Flask routing)
            if isinstance(url_id, uuid.UUID):
                url_id = str(url_id)
            if isinstance(session_id, uuid.UUID):
                session_id = str(session_id)
            
            if url_id != session_id:
                current_app.logger.warning(
                    f"Ownership violation: session={session_id}, url={url_id}"
                )
                return abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator