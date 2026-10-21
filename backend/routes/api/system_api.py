"""
routes/api/system_api.py - Endpoints de comprobación de salud y estado de la API.
"""
from flask import jsonify
from .base import api_bp


@api_bp.route('/health', methods=['GET', 'HEAD'])
def api_health():
    """Endpoint de comprobación de salud del servicio API."""
    return jsonify({
        "status": "ok",
        "app": "vino-nuevo",
        "service": "api"
    }), 200
