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
    obtener_red_por_id
)
from mock_data import get_mock_lideres, get_redes_demo, get_casas_demo
from services.dashboard_service import mock_mode_enabled
from werkzeug.security import generate_password_hash

from utils.validators import validate_name_red


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

def crear_nuevo_usuario(form_data):
    """
    Lógica de negocio para crear un usuario con validaciones de seguridad defensivas.
    """
    from utils.validators import (
        validate_username,
        validate_password_strength,
        validate_person_name
    )

    username_raw = form_data.get('username', '')
    password_raw = form_data.get('password', '')
    nombre_raw = form_data.get('nombre', '')
    apellido_raw = form_data.get('apellido', '')
    tipo_usuario = form_data.get('tipo_usuario', '').strip()

    # Validar Nombre y Apellido
    ok_nom, res_nom = validate_person_name(nombre_raw, "Nombre")
    if not ok_nom:
        return False, res_nom

    ok_ape, res_ape = validate_person_name(apellido_raw, "Apellido")
    if not ok_ape:
        return False, res_ape

    # Validar Username
    ok_user, res_user = validate_username(username_raw)
    if not ok_user:
        return False, res_user

    # Validar Complejidad de Contraseña
    ok_pass, res_pass = validate_password_strength(password_raw)
    if not ok_pass:
        return False, res_pass

    # Validar Rol permitido
    roles_permitidos = ('admin', 'supervisor', 'lider_cdp')
    if tipo_usuario not in roles_permitidos:
        return False, f"Rol no válido. Debe ser uno de: {', '.join(roles_permitidos)}."

    conn = get_db_connection()
    if not conn:
        return False, "Error de conexión a la base de datos."

    try:
        with conn.cursor() as cursor:
            # 1. Verificar si el username ya existe
            cursor.execute("SELECT id FROM usuario WHERE username = %s", (res_user,))
            if cursor.fetchone():
                return False, f"El nombre de usuario '{res_user}' ya está en uso."

            # 2. Encriptar la contraseña (NUNCA guardar en texto plano)
            password_hash = generate_password_hash(password_raw)

            # 3. Guardar en BD usando tu db_queries
            nuevo_id = insertar_usuario(
                cursor, res_user, password_hash, res_nom, res_ape, tipo_usuario
            )

            # 4. Asignación opcional según el rol seleccionado
            red_id_raw = form_data.get('red_id', '').strip()
            cdp_id_raw = form_data.get('cdp_id', '').strip()

            if tipo_usuario == 'supervisor' and red_id_raw:
                try:
                    red_id = int(red_id_raw)
                    asignar_supervisor_a_red(cursor, nuevo_id, red_id)
                except (ValueError, TypeError):
                    pass
            elif tipo_usuario == 'lider_cdp' and cdp_id_raw:
                try:
                    cdp_id = int(cdp_id_raw)
                    asignar_usuario_a_cdp(cursor, nuevo_id, cdp_id)
                except (ValueError, TypeError):
                    pass
            
        # Confirmar la transacción
        conn.commit()
        return True, "Usuario creado exitosamente."
        
    except Exception as e:
        conn.rollback()
        print(f"[Service] Error al crear usuario: {e}")
        return False, "Ocurrió un error interno al crear el usuario."
    finally:
        conn.close()


def get_opciones_asignacion():
    """
    Obtiene redes y CDPs disponibles para los selectores de asignación en form_usuario.
    """
    conn = get_db_connection()
    if not conn:
        return [], []
    try:
        with conn.cursor() as cursor:
            redes = get_redes_disponibles(cursor)
            cdps = get_cdps_disponibles(cursor)
        return redes, cdps
    except Exception as e:
        current_app.logger.error("Error obteniendo opciones de asignación: %s", e)
        return [], []
    finally:
        conn.close()


def get_supervisores_disponibles_servicio():
    """
    Obtiene la lista de usuarios con rol supervisor que no tienen red asignada.
    """
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            return get_supervisores_disponibles(cursor)
    except Exception as e:
        current_app.logger.error("Error obteniendo supervisores disponibles: %s", e)
        return []
    finally:
        conn.close()


def crear_red_servicio(form_data: dict) -> tuple:
    """
    Valida y procesa la creación de una nueva red ministerial.
    Retorna: (success: bool, message: str)
    """
    nombre_red_raw = form_data.get('nombre', '').strip()
    supervisor_id = form_data.get('supervisor_id', '').strip()

    is_valid, res_red = validate_name_red(nombre_red_raw)
    if not is_valid:
        return False, res_red

    conn = get_db_connection()
    if not conn:
        return False, 'Error de conexión a la base de datos.'

    try: 
        with conn.cursor() as cursor:
            #1. Verificar que no exista otra red con el mismo nombre
            cursor.execute("SELECT id FROM red WHERE nombre = %s", (res_red,))

            if cursor.fetchone():
                return False, f"Ya existe una red con el nombre '{res_red}'."
            #2. Validar supervisor si fue seleccionado
            sup_final = None
            if supervisor_id:
                # Comprobar que usuario exista y sea supervisor
                cursor.execute("SELECT id FROM usuario WHERE id = %s AND tipo_usuario = 'supervisor'", (supervisor_id,))
                if not cursor.fetchone():
                    return False, "El supervisor seleccionado no es válido."
                # Comprobar regla 1 a 1: que no esté asignado a otra red
                cursor.execute("SELECT id, nombre FROM red WHERE supervisor_id = %s", (supervisor_id,))
                red_ocupada = cursor.fetchone()
                if red_ocupada:
                    return False, f"Este supervisor ya está asignado a la red '{red_ocupada['nombre']}'"

                sup_final = supervisor_id

            #3. Insertar la nueva red
            insertar_red(cursor, res_red, sup_final)
            conn.commit()

            try:
                invalidate_dashboard_cache()
            except Exception:
                pass

            return True, "Red creada exitosamente."
            
    except Exception as e:
        conn.rollback()
        current_app.logger.error("Error creando red: %s", e)
        return False, f"Error interno al crear la red: {str(e)}"
    finally:
        conn.close()


