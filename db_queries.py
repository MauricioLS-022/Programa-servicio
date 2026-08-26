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
def get_metricas_generales(conn):
    """Query real de métricas generales de toda la iglesia."""
    cur = conn.cursor()

    # --- KPIs principales ---
    cur.execute("""
        SELECT
            COALESCE(SUM(nro_regulares + nro_niños + nro_visitas + nro_comprometidos), 0) AS total_asistencia,
            COALESCE(SUM(ofrendas), 0) AS ofrendas,
            COALESCE(SUM(confesiones), 0) AS conversiones,
            COUNT(DISTINCT cdp_id) AS reportes_enviados
        FROM reporte
    """)
    kpis = cur.fetchone()

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
    rows_tendencia = cur.fetchall() or []
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
            CONCAT(u.nombre, ' ', u.apellido) AS supervisor
        FROM red r
        LEFT JOIN cdp c ON c.red_id = r.id
        LEFT JOIN reporte rep ON rep.cdp_id = c.id
        LEFT JOIN usuario u ON r.supervisor_id = u.id
        GROUP BY r.id, r.nombre, u.nombre, u.apellido
        ORDER BY asistencia DESC
    """, (inicio_semana,))
    ranking = cur.fetchall()
    color_map = {
        'hebrón': 'hebron', 'cielos abiertos': 'hebron',
        'sur': 'sur',
        'central': 'central',
    }
    for r in ranking:
        r['color_class'] = color_map.get(r['nombre'].lower().strip(), 'default')

    # --- Alertas: casas sin reporte en 14+ días ---
    corte = hoy - timedelta(days=14)
    cur.execute("""
        SELECT
            c.codigo,
            CONCAT(c.anfitrion, '') AS nombre,
            r.nombre AS red,
            DATEDIFF(CURDATE(), MAX(rep.fecha)) AS dias_sin_reporte,
            CONCAT(l.nombre, ' ', l.apellido) AS lider,
            l.telefono
        FROM cdp c
        LEFT JOIN reporte rep ON rep.cdp_id = c.id
        LEFT JOIN red r ON c.red_id = r.id
        LEFT JOIN lider l ON l.cdp_id = c.id AND l.rol = 'Lider'
        GROUP BY c.id, c.codigo, c.anfitrion, r.nombre, l.nombre, l.apellido, l.telefono
        HAVING dias_sin_reporte > 14 OR dias_sin_reporte IS NULL
        ORDER BY dias_sin_reporte DESC
    """)
    alertas_raw = cur.fetchall()
    alertas = [
        {
            'nombre': a['nombre'],
            'codigo': a['codigo'],
            'red': a['red'] or '',
            'dias_sin_reporte': a['dias_sin_reporte'] if a['dias_sin_reporte'] else 999,
            'lider': a['lider'] or 'Sin asignar',
            'telefono': a['telefono'] or '',
        }
        for a in alertas_raw
    ]

    cur.close()

    return {
        'total_asistencia': int(kpis['total_asistencia']),
        'cumplimiento': cumplimiento,
        'ofrendas': float(kpis['ofrendas']),
        'conversiones': int(kpis['conversiones']),
        'total_casas': total_casas,
        'reportes_enviados': int(kpis['reportes_enviados']),
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
            CONCAT(u.nombre, ' ', u.apellido) AS supervisor
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
    cur.execute("""
        SELECT
            COUNT(DISTINCT c.id) AS casas_activas,
            COALESCE(SUM(rep.nro_regulares + rep.nro_niños + rep.nro_visitas + rep.nro_comprometidos), 0) AS asistencia_total,
            COALESCE(SUM(rep.nro_niños), 0) AS ninos,
            COALESCE(SUM(rep.ofrendas), 0) AS ofrendas,
            COUNT(DISTINCT CASE WHEN rep.fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) THEN rep.cdp_id END) AS casas_con_reporte
        FROM cdp c
        LEFT JOIN reporte rep ON rep.cdp_id = c.id
        WHERE c.red_id = %s
    """, (red_id,))
    kpis = cur.fetchone()
    casas_activas = int(kpis['casas_activas'])
    asistencia_total = int(kpis['asistencia_total'])
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
    hoy = date.today()
    cur.execute("""
        SELECT
            c.codigo,
            c.anfitrion,
            COALESCE(SUM(rep2.nro_regulares + rep2.nro_niños + rep2.nro_visitas + rep2.nro_comprometidos), 0) AS asistencia,
            MAX(rep.fecha) AS ultimo_reporte,
            COALESCE(SUM(rep2.nro_visitas), 0) AS visitas,
            CONCAT(l.nombre, ' ', l.apellido) AS lider,
            DATEDIFF(CURDATE(), MAX(rep.fecha)) AS dias_desde_reporte
        FROM cdp c
        LEFT JOIN reporte rep ON rep.cdp_id = c.id
        LEFT JOIN (
            SELECT cdp_id, nro_regulares, nro_niños, nro_visitas, nro_comprometidos
            FROM reporte
        ) rep2 ON rep2.cdp_id = c.id
        LEFT JOIN lider l ON l.cdp_id = c.id AND l.rol = 'Lider'
        WHERE c.red_id = %s
        GROUP BY c.id, c.codigo, c.anfitrion, l.nombre, l.apellido
        ORDER BY c.codigo
    """, (red_id,))
    casas_raw = cur.fetchall()

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
            'nombre': c['codigo'],  # código como nombre para la vista
            'codigo': c['codigo'],
            'asistencia': int(c['asistencia']),
            'estado': estado,
            'lider': c['lider'] or 'Sin asignar',
            'visitas': int(c['visitas']),
        })

    # --- Alertas zonal: casas en rojo ---
    alertas_zonal = [
        {
            'nombre': c['codigo'],
            'codigo': c['codigo'],
            'dias_sin_reporte': c['dias_desde_reporte'] if c['dias_desde_reporte'] else 999,
            'motivo': 'Sin reporte reciente' if c['dias_desde_reporte'] is None else f"{c['dias_desde_reporte']} días sin reporte",
            'lider': c['lider'] or 'Sin asignar',
            'telefono': '',
        }
        for c in casas_raw
        if c['dias_desde_reporte'] is None or c['dias_desde_reporte'] > 14
    ]

    # --- Top crecimiento: casa con mayor asistencia reciente ---
    top_growth = {}
    if casas:
        best = max(casas, key=lambda x: x['asistencia'])
        top_growth = {
            'nombre': best['nombre'],
            'codigo': best['codigo'],
            'tasa': f"+{best['asistencia']}",
            'visitas': best['visitas'],
            'lider': best['lider'],
        }

    # --- Supervisores de la red ---
    cur.execute("""
        SELECT
            CONCAT(u.nombre, ' ', u.apellido) AS nombre,
            u.tipo_usuario AS rol,
            u.telefono
        FROM usuario u
        WHERE u.tipo_usuario = 'supervisor' AND u.is_active = 1
    """)
    supervisores = cur.fetchall()

    cur.close()

    return {
        'nombre_red': nombre_red,
        'red_id': red_id,
        'supervisor': supervisor,
        'casas_activas': casas_activas,
        'asistencia_total': asistencia_total,
        'promedio_casa': promedio_casa,
        'ninos': int(kpis['ninos']),
        'ofrendas': float(kpis['ofrendas']),
        'distribucion': distribucion,
        'casas': casas,
        'alertas_zonal': alertas_zonal,
        'top_crecimiento': top_growth,
        'supervisores': supervisores,
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
        "SELECT nombre, apellido, rol, telefono FROM lider WHERE cdp_id = %s ORDER BY FIELD(rol, 'Lider', 'Sublider')",
        (cdp_id,),
    )
    lideres = cur.fetchall()
    lider = ''
    sublider = ''
    for l in lideres:
        if l['rol'] == 'Lider':
            lider = f"{l['nombre']} {l['apellido']}"
        elif l['rol'] == 'Sublider':
            sublider = f"{l['nombre']} {l['apellido']}"

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
    ultimo_reporte_por = ultimo['enviado_por_nombre'] if ultimo and ultimo['enviado_por_nombre'] else ''
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
            ofrendas AS ofrenda,
            observaciones
        FROM reporte
        WHERE cdp_id = %s
        ORDER BY fecha DESC
        LIMIT 8
    """, (cdp_id,))
    historial_raw = cur.fetchall()
    historial = [
        {
            'fecha': h['fecha'].strftime('%Y-%m-%d') if h['fecha'] else '',
            'asistencia': int(h['asistencia']),
            'ninos': int(h['ninos']),
            'visitas': int(h['visitas']),
            'ofrenda': float(h['ofrenda']),
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
    mini_raw = cur.fetchall()
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

    # --- Potencial de multiplicación: si hay más de 1 líder registrado ---
    potencial = len(lideres) > 1

    cur.close()

    return {
        'nombre_cdp': cdp['codigo'],  # código como nombre principal
        'codigo': cdp['codigo'],
        'lider': lider,
        'sublider': sublider,
        'anfitrion': cdp['anfitrion'] or '',
        'telefono_contacto': cdp['telefono'] or '',
        'direccion': cdp['direccion'] or '',
        'asistencia_ultimo': asistencia_ultimo,
        'promedio_historico': promedio_historico,
        'visitas': visitas,
        'conversiones': conversiones,
        'estado_reporte': estado_reporte,
        'ultimo_reporte_por': ultimo_reporte_por,
        'ultimo_reporte_fecha': ultimo_reporte_fecha,
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
            rep.ofrendas,
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
            'ofrendas': float(r['ofrendas'] or 0.0),
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

