"""Obtención y gestión de usuarios para la administración."""
import logging
from flask import current_app
from werkzeug.security import generate_password_hash

from database import get_db_connection
from db_queries import (
    get_usuarios,
    insertar_usuario,
    asignar_supervisor_a_red,
    asignar_usuario_a_cdp,
    toggle_estado_usuario,
    get_redes_disponibles,
    get_cdps_disponibles,
)
from mock_data import get_mock_usuarios, get_redes_demo, get_casas_demo
from repositories import unit_of_work
from services.dashboard_service import mock_mode_enabled
from utils.cache import invalidate_dashboard_cache

logger = logging.getLogger(__name__)


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
        redes = get_redes_demo()
        casas = get_casas_demo()
        for u in usuarios:
            red_asig = next((r for r in redes if str(r.get('supervisor_id')) == str(u.get('id'))), None)
            u['red_nombre'] = red_asig['nombre'] if red_asig else None
            cdp_asig = next((c for c in casas if str(c.get('lider_id')) == str(u.get('id')) or str(c.get('usuario_id')) == str(u.get('id'))), None)
            u['cdp_codigo'] = cdp_asig['codigo'] if cdp_asig else None
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
    """Obtiene los datos de un usuario por su ID (UUID), incluyendo asignaciones de red o CDP."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT u.id, u.username, u.nombre, u.apellido, u.tipo_usuario, u.is_active,
                           r.id AS red_id, r.nombre AS red_nombre,
                           c.id AS cdp_id, c.codigo AS cdp_codigo
                    FROM usuario u
                    LEFT JOIN red r ON r.supervisor_id = u.id
                    LEFT JOIN cdp c ON c.usuario_id = u.id
                    WHERE u.id = %s
                """, (str(usuario_id),))
                return cursor.fetchone()
        except Exception as e:
            current_app.logger.error("Error obteniendo usuario %s: %s", usuario_id, e)
            return None
        finally:
            conn.close()
    elif mock_mode_enabled():
        usuarios = get_mock_usuarios()
        u = next((item for item in usuarios if str(item.get('id')) == str(usuario_id)), None)
        if u:
            u_data = dict(u)
            u_data['tipo_usuario'] = u_data.get('rol', u_data.get('tipo_usuario', 'admin'))
            redes = get_redes_demo()
            red_asig = next((r for r in redes if str(r.get('supervisor_id')) == str(usuario_id)), None)
            u_data['red_id'] = red_asig['id'] if red_asig else None
            u_data['red_nombre'] = red_asig['nombre'] if red_asig else None
            casas = get_casas_demo()
            cdp_asig = next((c for c in casas if str(c.get('lider_id')) == str(usuario_id)), None)
            u_data['cdp_id'] = cdp_asig['id'] if cdp_asig else None
            u_data['cdp_codigo'] = cdp_asig['codigo'] if cdp_asig else None
            return u_data
        return None
    return None


