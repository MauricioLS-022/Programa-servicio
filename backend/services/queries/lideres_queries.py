"""
services/queries/lideres_queries.py - Consultas de líderes ministeriales.
"""
from pymysql.cursors import Cursor

def get_lideres(conn, search='', rol='', red_id='', cdp_id='', supervisor_red_id=None, page=1, per_page=10):
    """Obtiene líderes paginados junto con las opciones de sus filtros."""
    offset = (page - 1) * per_page
    filters = []
    params = []

    if search:
        filters.append("(CONCAT(l.nombre, ' ', l.apellido) LIKE %s OR l.telefono LIKE %s)")
        search_value = f"%{search}%"
        params.extend([search_value, search_value])
    if rol:
        filters.append("l.rol = %s")
        params.append(rol)
    if red_id:
        filters.append("c.red_id = %s")
        params.append(red_id)
    if cdp_id:
        filters.append("l.cdp_id = %s")
        params.append(cdp_id)
    if supervisor_red_id is not None:
        filters.append("c.red_id = %s")
        params.append(supervisor_red_id)

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ''
    cur = conn.cursor()
    cur.execute(f"""
        SELECT COUNT(*) AS total
        FROM lider l
        JOIN cdp c ON c.id = l.cdp_id
        {where_clause}
    """, params)
    total = int(cur.fetchone()['total'])

    cur.execute(f"""
        SELECT l.id, l.nombre, l.apellido, l.rol, l.telefono, l.is_active,
               c.id AS cdp_id, c.codigo AS cdp_nombre, c.is_active AS cdp_is_active,
               r.id AS red_id, r.nombre AS red_nombre
        FROM lider l
        JOIN cdp c ON c.id = l.cdp_id
        LEFT JOIN red r ON r.id = c.red_id
        {where_clause}
        ORDER BY l.nombre, l.apellido
        LIMIT %s OFFSET %s
    """, [*params, per_page, offset])
    lideres = cur.fetchall() or []

    cur.execute("SELECT id, nombre FROM red ORDER BY nombre")
    redes = cur.fetchall() or []
    cur.execute("SELECT id, codigo AS nombre, red_id FROM cdp ORDER BY codigo")
    casas = cur.fetchall() or []
    cur.close()
    return lideres, total, redes, casas


def obtener_lideres_por_cdp(cursor, cdp_id):
    """Obtiene todos los líderes asociados a una Casa de Paz."""
    query = "SELECT id, nombre, apellido, rol, telefono FROM lider WHERE cdp_id = %s ORDER BY FIELD(rol, 'Lider', 'Sublider'), nombre ASC"
    cursor.execute(query, (cdp_id,))
    return cursor.fetchall() or []


def obtener_lideres_por_cdp(cursor: Cursor, cdp_id: int):
    """
    Obtiene todos los líderes y sublíderes ACTIVOS asociados a una Casa de Paz específica.
    Utilizada en generar_reporte y en la vista del dashboard.
    """
    query = """
        SELECT id, nombre, apellido, rol, telefono
        FROM lider
        WHERE cdp_id = %s AND is_active = 1
        ORDER BY FIELD(rol, 'Lider', 'Sublider'), nombre ASC
        """
    cursor.execute(query, (cdp_id,))
    return cursor.fetchall() or []


def get_cdps_para_lideres(cursor: Cursor):
    """
    Retorna las Casas de Paz activas junto con el nombre de su red
    para los selectores de asignación en form_lider.html.
    """
    query = """
        SELECT c.id, c.codigo, c.direccion, r.nombre AS red_nombre
        FROM cdp c
        LEFT JOIN red r ON c.red_id = r.id
        WHERE c.is_active = 1
        ORDER BY c.codigo ASC
    """
    cursor.execute(query)
    return cursor.fetchall() or []


def insertar_lider(cursor: Cursor, nombre:str, apellido:str, telefono:str, rol:str, cdp_id:int):
    """
    Inserta un nuevo miembro del equipo de liderazgo en una Casa de Paz.
    """
    query = """
        INSERT INTO lider (nombre, apellido, telefono, rol, is_active, cdp_id)
        VALUES (%s, %s, %s, %s, 1, %s)
    """
    cursor.execute(query, (nombre.strip(), apellido.strip(), telefono.strip(), rol.strip(), cdp_id))
    return cursor.lastrowid


def obtener_lider_por_id(cursor: Cursor, lider_id:int):
    """
    Obtiene la ficha de un líder por su ID, con datos de su Casa y Red asociada.
    """
    query = """
        SELECT l.id, l.nombre, l.apellido, l.telefono, l.rol, l.is_active, l.cdp_id,
        c.codigo AS cdp_codigo, c.direccion AS cdp_direccion,
        r.nombre AS red_nombre
        FROM lider l
        LEFT JOIN cdp c ON l.cdp_id = c.id
        LEFT JOIN red r ON c.red_id = r.id
        WHERE l.id = %s
    """
    cursor.execute(query, (lider_id,))
    return cursor.fetchone()


