"""
Decoradores de autenticación y autorización.
"""
from functools import wraps
from flask import redirect, url_for, session, abort, flash, current_app, jsonify, request
import uuid


def _client_wants_json():
    """Indica si el cliente declaró explícitamente preferencia por JSON."""
    best = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    return (
        best == 'application/json'
        and request.accept_mimetypes[best] > request.accept_mimetypes['text/html']
    )


def api_auth_required(f=None, *, allow_legacy_redirect=False):
    """
    Decorador de autenticación para endpoints REST (/api/*).
    Retorna 401 JSON por defecto. Si allow_legacy_redirect=True y el cliente no solicita
    explícitamente JSON, mantiene la redirección 302 hacia login por compatibilidad SSR.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if "usuario_id" not in session or not session.get("usuario_id"):
                if allow_legacy_redirect and not _client_wants_json():
                    return redirect(url_for("auth.login"))
                return jsonify({"error": "No autenticado"}), 401
            return func(*args, **kwargs)
        return wrapper

    if f is not None:
        return decorator(f)
    return decorator


def api_role_required(*roles, allow_legacy_redirect=False, forbidden_message=None):
    """
    Decorador de autorización por rol para endpoints REST (/api/*).
    Verifica autenticación (401 JSON) y pertenencia a los roles permitidos (403 JSON).
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if "usuario_id" not in session or not session.get("usuario_id"):
                if allow_legacy_redirect and not _client_wants_json():
                    return redirect(url_for("auth.login"))
                return jsonify({"error": "No autenticado"}), 401
            if session.get("rol") not in roles:
                if forbidden_message:
                    msg = forbidden_message
                elif roles == ('admin',):
                    msg = "Acceso restringido a administradores"
                else:
                    msg = "No autorizado"
                return jsonify({"error": msg}), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator


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


def is_safe_url(target):
    """
    Valida que una URL de destino sea segura y pertenezca al mismo host de la aplicación,
    previniendo vulnerabilidades de redirección abierta (Open Redirect).
    """
    from urllib.parse import urlparse, urljoin
    from flask import request
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def safe_redirect(fallback_endpoint, **fallback_kwargs):
    """
    Redirige al referrer si es seguro (pertenece al mismo host),
    o redirige al endpoint institucional de fallback.
    """
    from flask import request
    referrer = request.referrer
    if referrer and is_safe_url(referrer):
        return redirect(referrer)
    return redirect(url_for(fallback_endpoint, **fallback_kwargs))