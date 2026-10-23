"""
Paquete routes.api: inicializa el blueprint api_bp y registra todos los módulos de endpoints REST.
"""
from .base import api_bp, _serialize_item
from . import system_api
from . import auth_api
from . import reportes_api
from . import estructura_api
from . import dashboard_api
from . import usuarios_api

__all__ = [
    'api_bp',
    '_serialize_item',
    'system_api',
    'auth_api',
    'reportes_api',
    'estructura_api',
    'dashboard_api',
    'usuarios_api'
]
