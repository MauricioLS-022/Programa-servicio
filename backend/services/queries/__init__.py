"""
Paquete services.queries: Repositorio modular de consultas SQL segregado por dominio.
"""
from .helpers import (
    formatear_hora,
    formatear_horario_cdp,
    _asistencia_fila,
    _semana_label,
    formatear_fecha_corta,
    formatear_mes_nombre,
    _obtener_rango_periodo,
    _obtener_metadatos_periodo,
    _periodo_a_fecha,
    _currency_columns_checked,
    _ensure_currency_columns
)

from .usuarios_queries import (
    get_usuarios,
    insertar_usuario,
    toggle_estado_usuario,
    get_supervisores_disponibles
)

from .lideres_queries import (
    get_lideres,
    obtener_lideres_por_cdp,
    get_cdps_para_lideres,
    insertar_lider,
    obtener_lider_por_id,
    actualizar_lider,
    eliminar_pausar_lider,
    toggle_estado_lider,
    get_lideres_cdp_disponibles
)

from .reportes_queries import (
    get_reportes,
    insertar_reporte,
    obtener_reportes_por_cdp,
    actualizar_reporte_cdp,
    eliminar_reporte_cdp
)

from .estructura_queries import (
    obtener_cdp_por_usuario,
    get_redes_disponibles,
    get_todas_las_redes,
    insertar_red,
    obtener_red_por_id,
    get_redes_activas_select,
    actualizar_red,
    toggle_estado_red,
    eliminar_red,
    get_cdps_disponibles,
    asignar_supervisor_a_red,
    asignar_usuario_a_cdp,
    insertar_cdp,
    obtener_cdp_admin,
    actualizar_cdp_admin,
    eliminar_pausar_cdp,
    toggle_estado_cdp
)

from .metricas_queries import (
    get_metricas_generales,
    get_metricas_red,
    get_metricas_cdp,
    obtener_metricas_lider_cdp
)
