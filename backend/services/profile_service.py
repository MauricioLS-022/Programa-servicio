"""
Servicio de Perfil de Usuario - Consulta de asignaciones, cambio de username y contraseña.
"""
import hmac
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection
from repositories import unit_of_work

logger = logging.getLogger(__name__)


def get_perfil_data(usuario_id, *, _conn_provider=None):
    """
    Obtiene los datos del perfil del usuario, incluyendo su asignación de CDP o Red.
    """
    conn_fn = _conn_provider or get_db_connection
    try:
        with unit_of_work(conn_provider=conn_fn, transactional=False) as uow:
            if uow is None:
                from services.dashboard_service import mock_mode_enabled
                if mock_mode_enabled():
                    return _get_mock_perfil_data(usuario_id)
                return {}

            with uow.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        u.id,
                        u.username,
                        u.nombre,
                        u.apellido,
                        u.tipo_usuario,
                        r_sup.id AS red_sup_id,
                        r_sup.nombre AS red_sup_nombre,
                        c.id AS cdp_id,
                        c.codigo AS cdp_codigo,
                        c.anfitrion AS cdp_anfitrion,
                        r_cdp.id AS cdp_red_id,
                        r_cdp.nombre AS cdp_red_nombre
                    FROM usuario u
                    LEFT JOIN red r_sup ON r_sup.supervisor_id = u.id
                    LEFT JOIN cdp c ON c.usuario_id = u.id
                    LEFT JOIN red r_cdp ON c.red_id = r_cdp.id
                    WHERE u.id = %s
                    """,
                    (str(usuario_id),),
                )
                row = cursor.fetchone() or {}
                if not row:
                    return {}

                perfil = {
                    'id': row.get('id'),
                    'username': row.get('username'),
                    'nombre': row.get('nombre'),
                    'apellido': row.get('apellido'),
                    'tipo_usuario': row.get('tipo_usuario'),
                }
                tipo = perfil.get('tipo_usuario')
                if tipo == 'supervisor':
                    perfil['red_id'] = row.get('red_sup_id')
                    perfil['red_nombre'] = row.get('red_sup_nombre')
                    perfil['red_asignada'] = row.get('red_sup_nombre')
                elif tipo in ('lider_cdp', 'cdp'):
                    perfil['cdp_id'] = row.get('cdp_id')
                    perfil['cdp_codigo'] = row.get('cdp_codigo')
                    perfil['cdp_anfitrion'] = row.get('cdp_anfitrion')
                    if row.get('cdp_codigo'):
                        perfil['cdp_asignada'] = f'Casa "{row.get("cdp_codigo")}"'
                    perfil['red_id'] = row.get('cdp_red_id')
                    perfil['red_nombre'] = row.get('cdp_red_nombre')
                    perfil['red_asignada'] = row.get('cdp_red_nombre')
                elif tipo == 'admin':
                    perfil['asignacion_admin'] = 'Acceso Global'
                    perfil['red_asignada'] = 'Todas las Redes'
                else:
                    if row.get('red_sup_nombre'):
                        perfil['red_nombre'] = row.get('red_sup_nombre')
                        perfil['red_asignada'] = row.get('red_sup_nombre')
                    if row.get('cdp_codigo'):
                        perfil['cdp_codigo'] = row.get('cdp_codigo')
                        perfil['cdp_asignada'] = f'Casa "{row.get("cdp_codigo")}"'
                        perfil['red_nombre'] = row.get('cdp_red_nombre')
                        perfil['red_asignada'] = row.get('cdp_red_nombre')

                return perfil
    except Exception as e:
        logger.error("[DB] Error obteniendo perfil de usuario %s: %s", usuario_id, e)
        return {}


def _get_mock_perfil_data(usuario_id):
    from mock_data import get_mock_usuarios, get_redes_demo, get_casas_demo, get_mock_lideres

    usuarios = get_mock_usuarios()
    user = next(
        (u for u in usuarios if str(u['id']) == str(usuario_id) or str(u.get('username')) == str(usuario_id)),
        None,
    )
    if not user:
        user = usuarios[0]
    perfil = {
        'id': user['id'],
        'username': user['username'],
        'nombre': user['nombre'],
        'apellido': user['apellido'],
        'tipo_usuario': user.get('tipo_usuario') or user.get('rol', ''),
    }
    tipo = perfil['tipo_usuario']
    if tipo == 'supervisor':
        red = next((r for r in get_redes_demo() if str(r.get('supervisor_id')) == str(user['id'])), None)
        if red:
            perfil['red_id'] = red.get('id')
            perfil['red_nombre'] = red.get('nombre')
            perfil['red_asignada'] = red.get('nombre')
    elif tipo in ('lider_cdp', 'cdp'):
        casas = get_casas_demo()
        casa = next((c for c in casas if str(c.get('lider_id')) == str(user['id'])), None)
        if not casa:
            lideres_all = get_mock_lideres()
            lider_match = next((l for l in lideres_all if str(l.get('usuario_id')) == str(user['id'])), None)
            if lider_match:
                casa = next((c for c in casas if c['id'] == lider_match.get('cdp_id')), None)
        if not casa and casas:
            casa = casas[0]
        if casa:
            perfil['cdp_id'] = casa.get('id')
            perfil['cdp_codigo'] = casa.get('codigo')
            perfil['cdp_nombre'] = casa.get('nombre')
            perfil['cdp_anfitrion'] = casa.get('anfitrion')
            perfil['cdp_asignada'] = f'Casa "{casa.get("codigo")}"'
            perfil['red_id'] = casa.get('red_id')
            perfil['red_nombre'] = casa.get('red_nombre')
            perfil['red_asignada'] = casa.get('red_nombre')
    elif tipo == 'admin':
        perfil['asignacion_admin'] = 'Acceso Global'
        perfil['red_asignada'] = 'Todas las Redes'

    return perfil


def update_perfil(usuario_id, nombre, apellido, *, _conn_provider=None):
    """Actualiza los datos del perfil del usuario (nombre y apellido)."""
    conn_fn = _conn_provider or get_db_connection
    try:
        with unit_of_work(conn_provider=conn_fn, transactional=True) as uow:
            if uow is None:
                return False, "No se pudo conectar a la base de datos"
            with uow.cursor() as cursor:
                cursor.execute(
                    "UPDATE usuario SET nombre = %s, apellido = %s WHERE id = %s",
                    (nombre, apellido, str(usuario_id)),
                )
            return True, "Perfil actualizado exitosamente"
    except Exception as e:
        logger.error("[DB] Error actualizando perfil %s: %s", usuario_id, e)
        return False, "Error al actualizar el perfil."


def cambiar_username(usuario_id, nuevo_username, *, _conn_provider=None):
    """Cambia el nombre de usuario verificando que no exista duplicado."""
    if not nuevo_username or len(nuevo_username.strip()) < 3:
        return False, "El nombre de usuario debe tener al menos 3 caracteres"

    nuevo_username = nuevo_username.strip()
    if len(nuevo_username) > 30:
        return False, "El nombre de usuario no puede exceder 30 caracteres"

    conn_fn = _conn_provider or get_db_connection
    try:
        with unit_of_work(conn_provider=conn_fn, transactional=True) as uow:
            if uow is None:
                return False, "No se pudo conectar a la base de datos"
            with uow.cursor() as cursor:
                cursor.execute(
                    "SELECT id FROM usuario WHERE username = %s AND id != %s",
                    (nuevo_username, str(usuario_id)),
                )
                if cursor.fetchone():
                    uow.rollback()
                    return False, "Ese nombre de usuario ya está en uso"

                cursor.execute(
                    "UPDATE usuario SET username = %s WHERE id = %s",
                    (nuevo_username, str(usuario_id)),
                )
            return True, "Nombre de usuario actualizado exitosamente"
    except Exception as e:
        logger.error("[DB] Error cambiando username %s: %s", usuario_id, e)
        return False, "Error al cambiar el nombre de usuario."


def cambiar_password(usuario_id, password_actual, password_nueva, *, _conn_provider=None):
    """Cambia la contraseña verificando la contraseña actual."""
    if not password_nueva or len(password_nueva) < 6:
        return False, "La nueva contraseña debe tener al menos 6 caracteres"

    conn_fn = _conn_provider or get_db_connection
    try:
        with unit_of_work(conn_provider=conn_fn, transactional=True) as uow:
            if uow is None:
                return False, "No se pudo conectar a la base de datos"
            with uow.cursor() as cursor:
                cursor.execute("SELECT password FROM usuario WHERE id = %s", (str(usuario_id),))
                row = cursor.fetchone()
                if not row:
                    uow.rollback()
                    return False, "Usuario no encontrado"

                stored_hash = row.get('password', '')
                password_valida = False
                if stored_hash.count('$') < 2:
                    password_valida = hmac.compare_digest(stored_hash, password_actual)
                else:
                    try:
                        password_valida = check_password_hash(stored_hash, password_actual)
                    except (ValueError, TypeError):
                        password_valida = False

                if not password_valida:
                    uow.rollback()
                    return False, "La contraseña actual es incorrecta"

                nuevo_hash = generate_password_hash(password_nueva)
                cursor.execute(
                    "UPDATE usuario SET password = %s WHERE id = %s",
                    (nuevo_hash, str(usuario_id)),
                )
            return True, "Contraseña actualizada exitosamente"
    except Exception as e:
        logger.error("[DB] Error cambiando password %s: %s", usuario_id, e)
        return False, "Error al cambiar la contraseña."
