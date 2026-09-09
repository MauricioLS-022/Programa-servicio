"""Obtención de líderes para el directorio administrativo."""
import db_queries
from flask import current_app

from database import get_db_connection
<<<<<<< HEAD
from db_queries import get_lideres, insertar_usuario
=======
from db_queries import (
    get_lideres,
    insertar_usuario,
    asignar_supervisor_a_red,
    asignar_usuario_a_cdp,
    get_redes_disponibles,
    get_cdps_disponibles,
    get_supervisores_disponibles,
)
>>>>>>> ad66ecbc772e359d0c5ba3c7928099fda1159631
from mock_data import get_mock_lideres, get_redes_demo, get_casas_demo
from services.dashboard_service import mock_mode_enabled
from werkzeug.security import generate_password_hash


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
<<<<<<< HEAD
    Lógica de negocio para crear un usuario.
    Recibe los datos del formulario web, valida, encripta y guarda.
    """
    username = form_data.get('username')
    password = form_data.get('password')
    nombre = form_data.get('nombre')
    apellido = form_data.get('apellido')
    tipo_usuario = form_data.get('tipo_usuario')

    # Validaciones básicas (puedes agregar más)
    if not all([username, password, nombre, apellido, tipo_usuario]):
        return False, "Todos los campos son obligatorios."
=======
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
>>>>>>> ad66ecbc772e359d0c5ba3c7928099fda1159631

    conn = get_db_connection()
    if not conn:
        return False, "Error de conexión a la base de datos."

    try:
        with conn.cursor() as cursor:
<<<<<<< HEAD
            # 1. (Opcional pero recomendado) Verificar si el username ya existe
            cursor.execute("SELECT id FROM usuario WHERE username = %s", (username,))
            if cursor.fetchone():
                return False, f"El nombre de usuario '{username}' ya está en uso."

            # 2. Encriptar la contraseña (NUNCA guardar en texto plano)
            password_hash = generate_password_hash(password)

            # 3. Guardar en BD usando tu db_queries
            nuevo_id = insertar_usuario(
                cursor, username, password_hash, nombre, apellido, tipo_usuario
            )
=======
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
>>>>>>> ad66ecbc772e359d0c5ba3c7928099fda1159631
            
        # Confirmar la transacción
        conn.commit()
        return True, "Usuario creado exitosamente."
        
    except Exception as e:
        conn.rollback()
        print(f"[Service] Error al crear usuario: {e}")
        return False, "Ocurrió un error interno al crear el usuario."
    finally:
<<<<<<< HEAD
        conn.close()
=======
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
>>>>>>> ad66ecbc772e359d0c5ba3c7928099fda1159631
