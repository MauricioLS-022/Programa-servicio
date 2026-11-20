"""
routes/api/base.py - Blueprint base y serializadores para la API REST.
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from flask import Blueprint, current_app, jsonify, request
from flask_wtf.csrf import validate_csrf
from wtforms import ValidationError

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.before_request
def _enforce_api_csrf():
    """Valida cabecera X-CSRFToken en todas las mutaciones REST (/api/*)."""
    if request.method not in ('POST', 'PUT', 'PATCH', 'DELETE'):
        return None

    force_in_testing = bool(current_app.config.get('FORCE_CSRF_IN_TESTING', False))
    if current_app.config.get('TESTING', False) and not force_in_testing:
        return None
    if not force_in_testing and not current_app.config.get('WTF_CSRF_ENABLED', True):
        return None

    token = (
        request.headers.get('X-CSRFToken')
        or request.headers.get('X-CSRF-Token')
        or ''
    ).strip()
    if not token:
        return jsonify({
            "success": False,
            "error": "Token CSRF requerido en cabecera X-CSRFToken.",
            "code": "csrf_error",
        }), 400

    try:
        validate_csrf(token)
    except ValidationError:
        return jsonify({
            "success": False,
            "error": "Token CSRF inválido o expirado.",
            "code": "csrf_error",
        }), 400
    return None


def _serialize_item(item):
    """Convierte tipos no serializables nativos (date, datetime, Decimal, bytes) a formatos JSON estándar."""
    if isinstance(item, (date, datetime)):
        return item.isoformat()
    if isinstance(item, Decimal):
        return float(item)
    if isinstance(item, timedelta):
        return str(item)
    if isinstance(item, bytes):
        return item.decode('utf-8', errors='ignore')
    if isinstance(item, dict):
        return {k: _serialize_item(v) for k, v in item.items()}
    if isinstance(item, (list, tuple)):
        return [_serialize_item(v) for v in item]
    return item
