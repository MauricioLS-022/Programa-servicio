"""
Servicio de Redes Ministeriales - CRUD, asignación de supervisores y propagación de estado.
"""
import logging
from database import get_db_connection
from db_queries import (
    get_supervisores_disponibles,
    insertar_red,
    obtener_red_por_id,
    actualizar_red,
    toggle_estado_red,
    eliminar_red,
)
from repositories import unit_of_work, get_estructura_repository
from services.dashboard_service import mock_mode_enabled
from utils.cache import invalidate_dashboard_cache
from utils.validators import validate_name_red

logger = logging.getLogger(__name__)


def listar_redes_servicio(*, supervisor_red_id=None, allow_mock_fallback=True):
    """Lista las redes ministeriales a través del repositorio de estructura."""
    repo = get_estructura_repository(allow_mock_fallback_without_flag=allow_mock_fallback)
    return repo.list_redes(supervisor_red_id=supervisor_red_id)


def get_supervisores_disponibles_servicio(*, _conn_provider=None):
    """Obtiene la lista de usuarios con rol supervisor que no tienen red asignada."""
    conn_fn = _conn_provider or get_db_connection
    try:
        with unit_of_work(conn_provider=conn_fn, transactional=False) as uow:
            if uow is None:
                if mock_mode_enabled():
                    from mock_data import get_mock_usuarios, get_redes_demo
                    usuarios = get_mock_usuarios()
                    redes = get_redes_demo()
                    asignados_ids = {str(r.get('supervisor_id')) for r in redes if r.get('supervisor_id')}
                    return [
                        {
                            'id': u['id'],
                            'nombre': f"{u.get('nombre', '')} {u.get('apellido', '')}".strip() or u.get('username'),
                            'username': u.get('username'),
                        }
                        for u in usuarios
                        if u.get('rol') == 'supervisor' and str(u['id']) not in asignados_ids
                    ]
                return []
            with uow.cursor() as cursor:
                return get_supervisores_disponibles(cursor)
    except Exception as e:
        logger.error("Error obteniendo supervisores disponibles: %s", e)
        return []


def crear_red_servicio(form_data: dict, *, _conn_provider=None, _invalidate_cache=None) -> tuple:
    """Valida y procesa la creación de una nueva red ministerial."""
    nombre_red_raw = str(form_data.get('nombre') or '').strip()
    supervisor_id = str(form_data.get('supervisor_id') or '').strip()

    is_valid, res_red = validate_name_red(nombre_red_raw)
    if not is_valid:
        return False, res_red

    conn_fn = _conn_provider or get_db_connection
    inv_cache = _invalidate_cache or invalidate_dashboard_cache

    try:
        with unit_of_work(conn_provider=conn_fn, transactional=True) as uow:
            if uow is None:
                return False, 'Error de conexión a la base de datos.'
            with uow.cursor() as cursor:
                cursor.execute("SELECT id FROM red WHERE nombre = %s", (res_red,))
                if cursor.fetchone():
                    uow.rollback()
                    return False, f"Ya existe una red con el nombre '{res_red}'."

                sup_final = None
                if supervisor_id:
                    cursor.execute(
                        "SELECT id FROM usuario WHERE id = %s AND tipo_usuario = 'supervisor'",
                        (supervisor_id,),
                    )
                    if not cursor.fetchone():
                        uow.rollback()
                        return False, "El supervisor seleccionado no es válido."

                    cursor.execute("SELECT id, nombre FROM red WHERE supervisor_id = %s", (supervisor_id,))
                    red_ocupada = cursor.fetchone()
                    if red_ocupada:
                        uow.rollback()
                        return False, f"Este supervisor ya está asignado a la red '{red_ocupada['nombre']}'"
                    sup_final = supervisor_id

                insertar_red(cursor, res_red, sup_final)

        try:
            inv_cache()
        except Exception as cache_err:
            logger.warning("No se pudo invalidar caché tras crear red: %s", cache_err)

        return True, "Red creada exitosamente."
    except Exception as e:
        logger.error("Error creando red: %s", e)
        return False, "Error interno al crear la red."


def obtener_red_servicio(red_id: int, *, _conn_provider=None):
    """Obtiene los datos de una red específica por su ID."""
    conn_fn = _conn_provider or get_db_connection
    try:
        with unit_of_work(conn_provider=conn_fn, transactional=False) as uow:
            if uow is None:
                return None
            with uow.cursor() as cursor:
                return obtener_red_por_id(cursor, red_id)
    except Exception as e:
        logger.error("Error al obtener red %s: %s", red_id, e)
        return None


