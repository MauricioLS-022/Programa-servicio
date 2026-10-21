"""
services/queries/estructura_queries.py - Consultas de redes y casas de paz.
"""
import uuid
from pymysql.cursors import Cursor

def obtener_cdp_por_usuario(cursor, usuario_id):
    """Obtiene la Casa de Paz asignada a un usuario específico."""
    query = "SELECT id, codigo, anfitrion, telefono, direccion, red_id FROM cdp WHERE usuario_id = %s"
    cursor.execute(query, (usuario_id,))
    return cursor.fetchone()


def get_redes_disponibles(cursor, usuario_id=None):
    """
    Retorna las redes ministeriales que no tienen supervisor asignado,
    o la red actualmente asignada al usuario_id indicado (para edición).
    """
    if usuario_id:
        cursor.execute("""
            SELECT id, nombre
            FROM red
            WHERE supervisor_id IS NULL OR supervisor_id = %s
            ORDER BY nombre ASC
        """, (str(usuario_id),))
    else:
        cursor.execute("""
            SELECT id, nombre
            FROM red
            WHERE supervisor_id IS NULL
            ORDER BY nombre ASC
        """)
    return cursor.fetchall() or []


def get_todas_las_redes(cursor: Cursor):
    """
    Retorna todas las redes activas para asignación en Casas de Paz.
    """
    cursor.execute("""
        SELECT id, nombre
        FROM red
        WHERE is_active = 1
        ORDER BY nombre ASC
    """)
    return cursor.fetchall() or []


def insertar_red(cursor: Cursor, nombre, supervisor_id):
    """ 
    Inserta una nueva red ministerial en la base de datos.
    """
    query = """
        INSERT INTO red (nombre, is_active, supervisor_id) 
        VALUES (%s, 1, %s);
    """
    sup_id = supervisor_id if supervisor_id else None

    cursor.execute(query, (nombre.strip(), sup_id))
    return cursor.lastrowid  # Retorna el ID de la nueva red insertada


def obtener_red_por_id(cursor: Cursor, red_id):
    """
    Obtiene una red ministerial por su ID con el conteo de Casas de Paz vinculadas.
    """
    query = """
        SELECT r.*, 
        (SELECT COUNT(*) FROM cdp WHERE red_id = r.id) AS total_casas
        FROM red r
        WHERE r.id = %s
    """
    cursor.execute(query, (red_id,))
    return cursor.fetchone()


def get_redes_activas_select(cursor: Cursor):
    """
    Retorna todas las redes activas para el selector <select name="red_id"> de las Casas de Paz.
    """
    cursor.execute("SELECT id FROM red WHERE is_active = 1 ORDER BY nombre ASC")
    return cursor.fetchall() or []


def actualizar_red(cursor: Cursor, red_id, nombre, supervisor_id):
    """
    Actualiza los detalles de una red ministerial existente.
    """
    query = """
        UPDATE red SET nombre = %s, supervisor_id = %s
        WHERE id = %s
    """
    sup_id = supervisor_id if supervisor_id else None
    cursor.execute(query, (nombre.strip(), sup_id, red_id))
    return cursor.rowcount >= 0  # Retorna True si se actualizó alguna fila


def toggle_estado_red(cursor: Cursor, red_id):
    """
    Alterna el estado is_active de la red entre 1 y 0.
    Retorna el nuevo estado de la red (True si quedó activa, False si quedó pausada).
    """
    # 1. Invertir el valor de is_active en la BD
    query = """
        UPDATE red 
        SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END
        WHERE id = %s
    """

    cursor.execute(query, (red_id,))

    # 2. Consultar el nuevo estado para saber qué mensaje mostrar al usuario
    cursor.execute("SELECT is_active FROM red WHERE id = %s", (red_id,))
    fila = cursor.fetchone()
    return bool(fila['is_active']) if fila else None


def eliminar_red(cursor: Cursor, red_id):
    """
    Elimina una red ministerial de la base de datos.
    Retorna True si se eliminó correctamente, False si no existía.
    """
    # verificar si tiene casas de paz asociadas
    cursor.execute("SELECT COUNT(*) AS total_casas FROM cdp WHERE red_id = %s", (red_id,))
    total_casas = cursor.fetchone()['total_casas']
    # en caspo de que tenga casas de paz asociadas
    if total_casas > 0: 
        return False # No se puede eliminar si tiene casas de paz asociadas

    else: 
        # eliminar la red
        cursor.execute("DELETE FROM red WHERE id = %s", (red_id,))
        return cursor.rowcount > 0  # Retorna True si se eliminó alguna fila