def actualizar_usuario_admin(usuario_id, form_data):
    """
    Actualiza los datos de un usuario desde la administración con validaciones de seguridad
    y gestión transaccional de asignaciones ministeriales (red o CDP).
    """
    from utils.validators import (
        validate_username,
        validate_password_strength,
        validate_person_name
    )
    from werkzeug.security import generate_password_hash

    nombre_raw = str(form_data.get('nombre') or '')
    apellido_raw = str(form_data.get('apellido') or '')
    username_raw = str(form_data.get('username') or '')
    password_raw = str(form_data.get('password') or '').strip()
    tipo_usuario = str(form_data.get('tipo_usuario') or form_data.get('rol') or '').strip()

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

            is_active_raw = form_data.get('is_active')
            is_active_val = None
            if is_active_raw is not None and str(is_active_raw).strip() != '':
                is_active_val = 1 if str(is_active_raw).strip().lower() in ('1', 'true', 'on', 'si', 'sí') or is_active_raw is True or is_active_raw == 1 else 0

            if password_raw:
                ok_pass, res_pass = validate_password_strength(password_raw)
                if not ok_pass:
                    return False, res_pass
                pass_hash = generate_password_hash(password_raw)
                if is_active_val is not None:
                    cursor.execute("""
                        UPDATE usuario
                        SET nombre = %s, apellido = %s, username = %s, tipo_usuario = %s, password = %s, is_active = %s
                        WHERE id = %s
                    """, (res_nom, res_ape, res_user, tipo_usuario, pass_hash, is_active_val, str(usuario_id)))
                else:
                    cursor.execute("""
                        UPDATE usuario
                        SET nombre = %s, apellido = %s, username = %s, tipo_usuario = %s, password = %s
                        WHERE id = %s
                    """, (res_nom, res_ape, res_user, tipo_usuario, pass_hash, str(usuario_id)))
            else:
                if is_active_val is not None:
                    cursor.execute("""
                        UPDATE usuario
                        SET nombre = %s, apellido = %s, username = %s, tipo_usuario = %s, is_active = %s
                        WHERE id = %s
                    """, (res_nom, res_ape, res_user, tipo_usuario, is_active_val, str(usuario_id)))
                else:
                    cursor.execute("""
                        UPDATE usuario
                        SET nombre = %s, apellido = %s, username = %s, tipo_usuario = %s
                        WHERE id = %s
                    """, (res_nom, res_ape, res_user, tipo_usuario, str(usuario_id)))

            # Gestión de asignaciones ministeriales según el rol
            red_id_raw = str(form_data.get('red_id') or '').strip()
            cdp_id_raw = str(form_data.get('cdp_id') or '').strip()

            if tipo_usuario == 'supervisor':
                # Si tenía CDP asignada, desvincular
                cursor.execute("UPDATE cdp SET usuario_id = NULL WHERE usuario_id = %s", (str(usuario_id),))
                if red_id_raw:
                    try:
                        red_id = int(red_id_raw)
                        cursor.execute("UPDATE red SET supervisor_id = NULL WHERE supervisor_id = %s AND id != %s", (str(usuario_id), red_id))
                        asignar_supervisor_a_red(cursor, usuario_id, red_id)
                    except (ValueError, TypeError):
                        pass
                else:
                    cursor.execute("UPDATE red SET supervisor_id = NULL WHERE supervisor_id = %s", (str(usuario_id),))

            elif tipo_usuario == 'lider_cdp':
                # Si era supervisor, desvincular de redes
                cursor.execute("UPDATE red SET supervisor_id = NULL WHERE supervisor_id = %s", (str(usuario_id),))
                if cdp_id_raw:
                    try:
                        cdp_id = int(cdp_id_raw)
                        cursor.execute("UPDATE cdp SET usuario_id = NULL WHERE usuario_id = %s AND id != %s", (str(usuario_id), cdp_id))
                        asignar_usuario_a_cdp(cursor, usuario_id, cdp_id)
                    except (ValueError, TypeError):
                        pass
                else:
                    cursor.execute("UPDATE cdp SET usuario_id = NULL WHERE usuario_id = %s", (str(usuario_id),))

            else:  # admin
                cursor.execute("UPDATE red SET supervisor_id = NULL WHERE supervisor_id = %s", (str(usuario_id),))
                cursor.execute("UPDATE cdp SET usuario_id = NULL WHERE usuario_id = %s", (str(usuario_id),))

        conn.commit()
        try:
            invalidate_dashboard_cache()
        except Exception:
            pass
        return True, "Usuario actualizado exitosamente."
    except Exception as e:
        conn.rollback()
        current_app.logger.error("Error actualizando usuario %s: %s", usuario_id, e)
        return False, "Ocurrió un error al actualizar el usuario."
    finally:
        conn.close()