def obtener_red_servicio(red_id:int):
    """
    Obtiene los datos de una red específica por su ID.
    Retorna el diccionario de la red o None si no existe.
    """
    conn = get_db_connection()
    if not conn:
        return None
    try: 
        with conn.cursor() as cursor:
            return obtener_red_por_id(cursor, red_id)
    except Exception as e:
        current_app.logger.error("Error al obtener red %s: %s",red_id, e)
        return None
    finally:
        conn.close()

def actualizar_red_servicio(red_id:int, form_data:dict) -> tuple[bool, str]:
    """
    Actualiza el nombre y supervisor de una red existente.
    Retorna: (success: bool, message: str)
    """
    nombre_red_raw = form_data.get('nombre', '').strip()
    supervisor_id = form_data.get('supervisor_id', '').strip()

    is_valid, res_red = validate_name_red(nombre_red_raw)
    if not is_valid:
        return False, res_red
    
    conn = get_db_connection()
    if not conn:
        return False, 'Error de conexión a la base de datos.'

    try:
        with conn.cursor() as cursor:
            #1. Verificar que la red exista
            cursor.execute("SELECT id FROM red WHERE id = %s", (red_id,))
            if not cursor.fetchone():
                return False, "La red especificada no existe."

            #2. Verificar que no exista otra red con el mismo nombre
            cursor.execute("SELECT id FROM red WHERE nombre = %s AND id != %s", (res_red, red_id))
            if cursor.fetchone():
                return False, f"Ya existe otra red con el nombre '{res_red}'."
            
            #3. Validar supervisor si fue seleccionado
            sup_final = None
            if supervisor_id:
                cursor.execute("SELECT id FROM usuario WHERE id = %s AND tipo_usuario = 'supervisor'", (supervisor_id,))
                if not cursor.fetchone():
                    return False, "El supervisor seleccionado no es válido."
                # Comprobar que no este en otra red
                cursor.execute("SELECT id, nombre FROM red WHERE supervisor_id = %s AND id != %s", (supervisor_id, red_id))
                red_ocupada = cursor.fetchone()
                if red_ocupada:
                    return False, f"Este supervisor ya está asignado a la red '{red_ocupada['nombre']}'"
                sup_final = supervisor_id

            #4. Actualizar la red
            actualizar_red(cursor, red_id, res_red, sup_final)
        conn.commit()
        try:
            invalidate_dashboard_cache()
        except Exception:
            pass
        return True, "Red actualizada exitosamente."
    except Exception as e:
        conn.rollback()
        current_app.logger.error("Error actualizando red: %s", e)
        return False, f"Error interno al actualizar la red: {str(e)}"
    finally:
        conn.close()

def toggle_red_servicio(red_id:int) -> tuple[bool, str]:
    """
    Pone en pausa o reactiva una red.
    Retorna: (success: bool, message: str)
    """
    conn = get_db_connection()
    if not conn: 
        return False, 'Error de conexión a la base de datos.'

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT nombre FROM red WHERE id = %s", (red_id,))
            red = cursor.fetchone()
            if not red:
                return False, "La red especificada no existe."

            quedo_activa = toggle_estado_red(cursor, red_id)
        conn.commit()

        try:
            invalidate_dashboard_cache()
        except Exception:
            pass

        estado = 'reactivada' if quedo_activa else 'puesta en pausa'
        return True, f"La red '{red['nombre']}' ha sido {estado} exitosamente."
    
    except Exception as e:
        conn.rollback()
        current_app.logger.error("Error al cambiar el estado de la red %s: %s", red_id, e)
        return False, f"Error interno al cambiar el estado de la red"
    finally:
        conn.close()

def eliminar_red_servicio(red_id:int) -> tuple[bool, str]:
    """
    Elimina una red si no tiene Casas de Paz vinculadas.
    Retorna: (success: bool, message: str)
    """
    conn = get_db_connection()
    if not conn:
        return False, 'Error de conexión a la base de datos.'

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT nombre FROM red WHERE id = %s", (red_id,))
            red = cursor.fetchone()
            if not red:
                return False, "La red especificada no existe."

            exito = eliminar_red(cursor, red_id)
            if not exito:
                return False, f"No se puede eliminar la red '{red['nombre']}' porque tiene Casas de Paz vinculadas.  Reasigna las casas primero o pon la red en pausa."
        conn.commit()

        try:
            invalidate_dashboard_cache()
        except Exception:
            pass

        return True, f"La red '{red['nombre']}' ha sido eliminada exitosamente."

    except Exception as e:
        conn.rollback()
        current_app.logger.error("Error al eliminar la red %s: %s", red_id, e)
        return False, f"Error interno al eliminar la red"
    finally:
        conn.close()