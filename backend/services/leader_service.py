"""Obtención de líderes para el directorio administrativo."""
from flask import current_app
from utils.cache import invalidate_dashboard_cache
from database import get_db_connection
from db_queries import (
    get_lideres,
    insertar_usuario,
    asignar_supervisor_a_red,
    asignar_usuario_a_cdp,
    get_redes_disponibles,
    get_cdps_disponibles,
    get_supervisores_disponibles,
    actualizar_red,
    eliminar_red,
    insertar_red,
    toggle_estado_red,
    obtener_red_por_id,
    insertar_lider,
    obtener_lider_por_id,
    actualizar_lider,
    eliminar_pausar_lider,
    get_cdps_para_lideres,
    toggle_estado_lider
)
from mock_data import get_mock_lideres, get_redes_demo, get_casas_demo
from services.dashboard_service import mock_mode_enabled
from werkzeug.security import generate_password_hash

from utils.validators import validate_name_red, validate_phone, validate_person_name
from services import red_service as _red_service
from services import user_service as _user_service


# =====================================================================
# SERVICIOS PARA GESTIÓN DE LÍDERES (EQUIPO MINISTERIAL DE CASAS DE PAZ)
# =====================================================================

def get_lideres_context(search='', rol='', red_id='', cdp_id='', page=1, per_page=5, supervisor_red_id=None):
    """Retorna líderes reales o mock junto con filtros y paginación."""
    conn = get_db_connection()
    if conn:
        try:
            lideres, total, redes, casas = get_lideres(
                conn, search, rol, red_id, cdp_id, supervisor_red_id, page, per_page
            )
        except Exception as error:
            current_app.logger.error('Error obteniendo líderes: %s', error)
            lideres, total, redes, casas = [], 0, [], []
        finally:
            conn.close()
    elif mock_mode_enabled():
        lideres = get_mock_lideres()
        if supervisor_red_id is not None:
            lideres = [leader for leader in lideres if leader['red_id'] == supervisor_red_id]
        if search:
            search_lower = search.lower()
            lideres = [leader for leader in lideres if search_lower in (
                f"{leader['nombre']} {leader['apellido']} {leader['telefono']}"
            ).lower()]
        if rol:
            lideres = [leader for leader in lideres if leader['rol'] == rol]
        if red_id:
            lideres = [leader for leader in lideres if str(leader['red_id']) == str(red_id)]
        if cdp_id:
            lideres = [leader for leader in lideres if str(leader['cdp_id']) == str(cdp_id)]
        total = len(lideres)
        redes = get_redes_demo()
        casas = get_casas_demo()
        start = (page - 1) * per_page
        lideres = lideres[start:start + per_page]
    else:
        lideres, total, redes, casas = [], 0, [], []

    if supervisor_red_id is not None:
        redes = [red for red in redes if str(red['id']) == str(supervisor_red_id)]
        casas = [casa for casa in casas if str(casa['red_id']) == str(supervisor_red_id)]

    pages = max((total + per_page - 1) // per_page, 1)
    return {
        'lideres': lideres,
        'total_lideres': total,
        'redes_lideres': redes,
        'casas_lideres': casas,
        'page': page,
        'pages': pages,
        'search': search,
        'rol': rol,
        'red_id': red_id,
        'cdp_id': cdp_id,
    }

def _as_str(val, default: str = '') -> str:
    if val is None:
        return default
    return str(val).strip()


def crear_lider_servicio(form_data: dict) -> tuple[bool, str]:
    """
    Valida y registra un nuevo líder o sublíder asignado a una Casa de Paz activa.
    Retorna: (exito: bool, mensaje: str)
    """

    nombre_raw = _as_str(form_data.get('nombre'))
    apellido_raw = _as_str(form_data.get('apellido'))
    telefono_raw = _as_str(form_data.get('telefono'))
    rol = _as_str(form_data.get('rol'))
    cdp_id_raw = _as_str(form_data.get('cdp_id'))

    # 1. Validaciones defensivas de nombres
    ok_nom, res_nom = validate_person_name(nombre_raw, 'Nombre')
    if not ok_nom:
        return False, res_nom

    ok_ape, res_ape = validate_person_name(apellido_raw, 'Apellido')
    if not ok_ape:
        return False, res_ape

    # 2. Validación de teléfono
    if not telefono_raw:
        return False, "El teléfono de contacto es obligatorio."
    
    ok_tel, clean_tel, error_tel = validate_phone(telefono_raw)
    if not ok_tel:
        return False, error_tel

    # 3. Validación de rol
    if not rol in ('Lider', 'Sublider'):
        return False, "El rol debe ser 'Lider' o 'Sublider'."

    # 4. Validación de Casa de Paz seleccionada
    try:
        cdp_id = int(cdp_id_raw)
    except (ValueError, TypeError):
        return False, "Debe seleccionar una Casa de Paz válida."

    conn = get_db_connection()
    if not conn:
        from services.dashboard_service import mock_mode_enabled
        if mock_mode_enabled():
            return True, f"Líder '{res_nom} {res_ape}' registrado exitosamente (modo demo)."
        return False, "Error de conexión a la base de datos."

    try:
        with conn.cursor() as cursor:
            # Candado: Comprobar que la Casa de Paz existe y está activa
            cursor.execute("SELECT id, codigo, is_active FROM cdp WHERE id = %s", (cdp_id,))
            cdp = cursor.fetchone()
            if not cdp:
                return False, "La Casa de Paz seleccionada no existe."

            if not bool(cdp.get('is_active', 1)):
                return False, f"La Casa de Paz '{cdp.get('codigo')}' se encuentra inactiva/pausada. No se pueden asignar líderes a casas inactivas."

            # Candado anti-duplicados: Comprobar que no exista ya un líder con el mismo nombre y apellido en esa casa
            cursor.execute("SELECT id FROM lider WHERE nombre = %s AND apellido = %s AND cdp_id = %s", (res_nom, res_ape, cdp_id))
            if cursor.fetchone():
                return False, f"Ya existe un líder registrado como '{res_nom} {res_ape}' en la Casa de Paz '{cdp.get('codigo')}'."

            # Insertar el nuevo líder
            insertar_lider(cursor, res_nom, res_ape, clean_tel, rol, cdp_id)

        conn.commit()
        try:
            invalidate_dashboard_cache()
        except Exception:
            pass
        return True, f"Líder '{res_nom} {res_ape}' registrado exitosamente."

    except Exception as e:
        conn.rollback()
        current_app.logger.error("Error al registrar líder: %s", e)
        return False, "Error interno al registrar el líder."
    finally:
        conn.close()

def obtener_lider_servicio(lider_id: int):
    """
    Obtiene los datos completos de un líder por su ID.
    Retorna el diccionario del líder o None si no existe.
    """
    try:
        lider_id = int(lider_id)
    except (ValueError, TypeError):
        return None

    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            return obtener_lider_por_id(cursor, lider_id)
    except Exception as e:
        current_app.logger.error("Error al obtener líder %s: %s", lider_id, e)
        return None
    finally:
        conn.close()


def actualizar_lider_servicio(lider_id: int, form_data: dict, is_active: int = None) -> tuple[bool, str]:
    """
    Valida y actualiza los datos personales, rol o Casa de Paz de un líder.
    Valida jerarquía: si se activa o asigna, la Casa de Paz debe estar activa.
    Retorna: (exito: bool, mensaje: str)
    """
    try:
        lider_id = int(lider_id)
    except (ValueError, TypeError):
        return False, "Identificador de líder no válido."

    nombre_raw = _as_str(form_data.get('nombre'))
    apellido_raw = _as_str(form_data.get('apellido'))
    telefono_raw = _as_str(form_data.get('telefono'))
    rol = _as_str(form_data.get('rol'))
    cdp_id_raw = _as_str(form_data.get('cdp_id'))

    is_active_raw = is_active if is_active is not None else form_data.get('is_active')
    is_active_val = None
    if is_active_raw is not None and str(is_active_raw).strip() != '':
        is_active_val = 1 if str(is_active_raw).strip().lower() in ('1', 'true', 'on', 'si', 'sí') or is_active_raw is True or is_active_raw == 1 else 0

    # 1. Validaciones defensivas de nombres
    ok_nom, res_nom = validate_person_name(nombre_raw, 'Nombre')
    if not ok_nom:
        return False, res_nom

    ok_ape, res_ape = validate_person_name(apellido_raw, 'Apellido')
    if not ok_ape:
        return False, res_ape

    # 2. Validación de teléfono
    if not telefono_raw:
        return False, "El teléfono de contacto es obligatorio."
    
    ok_tel, clean_tel, error_tel = validate_phone(telefono_raw)
    if not ok_tel:
        return False, error_tel

    # 3. Validación de rol
    if rol not in ('Lider', 'Sublider'):
        return False, "El rol debe ser 'Lider' o 'Sublider'."

    # 4. Validación de Casa de Paz seleccionada
    try:
        cdp_id = int(cdp_id_raw)
    except (ValueError, TypeError):
        return False, "Debe seleccionar una Casa de Paz válida."

    conn = get_db_connection()
    if not conn:
        return False, "Error de conexión a la base de datos."

    try:
        with conn.cursor() as cursor:
            # 1. Verificar existencia del líder
            cursor.execute("SELECT id, nombre, apellido, is_active FROM lider WHERE id = %s", (lider_id,))
            lider = cursor.fetchone()
            if not lider:
                return False, "El líder especificado no existe."

            # 2. Candado: Verificar que la Casa de Paz destino exista y esté activa
            cursor.execute("SELECT id, codigo, is_active FROM cdp WHERE id = %s", (cdp_id,))
            cdp = cursor.fetchone()
            if not cdp:
                return False, "La Casa de Paz seleccionada no existe."

            # Si el líder quedará activo, validar que la Casa de Paz esté activa
            lider_sera_activo = (is_active_val == 1) if is_active_val is not None else bool(lider.get('is_active', 1))
            if lider_sera_activo and not bool(cdp.get('is_active', 1)):
                return False, f"No se puede reactivar al líder porque su Casa de Paz asignada ('{cdp.get('codigo')}') se encuentra en pausa o inactiva. Debe reactivar la Casa primero o reasignar al líder a una Casa activa."

            # 3. Actualizar datos
            if is_active_val is not None:
                actualizar_lider(cursor, lider_id, res_nom, res_ape, clean_tel, rol, cdp_id, is_active=is_active_val)
            else:
                actualizar_lider(cursor, lider_id, res_nom, res_ape, clean_tel, rol, cdp_id)

        conn.commit()
        try:
            invalidate_dashboard_cache()
        except Exception:
            pass
        return True, "Líder actualizado exitosamente."

    except Exception as e:
        conn.rollback()
        current_app.logger.error("Error al actualizar líder %s: %s", lider_id, e)
        return False, "Error interno al actualizar el líder."
    finally:
        conn.close()


def toggle_lider_servicio(lider_id: int) -> tuple[bool, str, str]:
    """
    Alterna el estado (pausa o reactivación) de un líder de Casa de Paz.
    Valida la jerarquía con la Casa de Paz asignada antes de reactivar.
    Retorna: (ok: bool, status: str, message: str)
    status: 'reactivado' | 'pausado' | 'bloqueada' | 'error'
    """
    try:
        lider_id = int(lider_id)
    except (ValueError, TypeError):
        return False, 'error', "Identificador de líder no válido."

    conn = get_db_connection()
    if not conn:
        return False, 'error', "Error de conexión a la base de datos."

    try:
        with conn.cursor() as cursor:
            ok, status, mensaje = toggle_estado_lider(cursor, lider_id)
            if ok:
                conn.commit()
                try:
                    invalidate_dashboard_cache()
                except Exception:
                    pass
                return True, status, mensaje
            else:
                conn.rollback()
                return False, status, mensaje
    except Exception as e:
        conn.rollback()
        current_app.logger.error("Error al alternar estado de líder %s: %s", lider_id, e)
        return False, 'error', "Error interno al alternar el estado del líder."
    finally:
        conn.close()


def eliminar_lider_servicio(lider_id_raw: int) -> tuple[bool, str, str]:
    """
    Gestiona la baja de un líder con candados de integridad llamando a eliminar_pausar_lider.
    Retorna: (exito: bool, categoria_flash: str, mensaje: str)
    """
    try:
        lider_id = int(lider_id_raw)
    except (ValueError, TypeError) as e:
        return False, "danger", "Identificador de líder no válido."

    conn = get_db_connection()

    if not conn:
        from services.dashboard_service import mock_mode_enabled
        if mock_mode_enabled():
            from mock_data import get_mock_reportes
            lideres = get_mock_lideres()
            target = next((l for l in lideres if str(l.get('id')) == str(lider_id)), None)
            nombre = f"{target.get('nombre', '')} {target.get('apellido', '')}".strip() if target else f"Líder #{lider_id}"
            reportes = get_mock_reportes()
            total_reps = sum(1 for r in reportes if r.get('lider_nombre') == nombre or (target and r.get('cdp_id') == target.get('cdp_id')))
            if total_reps > 0:
                return False, 'danger', (
                    f"No se puede eliminar al líder '{nombre}' porque tiene {total_reps} reporte(s) registrado(s). "
                    f"Para evitar datos huérfanos y preservar el historial ministerial, debes ponerlo en pausa en su lugar."
                )
            return True, 'success', f"El líder '{nombre}' ha sido eliminado exitosamente del sistema."
        return False, 'danger', "Error de conexión a la base de datos."

    try:
        with conn.cursor() as cursor:

            exito, accion, mensaje = eliminar_pausar_lider(cursor, lider_id)

            categorias = {
                'eliminado': 'success',  # Verde
                'pausado':   'warning',  # Amarillo / Ámbar
                'bloqueada': 'danger',   # Rojo
                'error':     'danger'    # Rojo
            }

            categoria_flash = categorias.get(accion, 'danger')
            if exito:
                conn.commit()

                try:
                    invalidate_dashboard_cache()
                except Exception:
                    pass

                return True, categoria_flash, mensaje
            else:
                conn.rollback()
                return False, categoria_flash, mensaje

    except Exception as e:
        conn.rollback()
        current_app.logger.error("Error en baja de líder %s: %s", lider_id, e)
        return False, "danger", "Error interno al procesar la baja del líder."
    finally:
        conn.close()


def crear_nuevo_usuario(form_data):
    """Fachada retrocompatible hacia services.user_service.crear_nuevo_usuario."""
    return _user_service.crear_nuevo_usuario(
        form_data,
        _conn_provider=get_db_connection,
        _insertar_usuario_fn=insertar_usuario,
        _asignar_sup_fn=asignar_supervisor_a_red,
        _asignar_cdp_fn=asignar_usuario_a_cdp,
    )


def get_opciones_asignacion(usuario_id=None):
    """Fachada retrocompatible hacia services.user_service.get_opciones_asignacion."""
    return _user_service.get_opciones_asignacion(usuario_id=usuario_id, _conn_provider=get_db_connection)


def get_supervisores_disponibles_servicio():
    """Fachada retrocompatible hacia services.red_service.get_supervisores_disponibles_servicio."""
    return _red_service.get_supervisores_disponibles_servicio(_conn_provider=get_db_connection)


def crear_red_servicio(form_data: dict) -> tuple:
    """Fachada retrocompatible hacia services.red_service.crear_red_servicio."""
    return _red_service.crear_red_servicio(
        form_data,
        _conn_provider=get_db_connection,
        _invalidate_cache=invalidate_dashboard_cache,
    )


def obtener_red_servicio(red_id: int):
    """Fachada retrocompatible hacia services.red_service.obtener_red_servicio."""
    return _red_service.obtener_red_servicio(red_id, _conn_provider=get_db_connection)


def actualizar_red_servicio(red_id: int, form_data: dict) -> tuple[bool, str]:
    """Fachada retrocompatible hacia services.red_service.actualizar_red_servicio."""
    return _red_service.actualizar_red_servicio(
        red_id,
        form_data,
        _conn_provider=get_db_connection,
        _invalidate_cache=invalidate_dashboard_cache,
    )


def toggle_red_servicio(red_id: int) -> tuple[bool, str]:
    """Fachada retrocompatible hacia services.red_service.toggle_red_servicio."""
    return _red_service.toggle_red_servicio(
        red_id,
        _conn_provider=get_db_connection,
        _toggle_fn=toggle_estado_red,
        _invalidate_cache=invalidate_dashboard_cache,
    )


def eliminar_red_servicio(red_id: int) -> tuple[bool, str]:
    """Fachada retrocompatible hacia services.red_service.eliminar_red_servicio."""
    return _red_service.eliminar_red_servicio(
        red_id,
        _conn_provider=get_db_connection,
        _eliminar_fn=eliminar_red,
        _invalidate_cache=invalidate_dashboard_cache,
    )