def toggle_usuario_servicio(usuario_id: str, usuario_session_id: str = None) -> tuple[bool, str, str]:
    """
    Alterna el estado is_active de una cuenta de usuario.
    Bloquea la autodesactivación de la cuenta en sesión.
    Retorna: (ok: bool, status: str, message: str)
    status: 'reactivado' | 'desactivado' | 'error'
    """
    if not usuario_id:
        return False, 'error', "Identificador de usuario no proporcionado."

    if usuario_session_id and str(usuario_id) == str(usuario_session_id):
        return False, 'error', "No puedes desactivar tu propia cuenta de usuario en sesión."

    conn = get_db_connection()
    if not conn:
        return False, 'error', "Error de conexión a la base de datos."

    try:
        with conn.cursor() as cursor:
            ok, status, mensaje = toggle_estado_usuario(cursor, usuario_id)
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
        current_app.logger.error("Error al alternar estado de usuario %s: %s", usuario_id, e)
        return False, 'error', "Error interno al alternar el estado del usuario."
    finally:
        conn.close()

def eliminar_usuario_servicio(usuario_id:str, usuario_session_id:str) -> tuple[bool, str,str]:
    """
    Permite eliminar un usuario solo si no es la cuenta en sesión 
    y no tiene redes o casas de paz vinculadas.
    """
    if str(usuario_id) == str(usuario_session_id):
        return False, "danger", "No puedes eliminar tu propia cuenta de usuario en sesión."

    conn = get_db_connection()

    if not conn:
        if mock_mode_enabled():
            redes = get_redes_demo()
            red_vinculada = next((r for r in redes if str(r.get('supervisor_id')) == str(usuario_id)), None)
            if red_vinculada:
                return False, 'danger', f"No se puede eliminar: el usuario es supervisor de la red '{red_vinculada.get('nombre')}'. Desvincula o reasigna la red primero."

            casas = get_casas_demo()
            cdp_vinculada = next((c for c in casas if str(c.get('lider_id')) == str(usuario_id) or str(c.get('usuario_id')) == str(usuario_id)), None)
            if cdp_vinculada:
                return False, 'danger', f"No se puede eliminar: el usuario tiene acceso a la Casa de Paz '{cdp_vinculada.get('codigo')}'. Desvincula la cuenta de la Casa primero."

            return True, 'success', "Usuario eliminado exitosamente del sistema."
        return False, 'danger', "Error de conexión a la base de datos."

    try:
        with conn.cursor() as cursor:
            # Candado 1: Verificar si es supervisor de alguna red
            cursor.execute("SELECT id, nombre FROM red WHERE supervisor_id = %s", (usuario_id,))
            red_vinculada = cursor.fetchone()

            if red_vinculada:
                return False, 'danger', f"No se puede eliminar: el usuario es supervisor de la red '{red_vinculada['nombre']}'. Desvincula o reasigna la red primero."

            # Candado 2: Verificar si tiene CDP asignada
            cursor.execute("SELECT id, codigo FROM cdp WHERE usuario_id = %s", (usuario_id,))
            cdp_vinculada = cursor.fetchone()

            if cdp_vinculada:
                return False, 'danger', f"No se puede eliminar: el usuario tiene acceso a la Casa de Paz '{cdp_vinculada['codigo']}'. Desvincula la cuenta de la Casa primero."

            # Eliminación segura
            cursor.execute("DELETE FROM usuario WHERE id = %s", (usuario_id,))
            conn.commit()

            try:
                invalidate_dashboard_cache()
            except Exception:
                pass

            return True, 'success', "Usuario eliminado exitosamente del sistema."
        
    except Exception as e:
        conn.rollback()
        current_app.logger.error("Error al eliminar usuario %s: %s", usuario_id, e)
        return False, 'danger', "Error interno al eliminar el usuario."
    finally:
        conn.close()