def get_cdps_disponibles(cursor, usuario_id=None):
    """
    Retorna las Casas de Paz que no tienen usuario (líder) asignado,
    o la Casa de Paz actualmente asignada al usuario_id indicado (para edición).
    """
    if usuario_id:
        cursor.execute("""
            SELECT c.id, c.codigo, c.direccion, c.red_id, r.nombre AS red_nombre
            FROM cdp c
            LEFT JOIN red r ON c.red_id = r.id
            WHERE c.usuario_id IS NULL OR c.usuario_id = %s
            ORDER BY c.codigo ASC
        """, (str(usuario_id),))
    else:
        cursor.execute("""
            SELECT c.id, c.codigo, c.direccion, c.red_id, r.nombre AS red_nombre
            FROM cdp c
            LEFT JOIN red r ON c.red_id = r.id
            WHERE c.usuario_id IS NULL
            ORDER BY c.codigo ASC
        """)
    return cursor.fetchall() or []


def asignar_supervisor_a_red(cursor, usuario_id, red_id):
    """
    Asigna un usuario supervisor a una red ministerial.
    """
    cursor.execute(
        "UPDATE red SET supervisor_id = %s WHERE id = %s AND (supervisor_id IS NULL OR supervisor_id = %s)",
        (str(usuario_id), int(red_id), str(usuario_id))
    )
    return cursor.rowcount > 0


def asignar_usuario_a_cdp(cursor, usuario_id, cdp_id):
    """
    Asigna un usuario líder a una Casa de Paz.
    """
    cursor.execute(
        "UPDATE cdp SET usuario_id = %s WHERE id = %s AND (usuario_id IS NULL OR usuario_id = %s)",
        (str(usuario_id), int(cdp_id), str(usuario_id))
    )
    return cursor.rowcount > 0


def insertar_cdp(cursor: Cursor, codigo: str, anfitrion: str, direccion: str, telefono: str, red_id: int, usuario_id: str = None):
    """
    Inserta una nueva Casa de Paz vinculada a una red y a su usuario de acceso.
    """
    query = """
        INSERT INTO cdp (codigo, anfitrion, direccion, is_active, telefono, red_id, usuario_id) 
        VALUES (%s, %s, %s, 1, %s, %s, %s)
    """
    cursor.execute(query, (codigo.strip(), anfitrion.strip(), direccion.strip(), telefono.strip(), red_id, usuario_id))
    return cursor.lastrowid


def obtener_cdp_admin(cursor: Cursor, cdp_id: int):
    """
    Obtiene los datos completos de una CDP incluyendo los datos del usuario asignado.
    """
    query = """
        SELECT c.*, u.username, u.nombre AS usuario_nombre, u.apellido AS usuario_apellido, r.nombre as red_nombre
        FROM cdp c
        LEFT JOIN usuario u ON c.usuario_id = u.id
        LEFT JOIN red r ON c.red_id = r.id
        WHERE c.id = %s
    """

    cursor.execute(query, (cdp_id,))
    return cursor.fetchone()


def actualizar_cdp_admin(cursor: Cursor, cdp_id: int, codigo: str, anfitrion: str, telefono: str, direccion:str, red_id:int, is_active: int = None):
    """
    Actualiza la información física y organizativa de la Casa de Paz.
    """
    if is_active is not None:
        query = """
        UPDATE cdp 
        SET codigo = %s, anfitrion = %s, telefono = %s, direccion = %s, red_id = %s, is_active = %s
        WHERE id = %s
        """
        cursor.execute(query, (codigo.strip(), anfitrion.strip(), telefono.strip(), direccion.strip(), red_id, int(is_active), cdp_id))
    else:
        query = """
        UPDATE cdp 
        SET codigo = %s, anfitrion = %s, telefono = %s, direccion = %s, red_id = %s
        WHERE id = %s
        """
        cursor.execute(query, (codigo.strip(), anfitrion.strip(), telefono.strip(), direccion.strip(), red_id, cdp_id))
    return cursor.rowcount >= 0