def actualizar_red_servicio(red_id: int, form_data: dict, *, _conn_provider=None, _invalidate_cache=None) -> tuple[bool, str]:
    """Actualiza el nombre y supervisor de una red existente."""
    nombre_red_raw = str(form_data.get('nombre') or '').strip()
    supervisor_id = str(form_data.get('supervisor_id') or '').strip()

    is_valid, res_red = validate_name_red(nombre_red_raw)
    if not is_valid:
        return False, res_red

    conn_fn = _conn_provider or get_db_connection
    inv_cache = _invalidate_cache or invalidate_dashboard_cache

    try:
        with unit_of_work(conn_provider=conn_fn, transactional=True) as uow:
            if uow is None:
                return False, 'Error de conexión a la base de datos.'
            with uow.cursor() as cursor:
                cursor.execute("SELECT id FROM red WHERE id = %s", (red_id,))
                if not cursor.fetchone():
                    uow.rollback()
                    return False, "La red especificada no existe."

                cursor.execute("SELECT id FROM red WHERE nombre = %s AND id != %s", (res_red, red_id))
                if cursor.fetchone():
                    uow.rollback()
                    return False, f"Ya existe otra red con el nombre '{res_red}'."

                sup_final = None
                if supervisor_id:
                    cursor.execute(
                        "SELECT id FROM usuario WHERE id = %s AND tipo_usuario = 'supervisor'",
                        (supervisor_id,),
                    )
                    if not cursor.fetchone():
                        uow.rollback()
                        return False, "El supervisor seleccionado no es válido."

                    cursor.execute(
                        "SELECT id, nombre FROM red WHERE supervisor_id = %s AND id != %s",
                        (supervisor_id, red_id),
                    )
                    red_ocupada = cursor.fetchone()
                    if red_ocupada:
                        uow.rollback()
                        return False, f"Este supervisor ya está asignado a la red '{red_ocupada['nombre']}'"
                    sup_final = supervisor_id

                actualizar_red(cursor, red_id, res_red, sup_final)

        try:
            inv_cache()
        except Exception as cache_err:
            logger.warning("No se pudo invalidar caché tras actualizar red: %s", cache_err)

        return True, "Red actualizada exitosamente."
    except Exception as e:
        logger.error("Error actualizando red %s: %s", red_id, e)
        return False, "Error interno al actualizar la red."


def toggle_red_servicio(red_id: int, *, _conn_provider=None, _toggle_fn=None, _invalidate_cache=None) -> tuple[bool, str]:
    """Pone en pausa o reactiva una red."""
    conn_fn = _conn_provider or get_db_connection
    toggle_fn = _toggle_fn or toggle_estado_red
    inv_cache = _invalidate_cache or invalidate_dashboard_cache

    try:
        with unit_of_work(conn_provider=conn_fn, transactional=True) as uow:
            if uow is None:
                return False, 'Error de conexión a la base de datos.'
            with uow.cursor() as cursor:
                cursor.execute("SELECT nombre FROM red WHERE id = %s", (red_id,))
                red = cursor.fetchone()
                if not red:
                    uow.rollback()
                    return False, "La red especificada no existe."
                quedo_activa = toggle_fn(cursor, red_id)

        try:
            inv_cache()
        except Exception as cache_err:
            logger.warning("No se pudo invalidar caché tras toggle de red: %s", cache_err)

        estado = 'reactivada' if quedo_activa else 'puesta en pausa'
        return True, f"La red '{red['nombre']}' ha sido {estado} exitosamente."
    except Exception as e:
        logger.error("Error al cambiar el estado de la red %s: %s", red_id, e)
        return False, "Error interno al cambiar el estado de la red"


def eliminar_red_servicio(red_id: int, *, _conn_provider=None, _eliminar_fn=None, _invalidate_cache=None) -> tuple[bool, str]:
    """Elimina una red si no tiene Casas de Paz vinculadas."""
    conn_fn = _conn_provider or get_db_connection
    eliminar_fn = _eliminar_fn or eliminar_red
    inv_cache = _invalidate_cache or invalidate_dashboard_cache

    try:
        with unit_of_work(conn_provider=conn_fn, transactional=True) as uow:
            if uow is None:
                return False, 'Error de conexión a la base de datos.'
            with uow.cursor() as cursor:
                cursor.execute("SELECT nombre FROM red WHERE id = %s", (red_id,))
                red = cursor.fetchone()
                if not red:
                    uow.rollback()
                    return False, "La red especificada no existe."

                exito = eliminar_fn(cursor, red_id)
                if not exito:
                    uow.rollback()
                    return False, f"No se puede eliminar la red '{red['nombre']}' porque tiene Casas de Paz vinculadas.  Reasigna las casas primero o pon la red en pausa."

        try:
            inv_cache()
        except Exception as cache_err:
            logger.warning("No se pudo invalidar caché tras eliminar red: %s", cache_err)

        return True, f"La red '{red['nombre']}' ha sido eliminada exitosamente."
    except Exception as e:
        logger.error("Error al eliminar la red %s: %s", red_id, e)
        return False, "Error interno al eliminar la red"
