"""
Servicio de Reportes Ministeriales - Lectura paginada, registro, edición y eliminación.
"""
import logging
from flask import current_app
from database import get_db_connection
import db_queries
from mock_data import get_mock_reportes, get_redes_demo, get_casas_demo
from repositories import unit_of_work
from services.dashboard_service import mock_mode_enabled
from services.queries.helpers import formatear_fecha_corta
from utils.cache import invalidate_dashboard_cache
from utils.validators import validate_report_form

logger = logging.getLogger(__name__)


class ProcessReporteResult(tuple):
    """Tupla (success, message) que evalúa a booleano según success."""
    def __bool__(self):
        return bool(self[0])


def _parse_cesta_amor(val):
    if isinstance(val, bool):
        return 1 if val else 0
    if isinstance(val, (int, float)):
        return 1 if val > 0 else 0
    val_str = str(val).strip().lower()
    return 1 if val_str in ('1', 'true', 'si', 'sí', 'on') else 0


def get_reportes_context(
    search='',
    red_id='',
    cdp_id='',
    fecha_desde='',
    fecha_hasta='',
    page=1,
    per_page=5,
    supervisor_red_id=None,
):
    """Retorna reportes reales o mock junto con filtros y paginación."""
    conn = get_db_connection()
    if conn:
        try:
            reportes, total, redes, casas = db_queries.get_reportes(
                conn, search, red_id, cdp_id, fecha_desde, fecha_hasta, supervisor_red_id, page, per_page
            )
        except Exception as error:
            current_app.logger.error('Error obteniendo reportes: %s', error)
            reportes, total, redes, casas = [], 0, [], []
        finally:
            conn.close()
    elif mock_mode_enabled():
        reportes = get_mock_reportes()
        if supervisor_red_id is not None:
            reportes = [rep for rep in reportes if rep.get('red_id') == supervisor_red_id]
        if search:
            search_lower = search.lower()
            reportes = [
                rep for rep in reportes
                if search_lower in (
                    f"{rep['lider_nombre']} {rep['cdp_nombre']} {rep['tema']} {rep['observaciones']}"
                ).lower()
            ]
        if red_id:
            reportes = [rep for rep in reportes if str(rep.get('red_id', '')) == str(red_id)]
        if cdp_id:
            reportes = [rep for rep in reportes if str(rep.get('cdp_id', '')) == str(cdp_id)]
        if fecha_desde:
            reportes = [rep for rep in reportes if rep.get('fecha', '') >= fecha_desde]
        if fecha_hasta:
            reportes = [rep for rep in reportes if rep.get('fecha', '') <= fecha_hasta]

        total = len(reportes)
        redes = get_redes_demo()
        casas = get_casas_demo()
        start = (page - 1) * per_page
        reportes = reportes[start:start + per_page]
    else:
        reportes, total, redes, casas = [], 0, [], []

    if supervisor_red_id is not None:
        redes = [red for red in redes if str(red['id']) == str(supervisor_red_id)]
        casas = [casa for casa in casas if str(casa.get('red_id', '')) == str(supervisor_red_id)]

    pages = max((total + per_page - 1) // per_page, 1)
    return {
        'reportes': reportes,
        'total_reportes': total,
        'redes': redes,
        'casas': casas,
        'page': page,
        'pages': pages,
        'search': search,
        'red_id': red_id,
        'cdp_id': cdp_id,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    }


def process_reporte(cdp_id, form_data, *, _conn_provider=None, _db_queries=None, _invalidate_cache=None):
    """
    Valida defensivamente y procesa el guardado de un reporte de Casa de Paz.
    """
    valido, error_msg, datos_reporte = validate_report_form(form_data, cdp_id)
    if not valido:
        return ProcessReporteResult((False, error_msg))

    conn_fn = _conn_provider or get_db_connection
    queries = _db_queries or db_queries
    inv_cache = _invalidate_cache or invalidate_dashboard_cache

    try:
        with unit_of_work(conn_provider=conn_fn, transactional=True) as uow:
            if uow is None:
                if mock_mode_enabled():
                    return ProcessReporteResult((True, "Reporte guardado exitosamente."))
                logger.error("No se pudo establecer conexión a la base de datos al guardar reporte.")
                return ProcessReporteResult((False, "No se pudo conectar a la base de datos."))

            with uow.cursor() as cursor:
                cursor.execute(
                    "SELECT id FROM reporte WHERE cdp_id = %s AND fecha = %s LIMIT 1",
                    (datos_reporte['cdp_id'], datos_reporte['fecha']),
                )
                reporte_existente = cursor.fetchone()
                if reporte_existente:
                    uow.rollback()
                    fecha_str = str(datos_reporte['fecha'])
                    fecha_fmt = formatear_fecha_corta(datos_reporte['fecha']) or fecha_str
                    return ProcessReporteResult((
                        False,
                        f"Ya existe un reporte registrado para esta Casa de Paz en la fecha {fecha_fmt}. Puedes consultarlo o editarlo en el historial.",
                    ))

                queries.insertar_reporte(cursor, datos_reporte)

        try:
            inv_cache()
        except Exception as cache_err:
            logger.warning("No se pudo invalidar la caché: %s", cache_err)

        return ProcessReporteResult((True, "Reporte guardado exitosamente."))
    except Exception as e:
        logger.error("Error al guardar reporte: %s", e)
        return ProcessReporteResult((False, "Error al guardar el reporte en la base de datos."))


def actualizar_reporte(reporte_id, cdp_id, form_data, *, _conn_provider=None, _db_queries=None, _invalidate_cache=None):
    """Valida y actualiza un reporte existente perteneciente a la CDP."""
    if not reporte_id:
        return False, "Identificador de reporte no válido."

    try:
        cdp_id = int(cdp_id) if cdp_id else 0
    except (ValueError, TypeError):
        cdp_id = 0

    if not cdp_id:
        return False, "Identificador de Casa de Paz no válido."

    conn_fn = _conn_provider or get_db_connection
    queries = _db_queries or db_queries
    inv_cache = _invalidate_cache or invalidate_dashboard_cache

    conn = conn_fn()
    if not conn:
        return False, "No se pudo conectar a la base de datos."

    valido, error_msg, datos_reporte = validate_report_form(form_data, cdp_id)
    if not valido:
        conn.close()
        return False, error_msg

    try:
        with conn.cursor() as cursor:
            exito = queries.actualizar_reporte_cdp(cursor, reporte_id, cdp_id, datos_reporte)
        conn.commit()

        if exito:
            try:
                inv_cache()
            except Exception as cache_err:
                logger.warning("No se pudo invalidar la caché: %s", cache_err)
            return True, "Reporte actualizado exitosamente."
        return False, "No se encontró el reporte o no pertenece a tu Casa de Paz."
    except Exception as e:
        conn.rollback()
        logger.error("Error al actualizar reporte %s: %s", reporte_id, e)
        return False, "Error interno al guardar los cambios del reporte."
    finally:
        conn.close()


def eliminar_reporte(reporte_id, cdp_id, *, _conn_provider=None, _db_queries=None, _invalidate_cache=None):
    """Elimina de forma segura un reporte perteneciente a la CDP."""
    conn_fn = _conn_provider or get_db_connection
    queries = _db_queries or db_queries
    inv_cache = _invalidate_cache or invalidate_dashboard_cache

    try:
        with unit_of_work(conn_provider=conn_fn, transactional=True) as uow:
            if uow is None:
                return False, "No se pudo conectar a la base de datos."
            with uow.cursor() as cursor:
                exito = queries.eliminar_reporte_cdp(cursor, reporte_id, cdp_id)

        if exito:
            try:
                inv_cache()
            except Exception as cache_err:
                logger.warning("No se pudo invalidar la caché: %s", cache_err)
            return True, "Reporte eliminado exitosamente."
        return False, "No se encontró el reporte o no pertenece a tu Casa de Paz."
    except Exception as e:
        logger.error("Error al eliminar reporte %s: %s", reporte_id, e)
        return False, "Error interno al eliminar el reporte."
