"""
services/queries/usuarios_queries.py - Consultas de usuarios y asignaciones.
"""
import uuid
from pymysql.cursors import Cursor

def get_usuarios(conn, search='', rol='', page=1, per_page=5):
    """Obtiene usuarios paginados para el directorio administrativo."""
    offset = (page - 1) * per_page
    filters = []
    params = []

    if search:
        filters.append("(u.nombre LIKE %s OR u.apellido LIKE %s OR u.username LIKE %s)")
        search_value = f"%{search}%"
        params.extend([search_value, search_value, search_value])
    if rol:
        filters.append("u.tipo_usuario = %s")
        params.append(rol)

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ''
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) AS total FROM usuario u {where_clause}", params)
    total = int(cur.fetchone()['total'])

    cur.execute(f"""
        SELECT u.id, u.username, u.nombre, u.apellido, u.tipo_usuario AS rol, u.is_active,
               (SELECT r.nombre FROM red r WHERE r.supervisor_id = u.id LIMIT 1) AS red_nombre,
               (SELECT c.codigo FROM cdp c WHERE c.usuario_id = u.id LIMIT 1) AS cdp_codigo
        FROM usuario u
        {where_clause}
        ORDER BY u.nombre IS NULL, u.nombre, u.apellido IS NULL, u.apellido, u.username
        LIMIT %s OFFSET %s
    """, [*params, per_page, offset])
    usuarios = cur.fetchall() or []

    cur.execute("SELECT COUNT(*) AS total FROM usuario WHERE is_active = 1")
    total_activos = int(cur.fetchone()['total'])
    cur.close()
    return usuarios, total, total_activos


def insertar_usuario(cursor, username, password_hash, nombre, apellido, tipo_usuario):
    """
    Inserta un nuevo usuario en la base de datos y retorna su UUID generado.
    """
    nuevo_id = str(uuid.uuid4())
    query = """
        INSERT INTO usuario (id, username, password, nombre, apellido, tipo_usuario)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (nuevo_id, username, password_hash, nombre, apellido, tipo_usuario))
    return nuevo_id


def toggle_estado_usuario(cursor: Cursor, usuario_id: str) -> tuple[bool, str, str]:
    """
    Alterna el estado is_active de un usuario entre 1 y 0.
    
    Retorna: (éxito: bool, acción: 'reactivado' | 'desactivado' | 'error', mensaje: str)
    """
    cursor.execute("""
        SELECT id, username, nombre, apellido, is_active 
        FROM usuario 
        WHERE id = %s
    """, (str(usuario_id),))
    usuario = cursor.fetchone()

    if not usuario:
        return False, 'error', "El usuario no existe."

    nombre_display = f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}".strip() or usuario.get('username', '')
    is_active = bool(usuario.get('is_active', 0))

    if not is_active:
        cursor.execute("UPDATE usuario SET is_active = 1 WHERE id = %s", (str(usuario_id),))
        return True, 'reactivado', f"El usuario '{nombre_display}' ha sido reactivado exitosamente."
    else:
        cursor.execute("UPDATE usuario SET is_active = 0 WHERE id = %s", (str(usuario_id),))
        return True, 'desactivado', f"El usuario '{nombre_display}' ha sido desactivado exitosamente."


def get_supervisores_disponibles(cursor):
    """
    Retorna los usuarios con rol 'supervisor' que aún no tienen una red asignada.
    """
    cursor.execute("""
        SELECT u.id, u.nombre, u.apellido, u.username
        FROM usuario u
        LEFT JOIN red r ON r.supervisor_id = u.id
        WHERE u.tipo_usuario = 'supervisor' AND r.id IS NULL
        ORDER BY u.nombre, u.apellido
    """)
    return cursor.fetchall() or []


