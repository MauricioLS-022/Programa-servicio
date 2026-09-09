"""Obtención de usuarios para la administración."""
from flask import current_app

from database import get_db_connection
from db_queries import get_usuarios
from mock_data import get_mock_usuarios
from services.dashboard_service import mock_mode_enabled


def get_usuarios_context(search='', rol='', page=1, per_page=5):
    """Retorna usuarios reales o demo junto con la metadata de paginación."""
    conn = get_db_connection()
    if conn:
        try:
            usuarios, total, total_activos = get_usuarios(conn, search, rol, page, per_page)
        except Exception as error:
            current_app.logger.error('Error obteniendo usuarios: %s', error)
            usuarios, total, total_activos = [], 0, 0
        finally:
            conn.close()
    elif mock_mode_enabled():
        usuarios = get_mock_usuarios()
        if search:
            search_lower = search.lower()
            usuarios = [
                usuario for usuario in usuarios
                if search_lower in ' '.join([
                    usuario['nombre'], usuario['apellido'], usuario['username']
                ]).lower()
            ]
        if rol:
            usuarios = [usuario for usuario in usuarios if usuario['rol'] == rol]
        total = len(usuarios)
        total_activos = sum(usuario['is_active'] for usuario in usuarios)
        start = (page - 1) * per_page
        usuarios = usuarios[start:start + per_page]
    else:
        usuarios, total, total_activos = [], 0, 0

    pages = max((total + per_page - 1) // per_page, 1)
    return {
        'usuarios': usuarios,
        'total_usuarios': total,
        'total_activos': total_activos,
        'page': page,
        'pages': pages,
        'search': search,
        'rol': rol,
    }


def obtener_usuario_por_id(usuario_id):
    """Obtiene los datos de un usuario por su ID (UUID)."""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, username, nombre, apellido, tipo_usuario, is_active
                FROM usuario
                WHERE id = %s
            """, (str(usuario_id),))
            return cursor.fetchone()
    except Exception as e:
        current_app.logger.error("Error obteniendo usuario %s: %s", usuario_id, e)
        return None
    finally:
        conn.close()


def actualizar_usuario_admin(usuario_id, form_data):
    """
    Actualiza los datos de un usuario desde la administración con validaciones de seguridad.
    """
    from utils.validators import (
        validate_username,
        validate_password_strength,
        validate_person_name
    )
    from werkzeug.security import generate_password_hash

    nombre_raw = form_data.get('nombre', '')
    apellido_raw = form_data.get('apellido', '')
    username_raw = form_data.get('username', '')
    password_raw = form_data.get('password', '').strip()
    tipo_usuario = form_data.get('tipo_usuario', '').strip()

    ok_nom, res_nom = validate_person_name(nombre_raw, "Nombre")
    if not ok_nom:
        return False, res_nom

    ok_ape, res_ape = validate_person_name(apellido_raw, "Apellido")
    if not ok_ape:
        return False, res_ape

    ok_user, res_user = validate_username(username_raw)
    if not ok_user:
        return False, res_user

    roles_permitidos = ('admin', 'supervisor', 'lider_cdp')
    if tipo_usuario not in roles_permitidos:
        return False, f"Rol no válido. Debe ser uno de: {', '.join(roles_permitidos)}."

    conn = get_db_connection()
    if not conn:
        return False, "Error de conexión a la base de datos."

    try:
        with conn.cursor() as cursor:
            # Validar unicidad de username excluyendo al propio usuario
            cursor.execute("SELECT id FROM usuario WHERE username = %s AND id != %s", (res_user, str(usuario_id)))
            if cursor.fetchone():
                return False, f"El nombre de usuario '{res_user}' ya está en uso."

            if password_raw:
                ok_pass, res_pass = validate_password_strength(password_raw)
                if not ok_pass:
                    return False, res_pass
                pass_hash = generate_password_hash(password_raw)
                cursor.execute("""
                    UPDATE usuario
                    SET nombre = %s, apellido = %s, username = %s, tipo_usuario = %s, password = %s
                    WHERE id = %s
                """, (res_nom, res_ape, res_user, tipo_usuario, pass_hash, str(usuario_id)))
            else:
                cursor.execute("""
                    UPDATE usuario
                    SET nombre = %s, apellido = %s, username = %s, tipo_usuario = %s
                    WHERE id = %s
                """, (res_nom, res_ape, res_user, tipo_usuario, str(usuario_id)))

        conn.commit()
        return True, "Usuario actualizado exitosamente."
    except Exception as e:
        conn.rollback()
        current_app.logger.error("Error actualizando usuario %s: %s", usuario_id, e)
        return False, "Ocurrió un error al actualizar el usuario."
    finally:
        conn.close()