"""
services/queries/metricas_queries.py - Consultas de agregación y métricas de dashboard.
"""
from datetime import date, timedelta, datetime
from pymysql.cursors import Cursor
from .helpers import (
    formatear_hora, formatear_horario_cdp, _asistencia_fila, _semana_label, formatear_fecha_corta,
    formatear_mes_nombre, _obtener_rango_periodo, _obtener_metadatos_periodo,
    _periodo_a_fecha, _ensure_currency_columns
)

def get_metricas_generales(conn, periodo='semana', include_alertas=True, mes=None, anio=None):
    """Query real de métricas generales de toda la iglesia según el período ('semana', 'mes', 'anio')."""
    cur = conn.cursor()
    import db_queries
    db_queries._ensure_currency_columns(cur)

    hoy = date.today()
    fecha_desde, fecha_hasta = _obtener_rango_periodo(periodo, mes=mes, anio=anio)
    periodo_meta = _obtener_metadatos_periodo(periodo, fecha_desde, fecha_hasta, mes=mes, anio=anio)

    # Si estamos en vista semanal y no hay reportes en los últimos 7 días calendario,
    # sincronizamos con la semana del último reporte recibido para no mostrar métricas vacías
    if periodo == 'semana':
        try:
            cur.execute("""
                SELECT COUNT(*) AS total_sem
                FROM reporte rep
                JOIN cdp c ON rep.cdp_id = c.id
                WHERE c.is_active = 1 AND rep.fecha BETWEEN %s AND %s
            """, (fecha_desde, fecha_hasta))
            sem_row = cur.fetchone()
            if not sem_row or sem_row.get('total_sem', 0) == 0:
                cur.execute("""
                    SELECT MAX(rep.fecha) AS max_fecha
                    FROM reporte rep
                    JOIN cdp c ON rep.cdp_id = c.id
                    WHERE c.is_active = 1 AND rep.fecha IS NOT NULL
                """)
                max_row = cur.fetchone()
                if max_row and max_row.get('max_fecha'):
                    max_f = max_row['max_fecha']
                    if hasattr(max_f, 'date'):
                        max_f = max_f.date()
                    elif isinstance(max_f, str):
                        try:
                            from datetime import date as d_cls
                            max_f = d_cls.fromisoformat(max_f[:10])
                        except Exception:
                            pass
                    if isinstance(max_f, date):
                        fecha_hasta = max_f
                        fecha_desde = max_f - timedelta(days=6)
                        periodo_meta = _obtener_metadatos_periodo(periodo, fecha_desde, fecha_hasta, mes=mes, anio=anio)
                        if fecha_hasta < hoy - timedelta(days=7):
                            periodo_meta['periodo_nombre'] = f"Semana {formatear_fecha_corta(fecha_desde)} - {formatear_fecha_corta(fecha_hasta)}"
        except Exception as e:
            print(f"[DB] Aviso comprobando última fecha de reportes: {e}")

    # --- KPIs principales (filtrados por el período analizado) ---
    try:
        cur.execute("""
            SELECT
                COALESCE(SUM(rep.nro_regulares + rep.nro_niños + rep.nro_visitas + rep.nro_comprometidos), 0) AS total_asistencia,
                COALESCE(SUM(rep.nro_regulares), 0) AS regulares,
                COALESCE(SUM(rep.nro_niños), 0) AS ninos,
                COALESCE(SUM(rep.nro_visitas), 0) AS visitas,
                COALESCE(SUM(rep.nro_comprometidos), 0) AS comprometidos,
                COALESCE(SUM(rep.ofrendas_usd), 0) AS ofrendas_usd,
                COALESCE(SUM(rep.ofrendas_bs), 0) AS ofrendas_bs,
                COALESCE(SUM(rep.confesiones), 0) AS conversiones,
                COALESCE(SUM(rep.reconciliaciones), 0) AS reconciliaciones,
                COALESCE(SUM(rep.cesta_amor), 0) AS cestas_amor,
                COALESCE(SUM(rep.nro_visitas), 0) AS total_visitas,
                COUNT(DISTINCT rep.cdp_id) AS reportes_enviados
            FROM reporte rep
            JOIN cdp c ON rep.cdp_id = c.id
            WHERE c.is_active = 1 AND rep.fecha BETWEEN %s AND %s
        """, (fecha_desde, fecha_hasta))
        kpis = cur.fetchone() or {}
    except Exception:
        kpis = {}

    # Total casas activas como base de cálculo
    cur.execute("SELECT COUNT(*) AS total FROM cdp WHERE is_active = 1")
    total_casas = cur.fetchone()['total']

    # Cumplimiento: casas activas con reporte en el período analizado / total casas activas
    con_reporte = int(kpis.get('reportes_enviados', 0) or 0)
    cumplimiento = round((con_reporte / total_casas * 100) if total_casas > 0 else 0)
    casas_pendientes = max(total_casas - con_reporte, 0)
    total_sin_reporte_7d = casas_pendientes

    # Lista de casas activas sin reporte en el período analizado
    cur.execute("""
        SELECT c.id, c.codigo
        FROM cdp c
        WHERE c.is_active = 1
          AND NOT EXISTS (
              SELECT 1 FROM reporte r
              WHERE r.cdp_id = c.id AND r.fecha BETWEEN %s AND %s
          )
        ORDER BY c.codigo
    """, (fecha_desde, fecha_hasta))
    faltantes_global = cur.fetchall() or []
    casas_sin_reporte_ids = [f['id'] for f in faltantes_global]
    casas_sin_reporte_codigos = [f['codigo'] for f in faltantes_global]

    # --- Distribución del período (coherente con total_asistencia y donut) ---
    distribucion = {
        'regulares': int(kpis.get('regulares', 0) or 0),
        'ninos': int(kpis.get('ninos', 0) or 0),
        'visitas': int(kpis.get('visitas', 0) or 0),
        'comprometidos': int(kpis.get('comprometidos', 0) or 0),
    }

    # --- Tendencia adaptada al período ---
    if periodo == 'anio':
        # Agrupación mensual en el año (rango continuo entre primer y último mes con reportes)
        cur.execute("""
            SELECT
                MONTH(rep.fecha) AS num_mes,
                COALESCE(SUM(rep.nro_regulares + rep.nro_niños + rep.nro_visitas + rep.nro_comprometidos), 0) AS asistencia
            FROM reporte rep
            JOIN cdp c ON rep.cdp_id = c.id
            WHERE c.is_active = 1 AND rep.fecha BETWEEN %s AND %s
            GROUP BY num_mes
            HAVING asistencia > 0
            ORDER BY num_mes ASC
        """, (fecha_desde, fecha_hasta))
        rows = cur.fetchall() or []
        asist_map = {int(r['num_mes']): int(r['asistencia'] or 0) for r in rows}
        meses_con_asistencia = [int(r['num_mes']) for r in rows if (r.get('asistencia') or 0) > 0]

        meses_nombres = ['', 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        meses_completos = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

        if meses_con_asistencia:
            min_mes = min(meses_con_asistencia)
            max_mes = max(meses_con_asistencia)
            tendencia = [
                {
                    'semana': meses_nombres[m],
                    'num_mes': m,
                    'asistencia': asist_map.get(m, 0),
                    'porcentaje': 0,
                    'fecha_completa': f"{meses_completos[m]} {fecha_desde.year}",
                }
                for m in range(min_mes, max_mes + 1)
            ]
        else:
            m_curr = fecha_desde.month if fecha_desde else hoy.month
            tendencia = [
                {
                    'semana': meses_nombres[m_curr],
                    'num_mes': m_curr,
                    'asistencia': 0,
                    'porcentaje': 0,
                    'fecha_completa': f"{meses_completos[m_curr]} {fecha_desde.year if fecha_desde else hoy.year}",
                }
            ]
        max_asistencia = max((item['asistencia'] for item in tendencia), default=0)
        for item in tendencia:
            item['porcentaje'] = round(item['asistencia'] / max_asistencia * 100) if max_asistencia > 0 else 0
    elif periodo == 'mes':
        # Agrupación semanal en el mes calendario analizado (Semanas 1 a 4/5)
        cur.execute("""
            SELECT
                CASE
                    WHEN DAYOFMONTH(rep.fecha) BETWEEN 1 AND 7 THEN 1
                    WHEN DAYOFMONTH(rep.fecha) BETWEEN 8 AND 14 THEN 2
                    WHEN DAYOFMONTH(rep.fecha) BETWEEN 15 AND 21 THEN 3
                    WHEN DAYOFMONTH(rep.fecha) BETWEEN 22 AND 28 THEN 4
                    ELSE 5
                END AS num_semana,
                COALESCE(SUM(rep.nro_regulares + rep.nro_niños + rep.nro_visitas + rep.nro_comprometidos), 0) AS asistencia
            FROM reporte rep
            JOIN cdp c ON rep.cdp_id = c.id
            WHERE c.is_active = 1 AND rep.fecha BETWEEN %s AND %s
            GROUP BY num_semana
            ORDER BY num_semana ASC
        """, (fecha_desde, fecha_hasta))
        semanas_map = {row['num_semana']: int(row['asistencia'] or 0) for row in (cur.fetchall() or [])}
        num_dias_mes = fecha_hasta.day
        total_semanas_mes = 5 if num_dias_mes > 28 else 4
        tendencia = []
        for w in range(1, total_semanas_mes + 1):
            dia_ini = 1 + (w - 1) * 7
            dia_fin = min(w * 7, num_dias_mes)
            d_ini = date(fecha_desde.year, fecha_desde.month, dia_ini)
            d_fin = date(fecha_desde.year, fecha_desde.month, dia_fin)
            tendencia.append({
                'semana': f"Sem {w}",
                'rango_fecha': f"{d_ini.strftime('%d')}-{formatear_fecha_corta(d_fin)}",
                'asistencia': semanas_map.get(w, 0),
                'porcentaje': 0,
                'fecha_completa': f"Semana {w} ({formatear_fecha_corta(d_ini)} - {formatear_fecha_corta(d_fin)})",
            })
        max_asistencia = max((item['asistencia'] for item in tendencia), default=0)
        for item in tendencia:
            item['porcentaje'] = round(item['asistencia'] / max_asistencia * 100) if max_asistencia > 0 else 0
    else:
        # Período semanal: Desglose individual de asistencia por cada Red en esta semana
        cur.execute("""
            SELECT
                r.id,
                r.nombre AS nombre_red,
                COALESCE(SUM(rep.nro_regulares + rep.nro_niños + rep.nro_visitas + rep.nro_comprometidos), 0) AS asistencia
            FROM red r
            LEFT JOIN cdp c ON c.red_id = r.id AND c.is_active = 1
            LEFT JOIN reporte rep ON rep.cdp_id = c.id AND rep.fecha BETWEEN %s AND %s
            GROUP BY r.id, r.nombre
            ORDER BY r.id ASC
        """, (fecha_desde, fecha_hasta))
        rows_tendencia = cur.fetchall() or []
        max_asistencia = max((int(r['asistencia'] or 0) for r in rows_tendencia), default=0)
        tendencia = [
            {
                'semana': r['nombre_red'],
                'asistencia': int(r['asistencia'] or 0),
                'porcentaje': round(int(r['asistencia'] or 0) / max_asistencia * 100) if max_asistencia > 0 else 0,
                'fecha_completa': f"{r['nombre_red']} · Esta semana",
            }
            for r in rows_tendencia
        ]
    promedio_tendencia = round(sum(item['asistencia'] for item in tendencia) / len(tendencia)) if tendencia else 0

    # --- Ranking de redes (Base: Casas activas, Ventana: período analizado) restringido al Top 3 ---
    cur.execute("""
        SELECT
            r.nombre AS nombre,
            COUNT(DISTINCT c.id) AS total_casas,
            COUNT(DISTINCT CASE WHEN rep.fecha BETWEEN %s AND %s THEN rep.cdp_id END) AS casas_reportadas,
            COALESCE(SUM(CASE WHEN rep.fecha BETWEEN %s AND %s THEN rep.nro_regulares + rep.nro_niños + rep.nro_visitas + rep.nro_comprometidos ELSE 0 END), 0) AS asistencia_semana,
            COALESCE(SUM(rep.nro_regulares + rep.nro_niños + rep.nro_visitas + rep.nro_comprometidos), 0) AS asistencia_total,
            ROUND(
                COUNT(DISTINCT CASE WHEN rep.fecha BETWEEN %s AND %s THEN rep.cdp_id END)
                / GREATEST(COUNT(DISTINCT c.id), 1) * 100
            ) AS cumplimiento,
            COALESCE(CONCAT(u.nombre, ' ', u.apellido), 'Sin supervisor') AS supervisor
        FROM red r
        LEFT JOIN cdp c ON c.red_id = r.id AND c.is_active = 1
        LEFT JOIN reporte rep ON rep.cdp_id = c.id
        LEFT JOIN usuario u ON r.supervisor_id = u.id
        GROUP BY r.id, r.nombre, u.nombre, u.apellido
        ORDER BY cumplimiento DESC, asistencia_semana DESC, asistencia_total DESC
    """, (fecha_desde, fecha_hasta, fecha_desde, fecha_hasta, fecha_desde, fecha_hasta))
    ranking = cur.fetchall() or []
    for r in ranking:
        n_clean = (r['nombre'] or '').lower().strip()
        if 'sur' in n_clean:
            r['color_class'] = 'sur'
        elif 'central' in n_clean:
            r['color_class'] = 'central'
        elif 'hebr' in n_clean or 'cielo' in n_clean:
            r['color_class'] = 'hebron'
        else:
            r['color_class'] = 'default'

        r['asistencia_semana'] = int(r.get('asistencia_semana', 0) or 0)
        r['asistencia_total'] = int(r.get('asistencia_total', 0) or 0)
        r['asistencia'] = r['asistencia_semana']
        r['casas_reportadas'] = int(r.get('casas_reportadas', 0) or 0)
        r['total_casas'] = int(r.get('total_casas', 0) or 0)
        r['cumplimiento'] = int(r.get('cumplimiento', 0) or 0)

    # Restringir ranking de redes al podio de los 3 primeros
    ranking = ranking[:3]

    # --- Alertas: casas activas sin reporte en 14+ días (umbral fijo por regla institucional) ---
    if include_alertas:
        cur.execute("""
            SELECT
                c.codigo,
                c.anfitrion AS nombre,
                r.nombre AS red,
                DATEDIFF(CURDATE(), MAX(rep.fecha)) AS dias_sin_reporte,
                COALESCE(
                    (SELECT CONCAT(l.nombre, ' ', l.apellido) FROM lider l WHERE l.cdp_id = c.id AND l.rol = 'Lider' LIMIT 1),
                    (SELECT CONCAT(l.nombre, ' ', l.apellido) FROM lider l WHERE l.cdp_id = c.id LIMIT 1),
                    'Sin asignar'
                ) AS lider,
                COALESCE(c.telefono, (SELECT l.telefono FROM lider l WHERE l.cdp_id = c.id AND l.telefono IS NOT NULL LIMIT 1), '') AS telefono
            FROM cdp c
            LEFT JOIN reporte rep ON rep.cdp_id = c.id
            LEFT JOIN red r ON c.red_id = r.id
            WHERE c.is_active = 1
            GROUP BY c.id, c.codigo, c.anfitrion, c.telefono, r.nombre
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
    else:
        alertas = []

    cur.close()

    return {
        'total_asistencia': int(kpis.get('total_asistencia', 0) or 0),
        'cumplimiento': cumplimiento,
        'ofrendas_usd': float(kpis.get('ofrendas_usd', 0.0) or 0.0),
        'ofrendas_bs': float(kpis.get('ofrendas_bs', 0.0) or 0.0),
        'conversiones': int(kpis.get('conversiones', 0) or 0),
        'reconciliaciones': int(kpis.get('reconciliaciones', 0) or 0),
        'cestas_amor': int(kpis.get('cestas_amor', 0) or 0),
        'total_visitas': int(kpis.get('total_visitas', 0) or 0),
        'total_casas': total_casas,
        'casas_con_reporte': con_reporte,
        'casas_pendientes': casas_pendientes,
        'total_sin_reporte_7d': total_sin_reporte_7d,
        'casas_sin_reporte_ids': casas_sin_reporte_ids,
        'casas_sin_reporte_codigos': casas_sin_reporte_codigos,
        'casas_sin_reporte_7d': casas_sin_reporte_codigos,
        'reportes_enviados': con_reporte,
        'distribucion': distribucion,
        'tendencia': tendencia,
        'tendencia_semanas': tendencia,
        'promedio_tendencia': promedio_tendencia,
        'ranking_redes': ranking,
        'alertas': alertas,
        'periodo': periodo,
        **periodo_meta,
    }


def get_metricas_red(conn, red_id, periodo='semana', mes=None, anio=None):
    """Query real de métricas para una red específica según el período ('semana', 'mes', 'anio')."""
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

    # --- Total casas activas de la red ---
    cur.execute("SELECT COUNT(*) AS total FROM cdp WHERE red_id = %s AND is_active = 1", (red_id,))
    casas_activas_row = cur.fetchone()
    casas_activas = int(casas_activas_row['total']) if casas_activas_row else 0

    # --- KPIs de la red (Base: Casas activas, Ventana: período analizado) ---
    hoy = date.today()
    fecha_desde, fecha_hasta = _obtener_rango_periodo(periodo, mes=mes, anio=anio)
    periodo_meta = _obtener_metadatos_periodo(periodo, fecha_desde, fecha_hasta, mes=mes, anio=anio)
    try:
        cur.execute("""
            SELECT
                COALESCE(SUM(rep.nro_regulares + rep.nro_niños + rep.nro_visitas + rep.nro_comprometidos), 0) AS asistencia_total,
                COALESCE(SUM(rep.nro_regulares), 0) AS regulares,
                COALESCE(SUM(rep.nro_niños), 0) AS ninos,
                COALESCE(SUM(rep.nro_visitas), 0) AS visitas,
                COALESCE(SUM(rep.nro_comprometidos), 0) AS comprometidos,
                COALESCE(SUM(rep.confesiones), 0) AS conversiones,
                COALESCE(SUM(rep.ofrendas_usd), 0) AS ofrendas_usd,
                COALESCE(SUM(rep.ofrendas_bs), 0) AS ofrendas_bs,
                COUNT(DISTINCT rep.cdp_id) AS casas_con_reporte
            FROM reporte rep
            JOIN cdp c ON rep.cdp_id = c.id
            WHERE c.red_id = %s AND c.is_active = 1 AND rep.fecha BETWEEN %s AND %s
        """, (red_id, fecha_desde, fecha_hasta))
        kpis = cur.fetchone() or {}
    except Exception:
        kpis = {}

    asistencia_total = int(kpis.get('asistencia_total', 0) or 0)
    promedio_casa = round(asistencia_total / casas_activas) if casas_activas > 0 else 0

    # --- Distribución consolidada de la red en el período activo ---
    distribucion = {
        'regulares': int(kpis.get('regulares', 0) or 0),
        'ninos': int(kpis.get('ninos', 0) or 0),
        'visitas': int(kpis.get('visitas', 0) or 0),
        'comprometidos': int(kpis.get('comprometidos', 0) or 0),
    }

    # --- Lista de casas con estado ---
    cur.execute("""
        SELECT
            c.id,
            c.codigo,
            c.anfitrion,
            c.telefono,
            c.is_active,
            COALESCE(SUM(CASE WHEN rep.fecha BETWEEN %s AND %s THEN rep.nro_regulares + rep.nro_niños + rep.nro_visitas + rep.nro_comprometidos ELSE 0 END), 0) AS asistencia_semana,
            COALESCE(SUM(CASE WHEN rep.fecha BETWEEN %s AND %s THEN rep.nro_visitas ELSE 0 END), 0) AS visitas_semana,
            COALESCE(SUM(rep.nro_regulares + rep.nro_niños + rep.nro_visitas + rep.nro_comprometidos), 0) AS asistencia_total_cdp,
            MAX(rep.fecha) AS ultimo_reporte,
            COALESCE(
                (SELECT CONCAT(l.nombre, ' ', l.apellido) FROM lider l WHERE l.cdp_id = c.id AND l.rol = 'Lider' LIMIT 1),
                (SELECT CONCAT(l.nombre, ' ', l.apellido) FROM lider l WHERE l.cdp_id = c.id LIMIT 1),
                'Sin asignar'
            ) AS lider,
            DATEDIFF(CURDATE(), MAX(rep.fecha)) AS dias_desde_reporte
        FROM cdp c
        LEFT JOIN reporte rep ON rep.cdp_id = c.id
        LEFT JOIN usuario u ON c.usuario_id = u.id
        WHERE c.red_id = %s
        GROUP BY c.id, c.codigo, c.anfitrion, c.telefono, c.is_active, u.nombre, u.apellido
        ORDER BY c.codigo
    """, (fecha_desde, fecha_hasta, fecha_desde, fecha_hasta, red_id))
    casas_raw = cur.fetchall() or []

    dias_limite = 30 if periodo == 'mes' else (365 if periodo == 'anio' else 7)
    casas = []
    for c in casas_raw:
        is_act = bool(c.get('is_active', 1)) if c.get('is_active') is not None else True
        dias = c['dias_desde_reporte']
        rep_periodo = (dias is not None and dias <= dias_limite)
        if not is_act:
            estado = 'pausada'
        elif rep_periodo:
            estado = 'verde'
        elif dias is not None and dias <= 14:
            estado = 'amarillo'
        else:
            estado = 'rojo'

        asist = int(c.get('asistencia_semana', 0) or 0)
        vis = int(c.get('visitas_semana', 0) or 0)

        casas.append({
            'id': c.get('id'),
            'nombre': c.get('anfitrion') or f"Casa {c['codigo']}",
            'codigo': c['codigo'],
            'asistencia': asist,
            'estado': estado,
            'is_active': is_act,
            'reporte_reciente_7d': (dias is not None and dias <= 7),
            'reporte_reciente_periodo': rep_periodo,
            'lider': c['lider'] or 'Sin asignar',
            'visitas': vis,
            'telefono': c.get('telefono') or '',
        })

    # --- Alertas zonal: solo casas activas con >14 días sin reporte (umbral fijo institucional) ---
    alertas_zonal = [
        {
            'nombre': c.get('anfitrion') or f"Casa {c['codigo']}",
            'codigo': c['codigo'],
            'dias_sin_reporte': c['dias_desde_reporte'] if c['dias_desde_reporte'] else 999,
            'motivo': 'Sin reporte reciente' if c['dias_desde_reporte'] is None else f"{c['dias_desde_reporte']} días sin reporte",
            'lider': c['lider'] or 'Sin asignar',
            'telefono': c.get('telefono') or '',
        }
        for c in casas_raw
        if bool(c.get('is_active', 1)) and (c['dias_desde_reporte'] is None or c['dias_desde_reporte'] > 14)
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

    # --- Cumplimiento de la red en el período analizado (Base: Casas activas) ---
    con_reporte = int(kpis.get('casas_con_reporte', 0) or 0)
    cumplimiento = round((con_reporte / casas_activas * 100) if casas_activas > 0 else 0)
    casas_pendientes = max(casas_activas - con_reporte, 0)
    total_sin_reporte_7d = casas_pendientes

    cur.execute("""
        SELECT c.id, c.codigo
        FROM cdp c
        WHERE c.red_id = %s AND c.is_active = 1
          AND NOT EXISTS (
              SELECT 1 FROM reporte r
              WHERE r.cdp_id = c.id AND r.fecha BETWEEN %s AND %s
          )
        ORDER BY c.codigo
    """, (red_id, fecha_desde, fecha_hasta))
    faltantes_red = cur.fetchall() or []
    casas_sin_reporte_ids = [f['id'] for f in faltantes_red]
    casas_sin_reporte_codigos = [f['codigo'] for f in faltantes_red]

    # --- Directorio de líderes de las Casas de Paz de esta red (solo Líderes titulares) ---
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
        WHERE c.red_id = %s AND l.is_active = 1 AND l.rol = 'Lider'
        ORDER BY c.codigo, l.nombre
    """, (red_id,))
    lideres_red = cur.fetchall() or []

    # --- Tendencia de asistencia en la red adaptada al período ---
    if periodo == 'anio':
        # Agrupación mensual en el año para la red (rango continuo entre primer y último mes con reportes)
        cur.execute("""
            SELECT
                MONTH(rep.fecha) AS num_mes,
                COALESCE(SUM(rep.nro_regulares + rep.nro_niños + rep.nro_visitas + rep.nro_comprometidos), 0) AS asistencia
            FROM reporte rep
            JOIN cdp c ON rep.cdp_id = c.id
            WHERE c.red_id = %s AND c.is_active = 1 AND rep.fecha BETWEEN %s AND %s
            GROUP BY num_mes
            HAVING asistencia > 0
            ORDER BY num_mes ASC
        """, (red_id, fecha_desde, fecha_hasta))
        rows = cur.fetchall() or []
        asist_map = {int(r['num_mes']): int(r['asistencia'] or 0) for r in rows}
        meses_con_asistencia = [int(r['num_mes']) for r in rows if (r.get('asistencia') or 0) > 0]

        meses_nombres = ['', 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        meses_completos = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

        if meses_con_asistencia:
            min_mes = min(meses_con_asistencia)
            max_mes = max(meses_con_asistencia)
            tendencia_red = [
                {
                    'semana': meses_nombres[m],
                    'num_mes': m,
                    'asistencia': asist_map.get(m, 0),
                    'porcentaje': 0,
                    'fecha_completa': f"{meses_completos[m]} {fecha_desde.year}",
                }
                for m in range(min_mes, max_mes + 1)
            ]
        else:
            m_curr = fecha_desde.month if fecha_desde else hoy.month
            tendencia_red = [
                {
                    'semana': meses_nombres[m_curr],
                    'num_mes': m_curr,
                    'asistencia': 0,
                    'porcentaje': 0,
                    'fecha_completa': f"{meses_completos[m_curr]} {fecha_desde.year if fecha_desde else hoy.year}",
                }
            ]
        max_asistencia = max((item['asistencia'] for item in tendencia_red), default=0)
        for item in tendencia_red:
            item['porcentaje'] = round(item['asistencia'] / max_asistencia * 100) if max_asistencia > 0 else 0
    elif periodo == 'mes':
        # Agrupación semanal en el mes calendario analizado (Semanas 1 a 4/5)
        cur.execute("""
            SELECT
                CASE
                    WHEN DAYOFMONTH(rep.fecha) BETWEEN 1 AND 7 THEN 1
                    WHEN DAYOFMONTH(rep.fecha) BETWEEN 8 AND 14 THEN 2
                    WHEN DAYOFMONTH(rep.fecha) BETWEEN 15 AND 21 THEN 3
                    WHEN DAYOFMONTH(rep.fecha) BETWEEN 22 AND 28 THEN 4
                    ELSE 5
                END AS num_semana,
                COALESCE(SUM(rep.nro_regulares + rep.nro_niños + rep.nro_visitas + rep.nro_comprometidos), 0) AS asistencia
            FROM reporte rep
            JOIN cdp c ON rep.cdp_id = c.id
            WHERE c.red_id = %s AND c.is_active = 1 AND rep.fecha BETWEEN %s AND %s
            GROUP BY num_semana
            ORDER BY num_semana ASC
        """, (red_id, fecha_desde, fecha_hasta))
        semanas_map = {row['num_semana']: int(row['asistencia'] or 0) for row in (cur.fetchall() or [])}
        num_dias_mes = fecha_hasta.day
        total_semanas_mes = 5 if num_dias_mes > 28 else 4
        tendencia_red = []
        for w in range(1, total_semanas_mes + 1):
            dia_ini = 1 + (w - 1) * 7
            dia_fin = min(w * 7, num_dias_mes)
            d_ini = date(fecha_desde.year, fecha_desde.month, dia_ini)
            d_fin = date(fecha_desde.year, fecha_desde.month, dia_fin)
            tendencia_red.append({
                'semana': f"Sem {w}",
                'rango_fecha': f"{d_ini.strftime('%d')}-{formatear_fecha_corta(d_fin)}",
                'asistencia': semanas_map.get(w, 0),
                'porcentaje': 0,
                'fecha_completa': f"Semana {w} ({formatear_fecha_corta(d_ini)} - {formatear_fecha_corta(d_fin)})",
            })
        max_asistencia = max((item['asistencia'] for item in tendencia_red), default=0)
        for item in tendencia_red:
            item['porcentaje'] = round(item['asistencia'] / max_asistencia * 100) if max_asistencia > 0 else 0
    else:
        # Período semanal: Desglose individual de asistencia por cada Casa de Paz en esta semana
        cur.execute("""
            SELECT
                c.id,
                c.codigo,
                c.anfitrion,
                COALESCE(SUM(rep.nro_regulares + rep.nro_niños + rep.nro_visitas + rep.nro_comprometidos), 0) AS asistencia
            FROM cdp c
            LEFT JOIN reporte rep ON rep.cdp_id = c.id AND rep.fecha BETWEEN %s AND %s
            WHERE c.red_id = %s AND c.is_active = 1
            GROUP BY c.id, c.codigo, c.anfitrion
            ORDER BY c.codigo ASC
        """, (fecha_desde, fecha_hasta, red_id))
        rows_tendencia = cur.fetchall() or []
        max_asistencia = max((int(r['asistencia'] or 0) for r in rows_tendencia), default=0)
        tendencia_red = [
            {
                'semana': r['codigo'],
                'asistencia': int(r['asistencia'] or 0),
                'porcentaje': round(int(r['asistencia'] or 0) / max_asistencia * 100) if max_asistencia > 0 else 0,
                'fecha_completa': f"{r['codigo']} - {r['anfitrion'] or 'Casa de Paz'}",
            }
            for r in rows_tendencia
        ]
    promedio_tendencia = round(sum(item['asistencia'] for item in tendencia_red) / len(tendencia_red)) if tendencia_red else 0

    # --- Actividad reciente de la red (últimos 5 reportes) ---
    cur.execute("""
        SELECT
            rep.id,
            rep.fecha,
            rep.tema,
            (rep.nro_regulares + rep.nro_niños + rep.nro_visitas + rep.nro_comprometidos) AS asistencia,
            c.codigo AS cdp_codigo,
            c.anfitrion AS cdp_nombre,
            COALESCE(
                (SELECT CONCAT(l.nombre, ' ', l.apellido) FROM lider l WHERE l.cdp_id = c.id AND l.rol = 'Lider' LIMIT 1),
                (SELECT CONCAT(l.nombre, ' ', l.apellido) FROM lider l WHERE l.cdp_id = c.id LIMIT 1),
                'Líder'
            ) AS lider_nombre
        FROM reporte rep
        JOIN cdp c ON rep.cdp_id = c.id
        WHERE c.red_id = %s AND c.is_active = 1
        ORDER BY rep.fecha DESC, rep.id DESC
        LIMIT 25
    """, (red_id,))
    actividad_rows = cur.fetchall() or []
    actividad_reciente = []
    vistos = set()
    avatar_classes = ['bg-primary-light text-primary', 'bg-secondary-light text-secondary']
    for act in actividad_rows:
        clave = (act.get('cdp_codigo'), str(act.get('fecha')))
        if clave in vistos:
            continue
        vistos.add(clave)
        lider_nom = act.get('lider_nombre') or 'Líder'
        partes_nom = lider_nom.split()
        ini = (partes_nom[0][0] + (partes_nom[-1][0] if len(partes_nom) > 1 else '')).upper() if partes_nom else 'LD'
        f_val = act.get('fecha')
        f_fmt = formatear_fecha_corta(f_val)
        if f_val and hasattr(f_val, 'year'):
            f_fmt = f"{f_fmt} {f_val.year}"
        elif f_val and isinstance(f_val, str) and len(f_val) >= 4:
            f_fmt = f"{f_fmt} {f_val[:4]}"
        
        actividad_reciente.append({
            'lider': lider_nom,
            'iniciales': ini,
            'avatar_class': avatar_classes[len(actividad_reciente) % len(avatar_classes)],
            'cdp_nombre': act.get('cdp_nombre') or f"Casa {act.get('cdp_codigo')}",
            'cdp_codigo': act.get('cdp_codigo') or '',
            'fecha_formateada': f_fmt,
            'asistencia': int(act.get('asistencia') or 0),
            'tema': act.get('tema') or '',
        })
        if len(actividad_reciente) >= 10:
            break

    cur.close()

    return {
        'nombre_red': nombre_red,
        'red_id': red_id,
        'supervisor': supervisor,
        'casas_activas': casas_activas,
        'asistencia_total': asistencia_total,
        'total_asistencia': asistencia_total,
        'promedio_casa': promedio_casa,
        'ninos': int(kpis.get('ninos', 0) or 0),
        'conversiones': int(kpis.get('conversiones', 0) or 0),
        'ofrendas_usd': float(kpis.get('ofrendas_usd', 0.0)) if kpis else 0.0,
        'ofrendas_bs': float(kpis.get('ofrendas_bs', 0.0)) if kpis else 0.0,
        'cumplimiento': cumplimiento,
        'casas_con_reporte': con_reporte,
        'casas_pendientes': casas_pendientes,
        'total_sin_reporte_7d': total_sin_reporte_7d,
        'casas_sin_reporte_ids': casas_sin_reporte_ids,
        'casas_sin_reporte_codigos': casas_sin_reporte_codigos,
        'casas_sin_reporte_7d': casas_sin_reporte_codigos,
        'distribucion': distribucion,
        'casas': casas,
        'alertas_zonal': alertas_zonal,
        'top_crecimiento': top_growth,
        'lideres_red': lideres_red,
        'tendencia': tendencia_red,
        'tendencia_semanas': tendencia_red,
        'promedio_tendencia': promedio_tendencia,
        'actividad_reciente': actividad_reciente,
        'periodo': periodo,
        **periodo_meta,
    }


def get_metricas_cdp(conn, cdp_id, periodo='semana'):
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

    hoy = date.today()
    hace_7_dias = hoy - timedelta(days=7)

    dias_desde_reporte = None
    reporte_al_dia = False
    if ultimo and ultimo.get('fecha'):
        u_fecha = ultimo['fecha']
        if isinstance(u_fecha, datetime):
            u_fecha = u_fecha.date()
        elif isinstance(u_fecha, str):
            try:
                u_fecha = datetime.strptime(u_fecha[:10], '%Y-%m-%d').date()
            except Exception:
                u_fecha = None

        if u_fecha:
            dias_desde_reporte = max(0, (hoy - u_fecha).days)
            reporte_al_dia = (dias_desde_reporte <= 7)

    asistencia_ultimo = _asistencia_fila(ultimo) if ultimo else 0
    estado_reporte = 'enviado' if reporte_al_dia else 'pendiente'
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
            'ofrendas_usd': float(h.get('ofrendas_usd') or 0.0),
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
    hr_inicio = formatear_hora(ultimo.get('hr_inicio')) if ultimo else ''
    hr_fin = formatear_hora(ultimo.get('hr_fin')) if ultimo else ''
    cesta_amor = bool(ultimo.get('cesta_amor')) if ultimo else False
    potencial = len(lideres) > 1

    cur.close()

    ofrendas_usd = float(ultimo.get('ofrendas_usd') or 0.0) if ultimo else 0.0
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
        'total_asistencia': asistencia_ultimo,
        'promedio_historico': promedio_historico,
        'visitas': visitas,
        'conversiones': conversiones,
        'ofrendas_usd': ofrendas_usd,
        'ofrendas_bs': ofrendas_bs,
        'estado_reporte': estado_reporte,
        'reporte_al_dia': reporte_al_dia,
        'dias_desde_reporte': dias_desde_reporte,
        'ultimo_reporte_reciente': reporte_al_dia,
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
        'ofrendas_usd_totales': ofrendas_usd_totales,
        'ofrendas_bs_totales': ofrendas_bs_totales,
        'visitas_totales': visitas_totales,
        'conversiones_totales': conversiones_totales,
        'reconciliaciones_totales': reconciliaciones_totales,
        'reporte_esta_semana': reporte_esta_semana,
        'dias_cierre_texto': dias_cierre_texto,
    }


