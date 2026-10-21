"""
db_queries.py - Capa Façade de compatibilidad hacia atrás.
Re-exporta todas las funciones de consulta desde el paquete modular services.queries.
"""
from services.queries import *
from services.queries.helpers import (
    _ensure_currency_columns,
    _periodo_a_fecha,
    _asistencia_fila,
    _semana_label,
    _obtener_rango_periodo,
    _obtener_metadatos_periodo,
    _currency_columns_checked
)