def eliminar_pausar_cdp(cursor: Cursor, cdp_id: int) -> tuple[bool, str, str]:
    """
    Gestiona la baja de una Casa de Paz preservando la integridad:
    - Validación 1: Si tiene líderes asignados, BLOQUEA la acción exigiendo su reasignación previa.
    - Validación 2: Si tiene reportes históricos, realiza soft delete (is_active = 0) en CDP y usuario.
    - Si NO tiene reportes ni líderes: Realiza eliminación física completa (CDP y usuario de acceso).
    
    Retorna: (éxito: bool, acción: 'bloqueada' | 'pausada' | 'eliminada' | 'error', mensaje: str)
    """
    # 1. Obtener usuario_id asociado a la CDP
    cursor.execute("SELECT usuario_id, codigo FROM cdp WHERE id = %s", (cdp_id,))
    cdp = cursor.fetchone()

    if not cdp:
        return False, 'error', "La casa de paz no existe."

    codigo_cdp = cdp.get('codigo')
    usuario_id = cdp.get('usuario_id')

    # 2. Verificar si tiene lideres asignados
    cursor.execute('SELECT COUNT(*) AS total FROM lider WHERE cdp_id = %s', (cdp_id,))
    total_lideres = cursor.fetchone()['total']

    if total_lideres > 0:
        return(
            False, 
            'bloqueada',
            f"No se puede dar de baja la Casa de Paz '{codigo_cdp}' porque tiene {total_lideres} líder(es) asignado(s). "
            f"Reasígnalos a otra Casa desde el botón de edición antes de continuar."
        )

    # 3. Verificar si tiene reportes históricos
    cursor.execute("SELECT COUNT(*) AS total FROM reporte WHERE cdp_id = %s", (cdp_id,))
    total_reportes = cursor.fetchone()['total']

    if total_reportes > 0:
        # --- CASO A: TIENE HISTORIAL -> DESACTIVACIÓN LÓGICA ---
        cursor.execute('UPDATE cdp SET is_active = 0 WHERE id = %s', (cdp_id,))

        if usuario_id:
            cursor.execute("UPDATE usuario SET is_active = 0 WHERE id = %s", (usuario_id,))

        return True, 'pausada', f"La Casa de Paz '{codigo_cdp}' tiene {total_reportes} reportes históricos. Ha sido pausada y su acceso desactivado para proteger las estadísticas."

    else:
        # --- CASO B: NO TIENE HISTORIAL -> ELIMINACIÓN FÍSICA LIMPIA ---
        # 1. Eliminar la CDP
        cursor.execute('DELETE FROM cdp WHERE id = %s', (cdp_id,)) 
        # 2. Eliminar el usuario de acceso para liberar el username
        if usuario_id:
            cursor.execute('DELETE FROM usuario WHERE id = %s', (usuario_id,))

        return True, 'eliminada', f"La Casa de Paz '{codigo_cdp}' y su cuenta de acceso han sido eliminadas permanentemente."


def toggle_estado_cdp(cursor: Cursor, cdp_id: int) -> tuple[bool, str, str]:
    """
    Alterna el estado is_active de una Casa de Paz y su cuenta de acceso vinculada.
    Valida que la Red Ministerial a la que pertenece esté activa antes de permitir la reactivación.
    
    Retorna: (éxito: bool, acción: 'bloqueada' | 'reactivada' | 'pausada' | 'error', mensaje: str)
    """
    cursor.execute("""
        SELECT c.id, c.codigo, c.is_active, c.red_id, c.usuario_id, 
               r.nombre AS red_nombre, r.is_active AS red_is_active 
        FROM cdp c 
        JOIN red r ON c.red_id = r.id 
        WHERE c.id = %s
    """, (cdp_id,))
    cdp = cursor.fetchone()

    if not cdp:
        return False, 'error', "La Casa de Paz no existe o no tiene Red Ministerial asignada."

    codigo = cdp.get('codigo', '')
    red_nombre = cdp.get('red_nombre', '')
    usuario_id = cdp.get('usuario_id')
    is_active = bool(cdp.get('is_active', 0))
    red_is_active = bool(cdp.get('red_is_active', 0))

    if not is_active:
        # Intento de reactivación: validar que la red esté activa
        if not red_is_active:
            return (
                False, 
                'bloqueada', 
                f"No se puede reactivar la Casa de Paz '{codigo}' porque su Red Ministerial '{red_nombre}' se encuentra en pausa. Debe reactivar la Red primero."
            )
        cursor.execute("UPDATE cdp SET is_active = 1 WHERE id = %s", (cdp_id,))
        if usuario_id:
            cursor.execute("UPDATE usuario SET is_active = 1 WHERE id = %s", (usuario_id,))
        return True, 'reactivada', f"La Casa de Paz '{codigo}' y su cuenta de acceso han sido reactivadas exitosamente."
    else:
        # Poner en pausa
        cursor.execute("UPDATE cdp SET is_active = 0 WHERE id = %s", (cdp_id,))
        if usuario_id:
            cursor.execute("UPDATE usuario SET is_active = 0 WHERE id = %s", (usuario_id,))
        return True, 'pausada', f"La Casa de Paz '{codigo}' ha sido puesta en pausa y su cuenta de acceso desactivada."