def crear_nuevo_usuario(
    form_data,
    *,
    _conn_provider=None,
    _insertar_usuario_fn=None,
    _asignar_sup_fn=None,
    _asignar_cdp_fn=None,
):
    """Lógica de negocio para crear un usuario con validaciones de seguridad defensivas."""
    from utils.validators import (
        validate_username,
        validate_password_strength,
        validate_person_name,
    )

    username_raw = form_data.get('username', '')
    password_raw = form_data.get('password', '')
    nombre_raw = form_data.get('nombre', '')
    apellido_raw = form_data.get('apellido', '')
    tipo_usuario = (form_data.get('tipo_usuario') or form_data.get('rol') or '').strip()

    ok_nom, res_nom = validate_person_name(nombre_raw, "Nombre")
    if not ok_nom:
        return False, res_nom

    ok_ape, res_ape = validate_person_name(apellido_raw, "Apellido")
    if not ok_ape:
        return False, res_ape

    ok_user, res_user = validate_username(username_raw)
    if not ok_user:
        return False, res_user

    ok_pass, res_pass = validate_password_strength(password_raw)
    if not ok_pass:
        return False, res_pass

    roles_permitidos = ('admin', 'supervisor', 'lider_cdp')
    if tipo_usuario not in roles_permitidos:
        return False, f"Rol no válido. Debe ser uno de: {', '.join(roles_permitidos)}."

    conn_fn = _conn_provider or get_db_connection
    ins_user = _insertar_usuario_fn or insertar_usuario
    asig_sup = _asignar_sup_fn or asignar_supervisor_a_red
    asig_cdp = _asignar_cdp_fn or asignar_usuario_a_cdp

    try:
        with unit_of_work(conn_provider=conn_fn, transactional=True) as uow:
            if uow is None:
                return False, "Error de conexión a la base de datos."
            with uow.cursor() as cursor:
                cursor.execute("SELECT id FROM usuario WHERE username = %s", (res_user,))
                if cursor.fetchone():
                    uow.rollback()
                    return False, f"El nombre de usuario '{res_user}' ya está en uso."

                password_hash = generate_password_hash(password_raw)
                nuevo_id = ins_user(cursor, res_user, password_hash, res_nom, res_ape, tipo_usuario)

                red_id_raw = str(form_data.get('red_id') or '').strip()
                cdp_id_raw = str(form_data.get('cdp_id') or '').strip()

                if tipo_usuario == 'supervisor' and red_id_raw:
                    try:
                        asig_sup(cursor, nuevo_id, int(red_id_raw))
                    except (ValueError, TypeError):
                        pass
                elif tipo_usuario == 'lider_cdp' and cdp_id_raw:
                    try:
                        asig_cdp(cursor, nuevo_id, int(cdp_id_raw))
                    except (ValueError, TypeError):
                        pass

        return True, "Usuario creado exitosamente."
    except Exception as e:
        logger.error("Error al crear usuario: %s", e)
        return False, "Ocurrió un error interno al crear el usuario."


def get_opciones_asignacion(usuario_id=None, *, _conn_provider=None):
    """Obtiene redes y CDPs disponibles para los selectores de asignación de usuarios."""
    conn_fn = _conn_provider or get_db_connection
    try:
        with unit_of_work(conn_provider=conn_fn, transactional=False) as uow:
            if uow is not None:
                with uow.cursor() as cursor:
                    redes = get_redes_disponibles(cursor, usuario_id=usuario_id)
                    cdps = get_cdps_disponibles(cursor, usuario_id=usuario_id)
                return redes, cdps
    except Exception as e:
        logger.error("Error obteniendo opciones de asignación: %s", e)
        return [], []

    if mock_mode_enabled():
        redes_demo = get_redes_demo()
        redes = [
            {'id': r['id'], 'nombre': r['nombre']}
            for r in redes_demo
            if not r.get('supervisor_id') or (usuario_id and str(r.get('supervisor_id')) == str(usuario_id))
        ]
        casas_demo = get_casas_demo()
        cdps = [
            {
                'id': c['id'],
                'codigo': c['codigo'],
                'direccion': c.get('direccion', ''),
                'red_nombre': c.get('red_nombre', ''),
            }
            for c in casas_demo
            if not c.get('lider_id') or (usuario_id and str(c.get('lider_id')) == str(usuario_id))
        ]
        return redes, cdps
    return [], []