def actualizar_lider(cursor: Cursor, lider_id:int, nombre:str, apellido:str, telefono:str, rol:str, cdp_id:int, is_active:int = None):
    """
    Actualiza la información personal, rol y Casa de Paz de un líder.
    """
    if is_active is not None:
        query = """
            UPDATE lider SET nombre = %s, apellido = %s, telefono = %s, rol = %s, cdp_id = %s, is_active = %s
            WHERE id = %s
        """
        cursor.execute(query, (nombre.strip(), apellido.strip(), telefono.strip(), rol.strip(), cdp_id, int(is_active), lider_id))
    else:
        query = """
            UPDATE lider SET nombre = %s, apellido = %s, telefono = %s, rol = %s, cdp_id = %s
            WHERE id = %s
        """
        cursor.execute(query, (nombre.strip(), apellido.strip(), telefono.strip(), rol.strip(), cdp_id, lider_id))
    return cursor.rowcount >= 0


def eliminar_pausar_lider(cursor: Cursor, lider_id: int) -> tuple[bool, str, str]:
    """
    Gestiona la baja de un líder con candado de integridad referencial:
    - Si tiene reportes asociados: BLOQUEA la eliminación física para evitar datos huérfanos
      en el historial ministerial, indicando que se debe poner en pausa.
    - Si NO tiene reportes asociados: Realiza eliminación física limpia.
    
    Retorna: (exito: bool, accion: 'bloqueada' | 'eliminado' | 'error', mensaje: str)
    """
    # 1. Verificar si el líder existe
    cursor.execute("SELECT id, nombre, apellido FROM lider WHERE id = %s", (lider_id,))
    lider = cursor.fetchone()
    if not lider:
        return False, 'error', "El líder no existe o ya fue eliminado."

    nombre_completo = f"{lider.get('nombre', '')} {lider.get('apellido', '')}".strip()

    # 2. Verificar si tiene reportes firmados
    cursor.execute("SELECT COUNT(*) AS total FROM reporte WHERE enviado_por_lider_id = %s", (lider_id,))
    total_reportes = cursor.fetchone()['total']

    if total_reportes > 0:
        return False, 'bloqueada', (
            f"No se puede eliminar al líder '{nombre_completo}' porque tiene {total_reportes} reporte(s) "
            f"registrado(s). Para evitar datos huérfanos y preservar el historial ministerial, "
            f"debes ponerlo en pausa en su lugar."
        )

    # 3. Sin historial -> Eliminación física limpia
    cursor.execute("DELETE FROM lider WHERE id = %s", (lider_id,))
    return True, 'eliminado', f"El líder '{nombre_completo}' ha sido eliminado exitosamente del sistema."


def toggle_estado_lider(cursor: Cursor, lider_id: int) -> tuple[bool, str, str]:
    """
    Alterna el estado is_active de un líder.
    Valida que la Casa de Paz asignada esté activa antes de permitir la reactivación.
    
    Retorna: (éxito: bool, acción: 'bloqueada' | 'reactivado' | 'pausado' | 'error', mensaje: str)
    """
    cursor.execute("""
        SELECT l.id, l.nombre, l.apellido, l.is_active, l.cdp_id, 
               c.codigo AS cdp_codigo, c.is_active AS cdp_is_active 
        FROM lider l 
        JOIN cdp c ON l.cdp_id = c.id 
        WHERE l.id = %s
    """, (lider_id,))
    lider = cursor.fetchone()

    if not lider:
        return False, 'error', "El líder no existe o no tiene Casa de Paz asignada."

    nombre_completo = f"{lider.get('nombre', '')} {lider.get('apellido', '')}".strip()
    cdp_codigo = lider.get('cdp_codigo', '')
    is_active = bool(lider.get('is_active', 0))
    cdp_is_active = bool(lider.get('cdp_is_active', 0))

    if not is_active:
        # Intento de reactivación: validar que la CDP asignada esté activa
        if not cdp_is_active:
            return (
                False, 
                'bloqueada', 
                f"No se puede reactivar al líder '{nombre_completo}' porque su Casa de Paz asignada ('{cdp_codigo}') se encuentra en pausa o inactiva. Debe reactivar la Casa primero o reasignar al líder a una Casa activa."
            )
        cursor.execute("UPDATE lider SET is_active = 1 WHERE id = %s", (lider_id,))
        return True, 'reactivado', f"El líder '{nombre_completo}' ha sido reactivado exitosamente."
    else:
        # Poner en pausa
        cursor.execute("UPDATE lider SET is_active = 0 WHERE id = %s", (lider_id,))
        return True, 'pausado', f"El líder '{nombre_completo}' ha sido pausado exitosamente."


def get_lideres_cdp_disponibles(cursor, cdp_id=None):
    """
    Retorna los usuarios con rol 'lider_cdp' activos que aún no tienen una Casa de Paz asignada,
    o el usuario actualmente asignado a la Casa de Paz cdp_id indicada (para edición).
    """
    if cdp_id:
        try:
            cdp_id_int = int(cdp_id)
        except (ValueError, TypeError):
            cdp_id_int = -1
        cursor.execute("""
            SELECT u.id, u.nombre, u.apellido, u.username
            FROM usuario u
            LEFT JOIN cdp c ON c.usuario_id = u.id
            WHERE u.tipo_usuario = 'lider_cdp' AND u.is_active = 1
              AND (c.id IS NULL OR c.id = %s)
            ORDER BY u.nombre, u.apellido
        """, (cdp_id_int,))
    else:
        cursor.execute("""
            SELECT u.id, u.nombre, u.apellido, u.username
            FROM usuario u
            LEFT JOIN cdp c ON c.usuario_id = u.id
            WHERE u.tipo_usuario = 'lider_cdp' AND u.is_active = 1
              AND c.id IS NULL
            ORDER BY u.nombre, u.apellido
        """)
    return cursor.fetchall() or []


