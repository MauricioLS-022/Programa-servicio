"""
services/queries/reportes_queries.py - Consultas de reportes semanales.
"""
from datetime import date, timedelta, datetime
from pymysql.cursors import Cursor
from .helpers import formatear_hora, formatear_horario_cdp, _asistencia_fila, _ensure_currency_columns

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

        hr_ini = formatear_hora(r.get('hr_inicio'))
        hr_fin = formatear_hora(r.get('hr_fin'))

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
            'ofrendas_usd': float(r.get('ofrendas_usd') or 0.0),
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


def insertar_reporte(cursor, datos_reporte):
    """
    Inserta un nuevo registro en la tabla 'reporte'.
    Alineado con los nombres de campos enviados por generar_reporte.html.
    """
    _ensure_currency_columns(cursor)
    ofrendas_usd = float(datos_reporte.get('ofrendas_usd', 0.0) or 0.0)
    ofrendas_bs = float(datos_reporte.get('ofrendas_bs', 0.0) or 0.0)
    query = """
        INSERT INTO reporte (
            id, cdp_id, enviado_por_lider_id, fecha, hr_inicio, hr_fin,
            tema, nro_niños, nro_regulares, nro_visitas, nro_comprometidos,
            reconciliaciones, confesiones, ofrendas_usd, ofrendas_bs, cesta_amor, observaciones
        ) VALUES (
            UUID(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
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
        ofrendas_bs,
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

        hr_ini = formatear_hora(r.get('hr_inicio'))
        hr_fin = formatear_hora(r.get('hr_fin'))

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


def actualizar_reporte_cdp(cursor, reporte_id, cdp_id, datos_reporte):
    """
    Actualiza un registro de reporte existente perteneciente a la cdp_id dada.
    """
    _ensure_currency_columns(cursor)
    ofrendas_usd = float(datos_reporte.get('ofrendas_usd', 0.0) or 0.0)
    ofrendas_bs = float(datos_reporte.get('ofrendas_bs', 0.0) or 0.0)
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
        ofrendas_bs,
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


