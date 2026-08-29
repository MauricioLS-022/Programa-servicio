"""
db_queries.py - Consultas reales a la base de datos para el dashboard.
Cada función recibe una conexión PyMySQL y retorna un dict con la
estructura exacta que espera el template dashboard_admin.html.

Si la consulta no retorna datos (tablas vacías), retorna valores por
defecto (0, listas vacías) en lugar de mock.
"""

from datetime import date, timedelta


def get_usuarios(conn, search='', rol='', page=1, per_page=10):
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
        SELECT id, username, nombre, apellido, tipo_usuario AS rol, is_active
        FROM usuario u
        {where_clause}
        ORDER BY nombre IS NULL, nombre, apellido IS NULL, apellido, username
        LIMIT %s OFFSET %s
    """, [*params, per_page, offset])
    usuarios = cur.fetchall() or []

    cur.execute("SELECT COUNT(*) AS total FROM usuario WHERE is_active = 1")
    total_activos = int(cur.fetchone()['total'])
    cur.close()
    return usuarios, total, total_activos


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
        SELECT l.id, l.nombre, l.apellido, l.rol, l.telefono,
               c.id AS cdp_id, c.codigo AS cdp_nombre, r.id AS red_id,
               r.nombre AS red_nombre
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


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------
def _asistencia_fila(row):
    """Calcula la asistencia total de un registro de reporte."""
    return (
        (row.get('nro_regulares') or 0)
        + (row.get('nro_niños') or 0)
        + (row.get('nro_visitas') or 0)
        + (row.get('nro_comprometidos') or 0)
    )


def _semana_label(fecha):
    """Retorna una etiqueta legible tipo 'Sem 1' a partir de una fecha."""
    dia = fecha.day
    if dia <= 7:
        return 'Sem 1'
    elif dia <= 14:
        return 'Sem 2'
    elif dia <= 21:
        return 'Sem 3'
    else:
        return 'Sem 4'


# ---------------------------------------------------------------------------
# Vista General
# ---------------------------------------------------------------------------
def _ensure_currency_columns(cursor):
    """Asegura que las columnas ofrendas_bs y ofrendas_usd existan en la tabla reporte si la BD está disponible."""
    try:
        cursor.execute("SHOW COLUMNS FROM reporte LIKE 'ofrendas_bs'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE reporte ADD COLUMN ofrendas_bs DECIMAL(10,2) NOT NULL DEFAULT 0.00")
        cursor.execute("SHOW COLUMNS FROM reporte LIKE 'ofrendas_usd'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE reporte ADD COLUMN ofrendas_usd DECIMAL(10,2) NOT NULL DEFAULT 0.00")
    except Exception:
        pass


def get_metricas_generales(conn):
    """Query real de métricas generales de toda la iglesia."""
    cur = conn.cursor()
    _ensure_currency_columns(cur)

    # --- KPIs principales ---
    try:
        cur.execute("""
            SELECT
                COALESCE(SUM(nro_regulares + nro_niños + nro_visitas + nro_comprometidos), 0) AS total_asistencia,
                COALESCE(SUM(ofrendas_usd), 0) AS ofrendas_usd,
                COALESCE(SUM(ofrendas_bs), 0) AS ofrendas_bs,
                COALESCE(SUM(confesiones), 0) AS conversiones,
                COALESCE(SUM(reconciliaciones), 0) AS reconciliaciones,
                COALESCE(SUM(cesta_amor), 0) AS cestas_amor,
                COALESCE(SUM(nro_visitas), 0) AS total_visitas,
                COUNT(DISTINCT cdp_id) AS reportes_enviados
            FROM reporte
        """)
        kpis = cur.fetchone() or {}
    except Exception:
        kpis = {}

    cur.execute("SELECT COUNT(*) AS total FROM cdp")
    total_casas = cur.fetchone()['total']

    # Cumplimiento: casas con reporte esta semana / total casas
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    cur.execute(
        "SELECT COUNT(DISTINCT cdp_id) AS con_reporte FROM reporte WHERE fecha >= %s",
        (inicio_semana,),
    )
    con_reporte = cur.fetchone()['con_reporte']
    cumplimiento = round((con_reporte / total_casas * 100) if total_casas > 0 else 0)

    # --- Distribución del último reporte (el más reciente global) ---
    cur.execute("""
        SELECT nro_regulares, nro_niños, nro_visitas, nro_comprometidos
        FROM reporte ORDER BY fecha DESC LIMIT 1
    """)
    dist_row = cur.fetchone()
    distribucion = {
        'regulares': dist_row['nro_regulares'] if dist_row else 0,
        'ninos': dist_row['nro_niños'] if dist_row else 0,
        'visitas': dist_row['nro_visitas'] if dist_row else 0,
        'comprometidos': dist_row['nro_comprometidos'] if dist_row else 0,
    }

    # --- Tendencia: últimos 8 meses agrupados ---
    cur.execute("""
        SELECT
            DATE_FORMAT(fecha, '%Y-%m') AS mes,
            SUM(nro_regulares + nro_niños + nro_visitas + nro_comprometidos) AS asistencia
        FROM reporte
        GROUP BY mes
        ORDER BY mes DESC
        LIMIT 8
    """)
    rows_tendencia = list(cur.fetchall() or [])
    rows_tendencia.reverse()
    max_asistencia = max((r['asistencia'] for r in rows_tendencia), default=1) or 1
    tendencia = [
        {
            'semana': r['mes'],
            'asistencia': int(r['asistencia']) if r['asistencia'] else 0,
            'porcentaje': round(int(r['asistencia']) / max_asistencia * 100) if max_asistencia > 0 else 0,
        }
        for r in rows_tendencia
    ]

    # --- Ranking de redes ---
    cur.execute("""
        SELECT
            r.nombre AS nombre,
            COUNT(DISTINCT c.id) AS total_casas,
            COALESCE(SUM(rep.nro_regulares + rep.nro_niños + rep.nro_visitas + rep.nro_comprometidos), 0) AS asistencia,
            ROUND(
                COUNT(DISTINCT CASE WHEN rep.fecha >= %s THEN rep.cdp_id END)
                / GREATEST(COUNT(DISTINCT c.id), 1) * 100
            ) AS cumplimiento,
            COALESCE(CONCAT(u.nombre, ' ', u.apellido), 'Sin supervisor') AS supervisor
        FROM red r
        LEFT JOIN cdp c ON c.red_id = r.id
        LEFT JOIN reporte rep ON rep.cdp_id = c.id
        LEFT JOIN usuario u ON r.supervisor_id = u.id
        GROUP BY r.id, r.nombre, u.nombre, u.apellido
        ORDER BY asistencia DESC
    """, (inicio_semana,))
    ranking = cur.fetchall() or []
    color_map = {
        'hebrón': 'hebron', 'cielos abiertos': 'hebron',
        'sur': 'sur',
        'central': 'central',
    }
    for r in ranking:
        r['color_class'] = color_map.get((r['nombre'] or '').lower().strip(), 'default')

    # --- Alertas: casas sin reporte en 14+ días ---
    cur.execute("""
        SELECT
            c.codigo,
            c.anfitrion AS nombre,
            r.nombre AS red,
            DATEDIFF(CURDATE(), MAX(rep.fecha)) AS dias_sin_reporte,
            COALESCE(
                (SELECT CONCAT(l.nombre, ' ', l.apellido) FROM lider l WHERE l.cdp_id = c.id AND l.rol = 'Lider' LIMIT 1),
                (SELECT CONCAT(l.nombre, ' ', l.apellido) FROM lider l WHERE l.cdp_id = c.id LIMIT 1),
                CONCAT(u.nombre, ' ', u.apellido),
                'Sin asignar'
            ) AS lider,
            COALESCE(c.telefono, (SELECT l.telefono FROM lider l WHERE l.cdp_id = c.id AND l.telefono IS NOT NULL LIMIT 1), '') AS telefono
        FROM cdp c
        LEFT JOIN reporte rep ON rep.cdp_id = c.id
        LEFT JOIN red r ON c.red_id = r.id
        LEFT JOIN usuario u ON c.usuario_id = u.id
        GROUP BY c.id, c.codigo, c.anfitrion, c.telefono, r.nombre, u.nombre, u.apellido
        HAVING dias_sin_reporte > 14 OR dias_sin_reporte IS NULL
        ORDER BY dias_sin_reporte DESC
    """)
    alertas_raw = cur.fetchall() or []
    alertas = [
        {
            'nombre': a['nombre'] or a['codigo'],
            'codigo': a['codigo'],
            'red': a['red'] or '',
            'dias_sin_reporte': a['dias_sin_reporte'] if a['dias_sin_reporte'] else 999,
            'motivo': 'Sin reporte reciente' if a['dias_sin_reporte'] is None else f"{a['dias_sin_reporte']} días sin reporte",
            'lider': a['lider'] or 'Sin asignar',
            'telefono': a['telefono'] or '',
        }
        for a in alertas_raw
    ]

    cur.close()

    return {
        'total_asistencia': int(kpis.get('total_asistencia', 0) or 0),
        'cumplimiento': cumplimiento,
        'ofrendas': float(kpis.get('ofrendas_usd', kpis.get('ofrendas', 0.0)) or 0.0),
        'ofrendas_usd': float(kpis.get('ofrendas_usd', kpis.get('ofrendas', 0.0)) or 0.0),
        'ofrendas_bs': float(kpis.get('ofrendas_bs', 0.0) or 0.0),
        'conversiones': int(kpis.get('conversiones', 0) or 0),
        'reconciliaciones': int(kpis.get('reconciliaciones', 0) or 0),
        'cestas_amor': int(kpis.get('cestas_amor', 0) or 0),
        'total_visitas': int(kpis.get('total_visitas', 0) or 0),
        'total_casas': total_casas,
        'casas_con_reporte': con_reporte,
        'reportes_enviados': con_reporte,
        'distribucion': distribucion,
        'tendencia_semanas': tendencia,
        'ranking_redes': ranking,
        'alertas': alertas,
    }


# ---------------------------------------------------------------------------
# Vista Red
# ---------------------------------------------------------------------------
def get_metricas_red(conn, red_id):
    """Query real de métricas para una red específica."""
    cur = conn.cursor()

    # --- Datos de la red + supervisor ---
    cur.execute("""
        SELECT
            r.nombre AS nombre_red,
            COALESCE(CONCAT(u.nombre, ' ', u.apellido), 'Sin asignar') AS supervisor
        FROM red r
        LEFT JOIN usuario u ON r.supervisor_id = u.id
        WHERE r.id = %s
    """, (red_id,))
    red_info = cur.fetchone()
    if not red_info:
        cur.close()
        return None
    nombre_red = red_info['nombre_red']
    supervisor = red_info['supervisor'] or ''

    # --- KPIs de la red ---
    try:
        cur.execute("""
            SELECT
                COUNT(DISTINCT c.id) AS casas_activas,
                COALESCE(SUM(rep.nro_regulares + rep.nro_niños + rep.nro_visitas + rep.nro_comprometidos), 0) AS asistencia_total,
                COALESCE(SUM(rep.nro_niños), 0) AS ninos,
                COALESCE(SUM(rep.confesiones), 0) AS conversiones,
                COALESCE(SUM(rep.ofrendas_usd), 0) AS ofrendas_usd,
                COALESCE(SUM(rep.ofrendas_bs), 0) AS ofrendas_bs,
                COUNT(DISTINCT CASE WHEN rep.fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) THEN rep.cdp_id END) AS casas_con_reporte
            FROM cdp c
            LEFT JOIN reporte rep ON rep.cdp_id = c.id
            WHERE c.red_id = %s
        """, (red_id,))
        kpis = cur.fetchone()
    except Exception:
        kpis = {}
    casas_activas = int(kpis['casas_activas']) if kpis else 0
    asistencia_total = int(kpis['asistencia_total']) if kpis else 0
    promedio_casa = round(asistencia_total / casas_activas) if casas_activas > 0 else 0

    # --- Distribución (del último reporte de la red) ---
    cur.execute("""
        SELECT rep.nro_regulares, rep.nro_niños, rep.nro_visitas, rep.nro_comprometidos
        FROM reporte rep
        JOIN cdp c ON rep.cdp_id = c.id
        WHERE c.red_id = %s
        ORDER BY rep.fecha DESC LIMIT 1
    """, (red_id,))
    dist_row = cur.fetchone()
    distribucion = {
        'regulares': dist_row['nro_regulares'] if dist_row else 0,
        'ninos': dist_row['nro_niños'] if dist_row else 0,
        'visitas': dist_row['nro_visitas'] if dist_row else 0,
        'comprometidos': dist_row['nro_comprometidos'] if dist_row else 0,
    }

    # --- Lista de casas con estado ---
    cur.execute("""
        SELECT
            c.id,
            c.codigo,
            c.anfitrion,
            c.telefono,
            COALESCE(SUM(rep.nro_regulares + rep.nro_niños + rep.nro_visitas + rep.nro_comprometidos), 0) AS asistencia,
            MAX(rep.fecha) AS ultimo_reporte,
            COALESCE(SUM(rep.nro_visitas), 0) AS visitas,
            COALESCE(
                (SELECT CONCAT(l.nombre, ' ', l.apellido) FROM lider l WHERE l.cdp_id = c.id AND l.rol = 'Lider' LIMIT 1),
                (SELECT CONCAT(l.nombre, ' ', l.apellido) FROM lider l WHERE l.cdp_id = c.id LIMIT 1),
                CONCAT(u.nombre, ' ', u.apellido),
                'Sin asignar'
            ) AS lider,
            DATEDIFF(CURDATE(), MAX(rep.fecha)) AS dias_desde_reporte
        FROM cdp c
        LEFT JOIN reporte rep ON rep.cdp_id = c.id
        LEFT JOIN usuario u ON c.usuario_id = u.id
        WHERE c.red_id = %s
        GROUP BY c.id, c.codigo, c.anfitrion, c.telefono, u.nombre, u.apellido
        ORDER BY c.codigo
    """, (red_id,))
    casas_raw = cur.fetchall() or []

    casas = []
    for c in casas_raw:
        dias = c['dias_desde_reporte']
        if dias is None or dias > 14:
            estado = 'rojo'
        elif dias > 7:
            estado = 'amarillo'
        else:
            estado = 'verde'
        casas.append({
            'nombre': f"{c['codigo']} - {c['anfitrion']}" if c.get('anfitrion') else c['codigo'],
            'codigo': c['codigo'],
            'asistencia': int(c['asistencia']),
            'estado': estado,
            'lider': c['lider'] or 'Sin asignar',
            'visitas': int(c['visitas']),
            'telefono': c.get('telefono') or '',
        })

    # --- Alertas zonal: casas en rojo ---
    alertas_zonal = [
        {
            'nombre': c['codigo'],
            'codigo': c['codigo'],
            'dias_sin_reporte': c['dias_desde_reporte'] if c['dias_desde_reporte'] else 999,
            'motivo': 'Sin reporte reciente' if c['dias_desde_reporte'] is None else f"{c['dias_desde_reporte']} días sin reporte",
            'lider': c['lider'] or 'Sin asignar',
            'telefono': c.get('telefono') or '',
        }
        for c in casas_raw
        if c['dias_desde_reporte'] is None or c['dias_desde_reporte'] > 14
    ]

    # --- Top crecimiento: casa con mayor asistencia reciente ---
    top_growth = {}
    if casas:
        best = max(casas, key=lambda x: (x['asistencia'], x['visitas']))
        top_growth = {
            'nombre': best['nombre'],
            'codigo': best['codigo'],
            'tasa': f"+{best['asistencia']}",
            'visitas': best['visitas'],
            'lider': best['lider'],
        }

    # --- Cumplimiento semanal de la red ---
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    cur.execute("""
        SELECT COUNT(DISTINCT rep.cdp_id) AS con_reporte
        FROM reporte rep
        JOIN cdp c ON rep.cdp_id = c.id
        WHERE c.red_id = %s AND rep.fecha >= %s
    """, (red_id, inicio_semana))
    con_reporte_row = cur.fetchone()
    con_reporte = int(con_reporte_row['con_reporte']) if con_reporte_row else 0
    cumplimiento = round((con_reporte / casas_activas * 100) if casas_activas > 0 else 0)
    casas_pendientes = max(casas_activas - con_reporte, 0)

    # --- Directorio de líderes de las Casas de Paz de esta red ---
    cur.execute("""
        SELECT
            l.id,
            CONCAT(l.nombre, ' ', l.apellido) AS nombre,
            l.rol,
            COALESCE(l.telefono, c.telefono, '') AS telefono,
            c.codigo AS cdp_codigo,
            c.anfitrion AS cdp_anfitrion
        FROM lider l
        JOIN cdp c ON l.cdp_id = c.id
        WHERE c.red_id = %s AND l.is_active = 1
        ORDER BY c.codigo, FIELD(l.rol, 'Lider', 'Sublider'), l.nombre
    """, (red_id,))
    lideres_red = cur.fetchall() or []

    cur.close()

    return {
        'nombre_red': nombre_red,
        'red_id': red_id,
        'supervisor': supervisor,
        'casas_activas': casas_activas,
        'asistencia_total': asistencia_total,
        'promedio_casa': promedio_casa,
        'ninos': int(kpis['ninos']) if kpis else 0,
        'conversiones': int(kpis.get('conversiones', 0) or 0) if kpis else 0,
        'ofrendas': float(kpis.get('ofrendas_usd', kpis.get('ofrendas', 0.0))) if kpis else 0.0,
        'ofrendas_usd': float(kpis.get('ofrendas_usd', kpis.get('ofrendas', 0.0))) if kpis else 0.0,
        'ofrendas_bs': float(kpis.get('ofrendas_bs', 0.0)) if kpis else 0.0,
        'cumplimiento': cumplimiento,
        'casas_con_reporte': con_reporte,
        'casas_pendientes': casas_pendientes,
        'distribucion': distribucion,
        'casas': casas,
        'alertas_zonal': alertas_zonal,
        'top_crecimiento': top_growth,
        'lideres_red': lideres_red,
    }


# ---------------------------------------------------------------------------
# Vista Casa de Paz
# ---------------------------------------------------------------------------
def get_metricas_cdp(conn, cdp_id):
    """Query real de métricas para una Casa de Paz específica."""
    cur = conn.cursor()

    # --- Datos del CDP ---
    cur.execute("SELECT * FROM cdp WHERE id = %s", (cdp_id,))
    cdp = cur.fetchone()
    if not cdp:
        cur.close()
        return None

    # --- Líder y sublíder ---
    cur.execute(
        "SELECT nombre, apellido, rol, telefono FROM lider WHERE cdp_id = %s ORDER BY FIELD(rol, 'Lider', 'Sublider'), id",
        (cdp_id,),
    )
    lideres = cur.fetchall() or []
    lider = ''
    sublider = ''
    telefono_lider = ''
    for l in lideres:
        if l['rol'] == 'Lider':
            lider = f"{l['nombre']} {l['apellido']}".strip()
            if l.get('telefono'):
                telefono_lider = l['telefono']
        elif l['rol'] == 'Sublider':
            sublider = f"{l['nombre']} {l['apellido']}".strip()
            if not telefono_lider and l.get('telefono'):
                telefono_lider = l['telefono']

    if not lider and lideres:
        lider = f"{lideres[0]['nombre']} {lideres[0]['apellido']}".strip()
        if lideres[0].get('telefono'):
            telefono_lider = lideres[0]['telefono']

    if not lider and cdp.get('usuario_id'):
        cur.execute("SELECT nombre, apellido FROM usuario WHERE id = %s", (cdp['usuario_id'],))
        u = cur.fetchone()
        if u:
            lider = f"{u['nombre']} {u['apellido']}".strip()

    telefono_contacto = cdp.get('telefono') or telefono_lider or ''

    # --- Último reporte ---
    cur.execute("""
        SELECT r.*, CONCAT(l.nombre, ' ', l.apellido) AS enviado_por_nombre
        FROM reporte r
        LEFT JOIN lider l ON r.enviado_por_lider_id = l.id
        WHERE r.cdp_id = %s
        ORDER BY r.fecha DESC
        LIMIT 1
    """, (cdp_id,))
    ultimo = cur.fetchone()

    asistencia_ultimo = _asistencia_fila(ultimo) if ultimo else 0
    estado_reporte = 'enviado' if ultimo else 'pendiente'
    ultimo_reporte_por = (ultimo.get('enviado_por_nombre') if ultimo else None) or lider or 'Líder encargado'
    ultimo_reporte_fecha = ultimo['fecha'].strftime('%d %b %Y') if ultimo and ultimo['fecha'] else ''
    visitas = ultimo['nro_visitas'] if ultimo else 0
    conversiones = ultimo['confesiones'] if ultimo else 0

    distribucion = {
        'regulares': ultimo['nro_regulares'] if ultimo else 0,
        'ninos': ultimo['nro_niños'] if ultimo else 0,
        'visitas': ultimo['nro_visitas'] if ultimo else 0,
        'comprometidos': ultimo['nro_comprometidos'] if ultimo else 0,
    }

    # --- Promedio histórico ---
    cur.execute(
        "SELECT AVG(nro_regulares + nro_niños + nro_visitas + nro_comprometidos) AS promedio FROM reporte WHERE cdp_id = %s",
        (cdp_id,),
    )
    promedio_row = cur.fetchone()
    promedio_historico = round(promedio_row['promedio']) if promedio_row and promedio_row['promedio'] else 0

    # --- Historial últimos 8 reportes ---
    cur.execute("""
        SELECT
            fecha,
            (nro_regulares + nro_niños + nro_visitas + nro_comprometidos) AS asistencia,
            nro_niños AS ninos,
            nro_visitas AS visitas,
            COALESCE(ofrendas_usd, 0) AS ofrenda,
            COALESCE(ofrendas_usd, 0) AS ofrendas_usd,
            COALESCE(ofrendas_bs, 0) AS ofrendas_bs,
            observaciones
        FROM reporte
        WHERE cdp_id = %s
        ORDER BY fecha DESC
        LIMIT 8
    """, (cdp_id,))
    historial_raw = cur.fetchall() or []
    historial = [
        {
            'fecha': h['fecha'].strftime('%Y-%m-%d') if h['fecha'] else '',
            'asistencia': int(h['asistencia']),
            'ninos': int(h['ninos']),
            'visitas': int(h['visitas']),
            'ofrenda': float(h.get('ofrendas_usd') or h.get('ofrenda') or 0.0),
            'ofrendas_usd': float(h.get('ofrendas_usd') or h.get('ofrenda') or 0.0),
            'ofrendas_bs': float(h.get('ofrendas_bs') or 0.0),
            'observaciones': h['observaciones'] or '',
        }
        for h in historial_raw
    ]

    # --- Mini histórico (últimos 4 para barras) ---
    cur.execute("""
        SELECT
            fecha,
            (nro_regulares + nro_niños + nro_visitas + nro_comprometidos) AS asistencia
        FROM reporte
        WHERE cdp_id = %s
        ORDER BY fecha DESC
        LIMIT 4
    """, (cdp_id,))
    mini_raw = list(cur.fetchall() or [])
    mini_raw.reverse()
    max_mini = max((int(m['asistencia']) for m in mini_raw), default=1) or 1
    mini_historico = [
        {
            'fecha': m['fecha'].strftime('%d %b') if m['fecha'] else '',
            'asistencia': int(m['asistencia']),
            'altura': round(int(m['asistencia']) / max_mini * 100),
        }
        for m in mini_raw
    ]

    ultimo_tema = (ultimo.get('tema') if ultimo else None) or 'Sin tema registrado'
    hr_inicio = str(ultimo.get('hr_inicio'))[:5] if ultimo and ultimo.get('hr_inicio') else ''
    hr_fin = str(ultimo.get('hr_fin'))[:5] if ultimo and ultimo.get('hr_fin') else ''
    cesta_amor = bool(ultimo.get('cesta_amor')) if ultimo else False
    potencial = len(lideres) > 1

    cur.close()

    ofrendas_usd = float(ultimo.get('ofrendas_usd') or ultimo.get('ofrenda') or 0.0) if ultimo else 0.0
    ofrendas_bs = float(ultimo.get('ofrendas_bs') or 0.0) if ultimo else 0.0

    return {
        'nombre_cdp': f"{cdp['codigo']} - {cdp['anfitrion']}" if cdp.get('anfitrion') else cdp['codigo'],
        'codigo': cdp['codigo'],
        'lider': lider,
        'sublider': sublider,
        'anfitrion': cdp['anfitrion'] or '',
        'telefono_contacto': telefono_contacto,
        'direccion': cdp['direccion'] or '',
        'asistencia_ultimo': asistencia_ultimo,
        'promedio_historico': promedio_historico,
        'visitas': visitas,
        'conversiones': conversiones,
        'ofrendas_usd': ofrendas_usd,
        'ofrendas_bs': ofrendas_bs,
        'estado_reporte': estado_reporte,
        'ultimo_reporte_por': ultimo_reporte_por,
        'ultimo_reporte_fecha': ultimo_reporte_fecha,
        'ultimo_tema': ultimo_tema,
        'hr_inicio': hr_inicio,
        'hr_fin': hr_fin,
        'cesta_amor': cesta_amor,
        'potencial_multiplicacion': potencial,
        'distribucion': distribucion,
        'historial': historial,
        'mini_historico': mini_historico,
    }


def get_reportes(conn, search='', red_id='', cdp_id='', fecha_desde='', fecha_hasta='', supervisor_red_id=None, page=1, per_page=10):
    """Obtiene reportes paginados con filtros de búsqueda, red, casa y rango de fechas."""
    offset = (page - 1) * per_page
    filters = []
    params = []

    if search:
        filters.append("(CONCAT(COALESCE(l.nombre, ''), ' ', COALESCE(l.apellido, '')) LIKE %s OR c.codigo LIKE %s OR c.anfitrion LIKE %s OR rep.tema LIKE %s)")
        search_value = f"%{search}%"
        params.extend([search_value, search_value, search_value, search_value])
    if red_id:
        filters.append("c.red_id = %s")
        params.append(red_id)
    if cdp_id:
        filters.append("rep.cdp_id = %s")
        params.append(cdp_id)
    if fecha_desde:
        filters.append("rep.fecha >= %s")
        params.append(fecha_desde)
    if fecha_hasta:
        filters.append("rep.fecha <= %s")
        params.append(fecha_hasta)
    if supervisor_red_id is not None:
        filters.append("c.red_id = %s")
        params.append(supervisor_red_id)

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ''
    cur = conn.cursor()
    cur.execute(f"""
        SELECT COUNT(*) AS total
        FROM reporte rep
        LEFT JOIN cdp c ON c.id = rep.cdp_id
        LEFT JOIN red r ON r.id = c.red_id
        LEFT JOIN lider l ON l.id = rep.enviado_por_lider_id
        {where_clause}
    """, params)
    total = int(cur.fetchone()['total'])

    cur.execute(f"""
        SELECT
            rep.id,
            rep.fecha,
            rep.hr_inicio,
            rep.hr_fin,
            rep.nro_regulares,
            rep.nro_niños,
            rep.nro_visitas,
            rep.nro_comprometidos,
            (rep.nro_regulares + rep.nro_niños + rep.nro_visitas + rep.nro_comprometidos) AS asistencia,
            rep.reconciliaciones,
            rep.confesiones,
            rep.cesta_amor,
            rep.tema,
            rep.observaciones,
            COALESCE(rep.ofrendas_usd, 0) AS ofrendas,
            COALESCE(rep.ofrendas_usd, 0) AS ofrendas_usd,
            COALESCE(rep.ofrendas_bs, 0) AS ofrendas_bs,
            rep.cdp_id,
            c.codigo AS cdp_codigo,
            c.anfitrion AS cdp_anfitrion,
            r.id AS red_id,
            r.nombre AS red_nombre,
            rep.enviado_por_lider_id,
            CONCAT(COALESCE(l.nombre, ''), ' ', COALESCE(l.apellido, '')) AS lider_nombre,
            l.nombre AS lider_nombre_solo,
            l.apellido AS lider_apellido
        FROM reporte rep
        LEFT JOIN cdp c ON c.id = rep.cdp_id
        LEFT JOIN red r ON r.id = c.red_id
        LEFT JOIN lider l ON l.id = rep.enviado_por_lider_id
        {where_clause}
        ORDER BY rep.fecha DESC, rep.id DESC
        LIMIT %s OFFSET %s
    """, [*params, per_page, offset])
    reportes_raw = cur.fetchall() or []

    meses_abr = {1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'}
    reportes = []
    for r in reportes_raw:
        fecha_obj = r['fecha']
        if hasattr(fecha_obj, 'strftime'):
            fecha_iso = fecha_obj.strftime('%Y-%m-%d')
            fecha_formateada = f"{fecha_obj.day} {meses_abr.get(fecha_obj.month, '')} {fecha_obj.year}"
        else:
            fecha_iso = str(fecha_obj or '')
            fecha_formateada = fecha_iso

        nombre_lider = (r['lider_nombre'] or '').strip() or 'Sin Asignar'
        partes = nombre_lider.split()
        if len(partes) >= 2:
            iniciales = (partes[0][0] + partes[1][0]).upper()
        elif len(partes) == 1 and partes[0]:
            iniciales = partes[0][:2].upper()
        else:
            iniciales = 'VN'

        hr_ini = str(r['hr_inicio'] or '')
        hr_fin = str(r['hr_fin'] or '')
        if len(hr_ini) >= 5 and ':' in hr_ini:
            hr_ini = hr_ini[:5]
        if len(hr_fin) >= 5 and ':' in hr_fin:
            hr_fin = hr_fin[:5]

        cdp_nombre = r['cdp_codigo'] or r['cdp_anfitrion'] or f"CDP #{r['cdp_id']}"
        if r['cdp_anfitrion'] and r['cdp_codigo']:
            cdp_nombre = f"{r['cdp_codigo']} - {r['cdp_anfitrion']}"

        cesta_desc = 'Sí' if r['cesta_amor'] else 'No'

        reportes.append({
            'id': r['id'],
            'fecha': fecha_iso,
            'fecha_formateada': fecha_formateada,
            'lider_nombre': nombre_lider,
            'iniciales': iniciales,
            'avatar_class': 'bg-primary-light text-primary',
            'cdp_id': r['cdp_id'],
            'cdp_nombre': cdp_nombre,
            'red_id': r['red_id'],
            'red_nombre': r['red_nombre'] or '',
            'hr_inicio': hr_ini,
            'hr_fin': hr_fin,
            'nro_regulares': int(r['nro_regulares'] or 0),
            'nro_niños': int(r['nro_niños'] or 0),
            'nro_visitas': int(r['nro_visitas'] or 0),
            'nro_comprometidos': int(r['nro_comprometidos'] or 0),
            'asistencia': int(r['asistencia'] or 0),
            'reconciliaciones': int(r['reconciliaciones'] or 0),
            'confesiones': int(r['confesiones'] or 0),
            'ofrendas': float(r.get('ofrendas_usd') or r.get('ofrendas') or 0.0),
            'ofrendas_usd': float(r.get('ofrendas_usd') or r.get('ofrendas') or 0.0),
            'ofrendas_bs': float(r.get('ofrendas_bs') or 0.0),
            'cesta_amor': r['cesta_amor'],
            'cesta_amor_desc': cesta_desc,
            'tema': r['tema'] or '',
            'observaciones': r['observaciones'] or '',
        })

    cur.execute("SELECT id, nombre FROM red ORDER BY nombre")
    redes = cur.fetchall() or []
    cur.execute("SELECT id, codigo, anfitrion, red_id FROM cdp ORDER BY codigo")
    casas_raw = cur.fetchall() or []
    casas = []
    for c in casas_raw:
        casas.append({
            'id': c['id'],
            'nombre': f"{c['codigo']} - {c['anfitrion']}" if c['anfitrion'] else c['codigo'],
            'codigo': c['codigo'],
            'red_id': c['red_id'],
        })
    cur.close()
    return reportes, total, redes, casas

# ---------------------------------------------------------------------------
# FUNCIONALIDAD PARA GENERAR REPORTES
# ---------------------------------------------------------------------------

def obtener_cdp_por_usuario(cursor, usuario_id):
    """Obtiene la Casa de Paz asignada a un usuario específico."""
    query = "SELECT id, codigo, anfitrion, telefono, direccion, red_id FROM cdp WHERE usuario_id = %s"
    cursor.execute(query, (usuario_id,))
    return cursor.fetchone()


def obtener_lideres_por_cdp(cursor, cdp_id):
    """Obtiene todos los líderes asociados a una Casa de Paz."""
    query = "SELECT id, nombre, apellido, rol, telefono FROM lider WHERE cdp_id = %s ORDER BY FIELD(rol, 'Lider', 'Sublider'), nombre ASC"
    cursor.execute(query, (cdp_id,))
    return cursor.fetchall() or []


def insertar_reporte(cursor, datos_reporte):
    """
    Inserta un nuevo registro en la tabla 'reporte'.
    Alineado con los nombres de campos enviados por generar_reporte.html.
    """
    _ensure_currency_columns(cursor)
    ofrendas_usd = float(datos_reporte.get('ofrendas_usd', datos_reporte.get('ofrendas', 0.0)) or 0.0)
    ofrendas_bs = float(datos_reporte.get('ofrendas_bs', 0.0) or 0.0)
    try:
        query = """
            INSERT INTO reporte (
                id, cdp_id, enviado_por_lider_id, fecha, hr_inicio, hr_fin,
                tema, nro_niños, nro_regulares, nro_visitas, nro_comprometidos,
                reconciliaciones, confesiones, ofrendas, ofrendas_usd, ofrendas_bs, cesta_amor, observaciones
            ) VALUES (
                UUID(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        params = (
            datos_reporte['cdp_id'],
            datos_reporte.get('lider_id') or None,
            datos_reporte['fecha'],
            datos_reporte['hr_inicio'],
            datos_reporte['hr_fin'],
            datos_reporte['tema'],
            datos_reporte.get('nro_ninos', 0),
            datos_reporte.get('nro_regulares', 0),
            datos_reporte.get('nro_visitas', 0),
            datos_reporte.get('nro_comprometidos', 0),
            datos_reporte.get('reconciliaciones', 0),
            datos_reporte.get('confesiones', 0),
            ofrendas_usd,
            ofrendas_usd,
            ofrendas_bs,
            1 if datos_reporte.get('cesta_amor') else 0,
            datos_reporte.get('observaciones', '')
        )
        cursor.execute(query, params)
    except Exception:
        query = """
            INSERT INTO reporte (
                id, cdp_id, enviado_por_lider_id, fecha, hr_inicio, hr_fin,
                tema, nro_niños, nro_regulares, nro_visitas, nro_comprometidos,
                reconciliaciones, confesiones, ofrendas, cesta_amor, observaciones
            ) VALUES (
                UUID(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        params = (
            datos_reporte['cdp_id'],
            datos_reporte.get('lider_id') or None,
            datos_reporte['fecha'],
            datos_reporte['hr_inicio'],
            datos_reporte['hr_fin'],
            datos_reporte['tema'],
            datos_reporte.get('nro_ninos', 0),
            datos_reporte.get('nro_regulares', 0),
            datos_reporte.get('nro_visitas', 0),
            datos_reporte.get('nro_comprometidos', 0),
            datos_reporte.get('reconciliaciones', 0),
            datos_reporte.get('confesiones', 0),
            ofrendas_usd,
            1 if datos_reporte.get('cesta_amor') else 0,
            datos_reporte.get('observaciones', '')
        )
        cursor.execute(query, params)


def obtener_reportes_por_cdp(cursor, cdp_id):
    """
    Obtiene todos los reportes registrados para una Casa de Paz específica,
    ordenados de forma descendente por fecha.
    """
    query = """
        SELECT
            r.id,
            r.fecha,
            r.hr_inicio,
            r.hr_fin,
            r.tema,
            r.nro_regulares,
            r.nro_niños,
            r.nro_visitas,
            r.nro_comprometidos,
            (r.nro_regulares + r.nro_niños + r.nro_visitas + r.nro_comprometidos) AS asistencia,
            r.reconciliaciones,
            r.confesiones,
            COALESCE(r.ofrendas_usd, 0) AS ofrendas_usd,
            COALESCE(r.ofrendas_bs, 0) AS ofrendas_bs,
            r.cesta_amor,
            r.observaciones,
            r.cdp_id,
            r.enviado_por_lider_id,
            CONCAT(COALESCE(l.nombre, ''), ' ', COALESCE(l.apellido, '')) AS lider_nombre,
            l.rol AS lider_rol
        FROM reporte r
        LEFT JOIN lider l ON r.enviado_por_lider_id = l.id
        WHERE r.cdp_id = %s
        ORDER BY r.fecha DESC, r.id DESC
    """
    cursor.execute(query, (cdp_id,))
    reportes_raw = cursor.fetchall() or []

    meses_abr = {1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'}
    reportes = []
    for r in reportes_raw:
        fecha_obj = r['fecha']
        if hasattr(fecha_obj, 'strftime'):
            fecha_iso = fecha_obj.strftime('%Y-%m-%d')
            fecha_formateada = f"{fecha_obj.day} {meses_abr.get(fecha_obj.month, '')} {fecha_obj.year}"
        else:
            fecha_iso = str(fecha_obj or '')
            fecha_formateada = fecha_iso

        nombre_lider = (r['lider_nombre'] or '').strip() or 'Líder Encargado'
        partes = nombre_lider.split()
        if len(partes) >= 2:
            iniciales = (partes[0][0] + partes[1][0]).upper()
        elif len(partes) == 1 and partes[0]:
            iniciales = partes[0][:2].upper()
        else:
            iniciales = 'CDP'

        hr_ini = str(r['hr_inicio'] or '')[:5] if r['hr_inicio'] else ''
        hr_fin = str(r['hr_fin'] or '')[:5] if r['hr_fin'] else ''

        ofrendas_usd = float(r.get('ofrendas_usd') or 0.0)
        ofrendas_bs = float(r.get('ofrendas_bs') or 0.0)

        reportes.append({
            'id': str(r['id']),
            'fecha': fecha_iso,
            'fecha_formateada': fecha_formateada,
            'hr_inicio': hr_ini,
            'hr_fin': hr_fin,
            'tema': r['tema'] or 'Sin tema registrado',
            'nro_regulares': int(r['nro_regulares'] or 0),
            'nro_niños': int(r['nro_niños'] or 0),
            'nro_visitas': int(r['nro_visitas'] or 0),
            'nro_comprometidos': int(r['nro_comprometidos'] or 0),
            'asistencia': int(r['asistencia'] or 0),
            'reconciliaciones': int(r['reconciliaciones'] or 0),
            'confesiones': int(r['confesiones'] or 0),
            'ofrendas': ofrendas_usd,
            'ofrendas_usd': ofrendas_usd,
            'ofrendas_bs': ofrendas_bs,
            'cesta_amor': 1 if r['cesta_amor'] else 0,
            'cesta_amor_desc': 'Sí' if r['cesta_amor'] else 'No',
            'observaciones': r['observaciones'] or '',
            'cdp_id': r['cdp_id'],
            'enviado_por_lider_id': r['enviado_por_lider_id'],
            'lider_nombre': nombre_lider,
            'iniciales': iniciales,
        })
    return reportes


def obtener_metricas_lider_cdp(cursor, cdp_id):
    """
    Obtiene las estadísticas consolidadas para el dashboard de una Casa de Paz.
    """
    try:
        query = """
            SELECT
                COUNT(*) AS total_reportes,
                COALESCE(AVG(nro_regulares + nro_niños + nro_visitas + nro_comprometidos), 0) AS asistencia_promedio,
                COALESCE(SUM(ofrendas_usd), 0) AS ofrendas_usd_totales,
                COALESCE(SUM(ofrendas_bs), 0) AS ofrendas_bs_totales,
                COALESCE(SUM(nro_visitas), 0) AS visitas_totales,
                COALESCE(SUM(confesiones), 0) AS conversiones_totales,
                COALESCE(SUM(reconciliaciones), 0) AS reconciliaciones_totales,
                MAX(fecha) AS ultimo_reporte_fecha
            FROM reporte
            WHERE cdp_id = %s
        """
        cursor.execute(query, (cdp_id,))
        row = cursor.fetchone() or {}
    except Exception:
        row = {}

    total_reportes = int(row.get('total_reportes', 0) or 0)
    asistencia_promedio = round(float(row.get('asistencia_promedio', 0) or 0))
    ofrendas_usd_totales = float(row.get('ofrendas_usd_totales', 0.0) or 0.0)
    ofrendas_bs_totales = float(row.get('ofrendas_bs_totales', 0.0) or 0.0)
    ofrendas_totales = ofrendas_usd_totales
    visitas_totales = int(row.get('visitas_totales', 0) or 0)
    conversiones_totales = int(row.get('conversiones_totales', 0) or 0)
    reconciliaciones_totales = int(row.get('reconciliaciones_totales', 0) or 0)

    # Verificar si ya se envió el reporte de la semana actual (desde lunes)
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    cursor.execute(
        "SELECT COUNT(*) AS count_semana FROM reporte WHERE cdp_id = %s AND fecha >= %s",
        (cdp_id, inicio_semana)
    )
    res_semana = cursor.fetchone() or {}
    reporte_esta_semana = int(res_semana.get('count_semana', 0) or 0) > 0

    # Días hasta el próximo domingo de cierre
    dias_hasta_domingo = (6 - hoy.weekday()) % 7
    if dias_hasta_domingo == 0:
        dias_cierre_texto = "Cierra hoy a las 6:00 PM"
    elif dias_hasta_domingo == 1:
        dias_cierre_texto = "Próximo cierre: Mañana"
    else:
        dias_cierre_texto = f"Próximo cierre: {dias_hasta_domingo} días"

    return {
        'total_reportes': total_reportes,
        'asistencia_promedio': asistencia_promedio,
        'ofrendas_totales': ofrendas_totales,
        'ofrendas_usd_totales': ofrendas_usd_totales,
        'ofrendas_bs_totales': ofrendas_bs_totales,
        'visitas_totales': visitas_totales,
        'conversiones_totales': conversiones_totales,
        'reconciliaciones_totales': reconciliaciones_totales,
        'reporte_esta_semana': reporte_esta_semana,
        'dias_cierre_texto': dias_cierre_texto,
    }


def actualizar_reporte_cdp(cursor, reporte_id, cdp_id, datos_reporte):
    """
    Actualiza un registro de reporte existente perteneciente a la cdp_id dada.
    """
    _ensure_currency_columns(cursor)
    ofrendas_usd = float(datos_reporte.get('ofrendas_usd', datos_reporte.get('ofrendas', 0.0)) or 0.0)
    ofrendas_bs = float(datos_reporte.get('ofrendas_bs', 0.0) or 0.0)
    try:
        query = """
            UPDATE reporte SET
                enviado_por_lider_id = %s,
                fecha = %s,
                hr_inicio = %s,
                hr_fin = %s,
                tema = %s,
                nro_niños = %s,
                nro_regulares = %s,
                nro_visitas = %s,
                nro_comprometidos = %s,
                reconciliaciones = %s,
                confesiones = %s,
                ofrendas = %s,
                ofrendas_usd = %s,
                ofrendas_bs = %s,
                cesta_amor = %s,
                observaciones = %s
            WHERE id = %s AND cdp_id = %s
        """
        params = (
            datos_reporte.get('lider_id') or None,
            datos_reporte['fecha'],
            datos_reporte['hr_inicio'],
            datos_reporte['hr_fin'],
            datos_reporte['tema'],
            datos_reporte.get('nro_ninos', 0),
            datos_reporte.get('nro_regulares', 0),
            datos_reporte.get('nro_visitas', 0),
            datos_reporte.get('nro_comprometidos', 0),
            datos_reporte.get('reconciliaciones', 0),
            datos_reporte.get('confesiones', 0),
            ofrendas_usd,
            ofrendas_usd,
            ofrendas_bs,
            1 if datos_reporte.get('cesta_amor') else 0,
            datos_reporte.get('observaciones', ''),
            str(reporte_id),
            cdp_id
        )
        cursor.execute(query, params)
        return cursor.rowcount > 0
    except Exception:
        query = """
            UPDATE reporte SET
                enviado_por_lider_id = %s,
                fecha = %s,
                hr_inicio = %s,
                hr_fin = %s,
                tema = %s,
                nro_niños = %s,
                nro_regulares = %s,
                nro_visitas = %s,
                nro_comprometidos = %s,
                reconciliaciones = %s,
                confesiones = %s,
                ofrendas = %s,
                cesta_amor = %s,
                observaciones = %s
            WHERE id = %s AND cdp_id = %s
        """
        params = (
            datos_reporte.get('lider_id') or None,
            datos_reporte['fecha'],
            datos_reporte['hr_inicio'],
            datos_reporte['hr_fin'],
            datos_reporte['tema'],
            datos_reporte.get('nro_ninos', 0),
            datos_reporte.get('nro_regulares', 0),
            datos_reporte.get('nro_visitas', 0),
            datos_reporte.get('nro_comprometidos', 0),
            datos_reporte.get('reconciliaciones', 0),
            datos_reporte.get('confesiones', 0),
            ofrendas_usd,
            1 if datos_reporte.get('cesta_amor') else 0,
            datos_reporte.get('observaciones', ''),
            str(reporte_id),
            cdp_id
        )
        cursor.execute(query, params)
        return cursor.rowcount > 0


def eliminar_reporte_cdp(cursor, reporte_id, cdp_id):
    """
    Elimina un reporte verificando que pertenezca a la CDP especificada.
    """
    query = "DELETE FROM reporte WHERE id = %s AND cdp_id = %s"
    cursor.execute(query, (str(reporte_id), cdp_id))
    return cursor.rowcount > 0