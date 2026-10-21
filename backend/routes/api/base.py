"""
routes/api/base.py - Blueprint base y serializadores para la API REST.
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')


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
