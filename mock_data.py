"""
mock_data.py - Datos de demostración para el dashboard y navegación sin base de datos.
Se usan cuando MOCK_MODE está activado o cuando la base de datos no está disponible.
Garantiza coherencia relacional estricta entre Redes, Casas de Paz, Líderes, Supervisores y Reportes.
"""
import urllib.parse
import re
from datetime import date, timedelta, datetime


def formatear_fecha_corta(fecha_val) -> str:
    """Formatea una fecha como fecha corta legible en español (ej. '28 Ago', '04 Sep')."""
    if not fecha_val:
        return ''
    meses_abr = {
        1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
    }
    if isinstance(fecha_val, str):
        f_str = fecha_val.strip()
        try:
            fecha_val = date.fromisoformat(f_str[:10])
        except Exception:
            for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y'):
                try:
                    fecha_val = datetime.strptime(f_str[:10], fmt).date()
                    break
                except Exception:
                    continue
            else:
                return f_str
    if hasattr(fecha_val, 'day') and hasattr(fecha_val, 'month'):
        return f"{fecha_val.day:02d} {meses_abr.get(fecha_val.month, '')}"
    return str(fecha_val)


def get_redes_demo():
    """Lista de redes para los selectores del filtro y vistas de estructura."""
    return [
        {
            'id': 1,
            'nombre': 'Red Hebrón',
            'supervisor': 'Pedro González',
            'supervisor_id': 'ca58cfc6-8337-11f1-8217-2016d8516279',
            'telefono': '+58 414 111 2233',
            'is_active': 1,
        },
        {
            'id': 2,
            'nombre': 'Red Sur',
            'supervisor': 'María López',
            'supervisor_id': 'mock-sup-2',
            'telefono': '+58 414 222 3344',
            'is_active': 1,
        },
        {
            'id': 3,
            'nombre': 'Red Central',
            'supervisor': 'Carlos Ramírez',
            'supervisor_id': 'mock-sup-3',
            'telefono': '+58 414 333 4455',
            'is_active': 1,
        },
    ]


def get_casas_demo():
    """Lista de casas de paz para los selectores del filtro y vista de estructura."""
    return [
        {
            'id': 1,
            'nombre': 'Casa Bethel',
            'codigo': 'HEB-001',
            'red_id': 1,
            'red_nombre': 'Red Hebrón',
            'supervisor': 'Pedro González',
            'anfitrion': 'David Gómez y Elena Ríos',
            'direccion': 'Calle 12 #18-45, sector El Carmen',
            'lider': 'Juan Carlos Pérez',
            'usuario_username': 'jperez',
            'usuario_nombre': 'Juan Carlos Pérez',
            'lider_id': '1d4f7c99-7d51-11f1-bf9e-2016d8516279',
            'telefono': '+58 412 123 4567',
            'asistencia': 18,
            'is_active': 1,
            'estado': 'activa',
            'tiene_reporte_7d': True,
            'horario': 'Miércoles · 7:00 PM'
        },
        {
            'id': 2,
            'nombre': 'Casa de Oración Sur',
            'codigo': 'SUR-001',
            'red_id': 2,
            'red_nombre': 'Red Sur',
            'supervisor': 'María López',
            'anfitrion': 'María López',
            'direccion': 'Av. Principal #45, sector Sur',
            'lider': 'Elena Pérez',
            'usuario_username': 'elena_p',
            'usuario_nombre': 'Elena Pérez',
            'lider_id': 'mock-leader-2',
            'telefono': '+58 414 987 6543',
            'asistencia': 14,
            'is_active': 1,
            'estado': 'pendiente',
            'tiene_reporte_7d': False,
            'horario': 'Miércoles · 7:00 PM'
        },
        {
            'id': 3,
            'nombre': 'Casa Nueva Vida',
            'codigo': 'CEN-001',
            'red_id': 3,
            'red_nombre': 'Red Central',
            'supervisor': 'Carlos Ramírez',
            'anfitrion': 'Carlos Ramírez',
            'direccion': 'Carrera 8 #22-10, Centro',
            'lider': 'Andrés Soler',
            'usuario_username': 'asoler',
            'usuario_nombre': 'Andrés Soler',
            'lider_id': 'mock-asoler',
            'telefono': '+58 424 567 8901',
            'asistencia': 22,
            'is_active': 1,
            'estado': 'pendiente',
            'tiene_reporte_7d': False,
            'horario': 'Jueves · 7:30 PM'
        },
        {
            'id': 4,
            'nombre': 'Casa Luz',
            'codigo': 'HEB-002',
            'red_id': 1,
            'red_nombre': 'Red Hebrón',
            'supervisor': 'Pedro González',
            'anfitrion': 'Pedro González',
            'direccion': 'Calle 5 #9-14, sector Las Flores',
            'lider': 'Mateo Rodríguez',
            'usuario_username': 'mateo_r',
            'usuario_nombre': 'Mateo Rodríguez',
            'lider_id': 'mock-leader-4',
            'telefono': '+58 416 345 6789',
            'asistencia': 12,
            'is_active': 1,
            'estado': 'activa',
            'tiene_reporte_7d': True,
            'horario': 'Viernes · 7:00 PM'
        },
    ]


def get_mock_usuarios():
    """Usuarios de demostración para la vista administrativa y autenticación."""
    return [
        {
            'id': '702f2129-7d4e-11f1-bf9e-2016d8516279',
            'username': 'admin',
            'nombre': 'Mateo',
            'apellido': 'Rodríguez',
            'rol': 'admin',
            'email': 'admin@vinonuevo.org',
            'is_active': 1
        },
        {
            'id': 'ca58cfc6-8337-11f1-8217-2016d8516279',
            'username': 'supervisor',
            'nombre': 'Pedro',
            'apellido': 'González',
            'rol': 'supervisor',
            'email': 'supervisor@vinonuevo.org',
            'is_active': 1
        },
        {
            'id': '1d4f7c99-7d51-11f1-bf9e-2016d8516279',
            'username': 'lider',
            'nombre': 'Juan Carlos',
            'apellido': 'Pérez',
            'rol': 'lider_cdp',
            'email': 'lider@vinonuevo.org',
            'is_active': 1
        },
        {
            'id': 'mock-asoler',
            'username': 'asoler',
            'nombre': 'Andrés',
            'apellido': 'Soler',
            'rol': 'lider_cdp',
            'email': 'asoler@vinonuevo.org',
            'is_active': 1
        },
        {
            'id': 'mock-sup-2',
            'username': 'mlopez',
            'nombre': 'María',
            'apellido': 'López',
            'rol': 'supervisor',
            'email': 'mlopez@vinonuevo.org',
            'is_active': 1
        },
    ]


def get_mock_lideres():
    """Líderes de demostración para el directorio administrativo y de supervisión."""
    return [
        {
            'id': 'mock-leader-1',
            'nombre': 'Juan Carlos',
            'apellido': 'Pérez',
            'rol': 'Lider',
            'telefono': '+58 412 123 4567',
            'cdp_id': 1,
            'cdp_nombre': 'Casa Bethel',
            'red_id': 1,
            'red_nombre': 'Red Hebrón',
            'usuario_id': '1d4f7c99-7d51-11f1-bf9e-2016d8516279'
        },
        {
            'id': 'mock-leader-1b',
            'nombre': 'Ana',
            'apellido': 'Martínez',
            'rol': 'Sublider',
            'telefono': '+58 412 765 4321',
            'cdp_id': 1,
            'cdp_nombre': 'Casa Bethel',
            'red_id': 1,
            'red_nombre': 'Red Hebrón',
            'usuario_id': None
        },
        {
            'id': 'mock-leader-2',
            'nombre': 'Elena',
            'apellido': 'Pérez',
            'rol': 'Lider',
            'telefono': '+58 414 987 6543',
            'cdp_id': 2,
            'cdp_nombre': 'Casa de Oración Sur',
            'red_id': 2,
            'red_nombre': 'Red Sur',
            'usuario_id': 'mock-eperez'
        },
        {
            'id': 'mock-leader-2b',
            'nombre': 'Lucía',
            'apellido': 'Gómez',
            'rol': 'Sublider',
            'telefono': '+58 414 555 1234',
            'cdp_id': 2,
            'cdp_nombre': 'Casa de Oración Sur',
            'red_id': 2,
            'red_nombre': 'Red Sur',
            'usuario_id': None
        },
        {
            'id': 'mock-leader-3',
            'nombre': 'Andrés',
            'apellido': 'Soler',
            'rol': 'Lider',
            'telefono': '+58 424 567 8901',
            'cdp_id': 3,
            'cdp_nombre': 'Casa Nueva Vida',
            'red_id': 3,
            'red_nombre': 'Red Central',
            'usuario_id': 'mock-asoler'
        },
        {
            'id': 'mock-leader-3b',
            'nombre': 'Carlos',
            'apellido': 'Ramírez',
            'rol': 'Sublider',
            'telefono': '+58 424 888 9900',
            'cdp_id': 3,
            'cdp_nombre': 'Casa Nueva Vida',
            'red_id': 3,
            'red_nombre': 'Red Central',
            'usuario_id': None
        },
        {
            'id': 'mock-leader-4',
            'nombre': 'Mateo',
            'apellido': 'Rodríguez',
            'rol': 'Lider',
            'telefono': '+58 416 345 6789',
            'cdp_id': 4,
            'cdp_nombre': 'Casa Luz',
            'red_id': 1,
            'red_nombre': 'Red Hebrón',
            'usuario_id': None
        },
        {
            'id': 'mock-leader-4b',
            'nombre': 'Roberto',
            'apellido': 'Morales',
            'rol': 'Sublider',
            'telefono': '+58 416 999 1122',
            'cdp_id': 4,
            'cdp_nombre': 'Casa Luz',
            'red_id': 1,
            'red_nombre': 'Red Hebrón',
            'usuario_id': None
        },
    ]


def get_mock_reportes():
    """Reportes de demostración para la vista administrativa y de supervisores."""
    hoy = date.today()
    meses_abr = {1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'}

    def fmt(d):
        return f"{d.day} {meses_abr.get(d.month, '')} {d.year}"

    f1 = hoy - timedelta(days=2)
    f2 = hoy - timedelta(days=4)
    f3 = hoy - timedelta(days=10)
    f4 = hoy - timedelta(days=12)
    f5 = hoy - timedelta(days=9)

    return [
        {
            'id': 'mock-rep-1',
            'fecha': f1.isoformat(),
            'fecha_formateada': fmt(f1),
            'lider_nombre': 'Juan Carlos Pérez',
            'iniciales': 'JP',
            'avatar_class': 'bg-primary-light text-primary',
            'cdp_id': 1,
            'cdp_nombre': 'Casa Bethel',
            'red_id': 1,
            'red_nombre': 'Red Hebrón',
            'hr_inicio': '19:00',
            'hr_fin': '20:30',
            'nro_regulares': 10,
            'nro_niños': 4,
            'nro_visitas': 3,
            'nro_comprometidos': 1,
            'asistencia': 18,
            'reconciliaciones': 2,
            'confesiones': 1,
            'ofrendas_usd': 25.00,
            'ofrendas_bs': 450.00,
            'cesta_amor': 1,
            'cesta_amor_desc': 'Sí',
            'tema': 'El poder del perdón',
            'observaciones': 'Excelente participación de nuevas familias del sector.',
        },
        {
            'id': 'mock-rep-2',
            'fecha': f2.isoformat(),
            'fecha_formateada': fmt(f2),
            'lider_nombre': 'Mateo Rodríguez',
            'iniciales': 'MR',
            'avatar_class': 'bg-secondary-light text-secondary',
            'cdp_id': 4,
            'cdp_nombre': 'Casa Luz',
            'red_id': 1,
            'red_nombre': 'Red Hebrón',
            'hr_inicio': '18:30',
            'hr_fin': '20:30',
            'nro_regulares': 7,
            'nro_niños': 3,
            'nro_visitas': 2,
            'nro_comprometidos': 0,
            'asistencia': 12,
            'reconciliaciones': 1,
            'confesiones': 0,
            'ofrendas_usd': 20.00,
            'ofrendas_bs': 360.00,
            'cesta_amor': 1,
            'cesta_amor_desc': 'Sí',
            'tema': 'Fe inquebrantable',
            'observaciones': 'Se recibieron 2 nuevos visitantes en el sector Las Flores.',
        },
        {
            'id': 'mock-rep-3',
            'fecha': f3.isoformat(),
            'fecha_formateada': fmt(f3),
            'lider_nombre': 'Elena Pérez',
            'iniciales': 'EP',
            'avatar_class': 'bg-primary-light text-primary',
            'cdp_id': 2,
            'cdp_nombre': 'Casa de Oración Sur',
            'red_id': 2,
            'red_nombre': 'Red Sur',
            'hr_inicio': '19:00',
            'hr_fin': '20:30',
            'nro_regulares': 8,
            'nro_niños': 3,
            'nro_visitas': 2,
            'nro_comprometidos': 1,
            'asistencia': 14,
            'reconciliaciones': 1,
            'confesiones': 1,
            'ofrendas_usd': 22.00,
            'ofrendas_bs': 390.00,
            'cesta_amor': 1,
            'cesta_amor_desc': 'Sí',
            'tema': 'La oración transforma',
            'observaciones': 'Tiempo especial de oración y acción de gracias.',
        },
        {
            'id': 'mock-rep-4',
            'fecha': f4.isoformat(),
            'fecha_formateada': fmt(f4),
            'lider_nombre': 'Andrés Soler',
            'iniciales': 'AS',
            'avatar_class': 'bg-secondary-light text-secondary',
            'cdp_id': 3,
            'cdp_nombre': 'Casa Nueva Vida',
            'red_id': 3,
            'red_nombre': 'Red Central',
            'hr_inicio': '19:30',
            'hr_fin': '21:00',
            'nro_regulares': 14,
            'nro_niños': 4,
            'nro_visitas': 3,
            'nro_comprometidos': 1,
            'asistencia': 22,
            'reconciliaciones': 3,
            'confesiones': 2,
            'ofrendas_usd': 35.00,
            'ofrendas_bs': 630.00,
            'cesta_amor': 1,
            'cesta_amor_desc': 'Sí',
            'tema': 'Discipulado y comunidad',
            'observaciones': 'Reunión especial con gran respuesta de los asistentes.',
        },
        {
            'id': 'mock-rep-5',
            'fecha': f5.isoformat(),
            'fecha_formateada': fmt(f5),
            'lider_nombre': 'Juan Carlos Pérez',
            'iniciales': 'JP',
            'avatar_class': 'bg-primary-light text-primary',
            'cdp_id': 1,
            'cdp_nombre': 'Casa Bethel',
            'red_id': 1,
            'red_nombre': 'Red Hebrón',
            'hr_inicio': '19:00',
            'hr_fin': '20:30',
            'nro_regulares': 9,
            'nro_niños': 4,
            'nro_visitas': 2,
            'nro_comprometidos': 1,
            'asistencia': 16,
            'reconciliaciones': 1,
            'confesiones': 0,
            'ofrendas_usd': 20.00,
            'ofrendas_bs': 360.00,
            'cesta_amor': 1,
            'cesta_amor_desc': 'Sí',
            'tema': 'Creciendo en Sabiduría',
            'observaciones': 'Estudio participativo y confraternidad.',
        },
    ]


# ---------------------------------------------------------------------------
def _mock_obtener_rango_periodo(periodo='semana'):
    """Calcula (fecha_inicio, fecha_fin) para datos mock según el período natural."""
    hoy = date.today()
    if periodo == 'mes':
        inicio = date(hoy.year, hoy.month, 1)
        fin = date(hoy.year, 12, 31) if hoy.month == 12 else date(hoy.year, hoy.month + 1, 1) - timedelta(days=1)
        return inicio, fin
    elif periodo == 'anio':
        return date(hoy.year, 1, 1), date(hoy.year, 12, 31)
    return hoy - timedelta(days=7), hoy


def _mock_periodo_a_fecha(periodo='semana'):
    """Calcula la fecha límite desde según el período para datos mock."""
    return _mock_obtener_rango_periodo(periodo)[0]


# ---------------------------------------------------------------------------
# Vista General
# ---------------------------------------------------------------------------
def get_mock_generales(periodo='semana'):
    """Métricas mock para la vista general de la iglesia según el período ('semana', 'mes', 'anio')."""
    hoy = date.today()
    fecha_desde, fecha_hasta = _mock_obtener_rango_periodo(periodo)

    reportes = get_mock_reportes()
    casas = get_casas_demo()

    # Base de cálculo: considerar únicamente Casas de Paz activas
    casas_activas = [c for c in casas if bool(c.get('is_active', 1)) and c.get('estado') != 'pausada']
    total_casas = len(casas_activas)
    casas_activas_ids = {c['id'] for c in casas_activas}

    # Reportes emitidos en el período activo de casas activas
    reportes_periodo = []
    casas_con_rep_ids = set()
    for r in reportes:
        f = r.get('fecha')
        if f and r.get('cdp_id') in casas_activas_ids:
            try:
                f_date = date.fromisoformat(str(f)[:10])
                if fecha_desde <= f_date <= fecha_hasta:
                    reportes_periodo.append(r)
                    casas_con_rep_ids.add(r['cdp_id'])
            except Exception:
                pass

    total_asistencia = sum(r['asistencia'] for r in reportes_periodo)
    total_ofrendas_usd = sum(r['ofrendas_usd'] for r in reportes_periodo)
    total_ofrendas_bs = sum(r['ofrendas_bs'] for r in reportes_periodo)
    total_visitas = sum(r['nro_visitas'] for r in reportes_periodo)
    total_reconciliaciones = sum(r['reconciliaciones'] for r in reportes_periodo)
    total_confesiones = sum(r['confesiones'] for r in reportes_periodo)
    total_cestas = sum(r['cesta_amor'] for r in reportes_periodo)

    casas_con_reporte = len([c for c in casas_activas if c['id'] in casas_con_rep_ids])
    cumplimiento = round((casas_con_reporte / total_casas * 100) if total_casas > 0 else 0)
    faltantes = [c for c in casas_activas if c['id'] not in casas_con_rep_ids]
    total_sin_reporte_7d = len(faltantes)
    casas_sin_reporte_ids = [c['id'] for c in faltantes]
    casas_sin_reporte_codigos = [c.get('codigo') or c.get('nombre') for c in faltantes]
    casas_pendientes = total_sin_reporte_7d

    # Tendencia según período
    meses_nombres = ['', 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    meses_completos = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

    if periodo == 'anio':
        # 12 meses fijos del año en curso
        asist_mes = {m: 0 for m in range(1, 13)}
        for r in reportes:
            f = r.get('fecha')
            if f:
                try:
                    fd = date.fromisoformat(str(f)[:10])
                    if fd.year == hoy.year:
                        asist_mes[fd.month] += r.get('asistencia', 0)
                except Exception:
                    pass
        if sum(asist_mes.values()) == 0:
            # Simular meses activos hasta el mes en curso (máx 6 meses)
            for m in range(max(1, hoy.month - 4), hoy.month + 1):
                asist_mes[m] = 120 + m * 8
        meses_activos = [m for m in range(1, 13) if asist_mes[m] > 0]
        if not meses_activos:
            meses_activos = [hoy.month]
        max_asist_tend = max((asist_mes[m] for m in meses_activos), default=1) or 1
        tendencia_semanas = [
            {
                'semana': meses_nombres[m],
                'fecha_completa': f"{meses_completos[m]} {hoy.year}",
                'asistencia': asist_mes[m],
                'porcentaje': round(asist_mes[m] / max_asist_tend * 100) if max_asist_tend > 0 else 0,
            }
            for m in meses_activos
        ]
    elif periodo == 'mes':
        # Semanas del mes calendario actual (Sem 1 a 4/5)
        num_dias_mes = fecha_hasta.day
        total_semanas_mes = 5 if num_dias_mes > 28 else 4
        asist_sem = {w: 0 for w in range(1, total_semanas_mes + 1)}
        for r in reportes_periodo:
            try:
                fd = date.fromisoformat(str(r['fecha'])[:10])
                day = fd.day
                w = 1 if day <= 7 else (2 if day <= 14 else (3 if day <= 21 else (4 if day <= 28 else 5)))
                if w in asist_sem:
                    asist_sem[w] += r.get('asistencia', 0)
            except Exception:
                pass
        if sum(asist_sem.values()) == 0:
            for w in range(1, total_semanas_mes + 1):
                asist_sem[w] = 20 + w * 6
        max_asist_tend = max(asist_sem.values(), default=1) or 1
        tendencia_semanas = []
        for w in range(1, total_semanas_mes + 1):
            dia_ini = 1 + (w - 1) * 7
            dia_fin = min(w * 7, num_dias_mes)
            d_ini = date(hoy.year, hoy.month, dia_ini)
            d_fin = date(hoy.year, hoy.month, dia_fin)
            tendencia_semanas.append({
                'semana': f"Sem {w}",
                'rango_fecha': f"{d_ini.strftime('%d')}-{formatear_fecha_corta(d_fin)}",
                'fecha_completa': f"Semana {w} ({formatear_fecha_corta(d_ini)} - {formatear_fecha_corta(d_fin)})",
                'asistencia': asist_sem[w],
                'porcentaje': round(asist_sem[w] / max_asist_tend * 100) if max_asist_tend > 0 else 0,
            })
    else:
        # Período semanal: Desglose individual de asistencia por cada Red
        redes = get_redes_demo()
        asist_red = {r['nombre']: 0 for r in redes}
        for r in reportes_periodo:
            rn = r.get('red_nombre')
            if rn in asist_red:
                asist_red[rn] += r.get('asistencia', 0)
        # Asegurar datos para demostración si no hay reportes en la semana
        if sum(asist_red.values()) == 0:
            asist_red = {'Red Hebrón': 30, 'Red Central': 25, 'Red Sur': 18}
        max_asist_tend = max(asist_red.values(), default=1) or 1
        tendencia_semanas = [
            {
                'semana': r['nombre'],
                'fecha_completa': f"{r['nombre']} · Esta semana",
                'asistencia': asist_red.get(r['nombre'], 0),
                'porcentaje': round(asist_red.get(r['nombre'], 0) / max_asist_tend * 100) if max_asist_tend > 0 else 0,
            }
            for r in redes
        ]
    promedio_tendencia = round(sum(t['asistencia'] for t in tendencia_semanas) / len(tendencia_semanas)) if tendencia_semanas else 0

    return {
        'total_asistencia': total_asistencia,
        'cumplimiento': cumplimiento,
        'ofrendas_usd': total_ofrendas_usd,
        'ofrendas_bs': total_ofrendas_bs,
        'conversiones': total_confesiones,
        'reconciliaciones': total_reconciliaciones,
        'cestas_amor': total_cestas,
        'total_visitas': total_visitas,
        'total_casas': total_casas,
        'casas_con_reporte': casas_con_reporte,
        'casas_pendientes': casas_pendientes,
        'total_sin_reporte_7d': total_sin_reporte_7d,
        'casas_sin_reporte_ids': casas_sin_reporte_ids,
        'casas_sin_reporte_codigos': casas_sin_reporte_codigos,
        'casas_sin_reporte_7d': casas_sin_reporte_codigos,
        'reportes_enviados': len(reportes_periodo),
        'distribucion': {
            'regulares': sum(r['nro_regulares'] for r in reportes_periodo),
            'ninos': sum(r['nro_niños'] for r in reportes_periodo),
            'visitas': total_visitas,
            'comprometidos': sum(r['nro_comprometidos'] for r in reportes_periodo),
        },
        'tendencia': tendencia_semanas,
        'tendencia_semanas': tendencia_semanas,
        'promedio_tendencia': promedio_tendencia,
        'ranking_redes': [
            {'nombre': 'Red Hebrón', 'cumplimiento': 100, 'asistencia': 30, 'asistencia_semana': 30, 'asistencia_total': 340, 'casas_reportadas': 2, 'total_casas': 2, 'supervisor': 'Pedro González', 'color_class': 'hebron'},
            {'nombre': 'Red Central', 'cumplimiento': 0, 'asistencia': 0, 'asistencia_semana': 0, 'asistencia_total': 280, 'casas_reportadas': 0, 'total_casas': 1, 'supervisor': 'Carlos Ramírez', 'color_class': 'central'},
            {'nombre': 'Red Sur', 'cumplimiento': 0, 'asistencia': 0, 'asistencia_semana': 0, 'asistencia_total': 190, 'casas_reportadas': 0, 'total_casas': 1, 'supervisor': 'María López', 'color_class': 'sur'},
        ][:3],
        'alertas': [],
        'periodo': periodo,
    }


# ---------------------------------------------------------------------------
# Vista Red
# ---------------------------------------------------------------------------
def get_mock_red(red_id, periodo='semana'):
    """Métricas mock para la vista de una red específica según el período ('semana', 'mes', 'anio')."""
    hoy = date.today()
    fecha_desde, fecha_hasta = _mock_obtener_rango_periodo(periodo)

    redes = get_redes_demo()
    red = next((r for r in redes if str(r['id']) == str(red_id)), None)
    if not red:
        return get_empty_red(red_id)
    rid = red['id']

    casas_red = [c for c in get_casas_demo() if c['red_id'] == rid]
    reportes_red = [rep for rep in get_mock_reportes() if rep['red_id'] == rid]
    reportes_red_periodo = []
    for rep in reportes_red:
        f = rep.get('fecha')
        if f:
            try:
                fd = date.fromisoformat(str(f)[:10])
                if fecha_desde <= fd <= fecha_hasta:
                    reportes_red_periodo.append(rep)
            except Exception:
                pass

    lideres_red = [l for l in get_mock_lideres() if l['red_id'] == rid and l.get('rol') == 'Lider']

    casas_activas_red = [c for c in casas_red if bool(c.get('is_active', 1)) and c.get('estado') != 'pausada']
    total_casas_red = len(casas_activas_red)

    casas_con_rep_ids = {r['cdp_id'] for r in reportes_red_periodo}

    asistencia_total = sum(rep['asistencia'] for rep in reportes_red_periodo)
    promedio_casa = round(asistencia_total / total_casas_red) if total_casas_red > 0 else 0
    ofrendas_usd_total = sum(rep.get('ofrendas_usd', 0.0) for rep in reportes_red_periodo)
    ofrendas_bs_total = sum(rep.get('ofrendas_bs', 0.0) for rep in reportes_red_periodo)
    ninos_total = sum(rep.get('nro_niños', 0) for rep in reportes_red_periodo)
    conversiones_total = sum(rep.get('confesiones', 0) for rep in reportes_red_periodo)

    distribucion = {
        'regulares': sum(rep.get('nro_regulares', 0) for rep in reportes_red_periodo),
        'ninos': ninos_total,
        'visitas': sum(rep.get('nro_visitas', 0) for rep in reportes_red_periodo),
        'comprometidos': sum(rep.get('nro_comprometidos', 0) for rep in reportes_red_periodo),
    }

    con_reporte = len([c for c in casas_activas_red if c['id'] in casas_con_rep_ids])
    cumplimiento = round((con_reporte / total_casas_red * 100) if total_casas_red > 0 else 0)
    faltantes = [c for c in casas_activas_red if c['id'] not in casas_con_rep_ids]
    total_sin_reporte_7d = len(faltantes)
    casas_sin_reporte_ids = [c['id'] for c in faltantes]
    casas_sin_reporte_codigos = [c.get('codigo') or c.get('nombre') for c in faltantes]
    casas_pendientes = total_sin_reporte_7d

    casas_cards = []
    for c in casas_red:
        is_act = bool(c.get('is_active', 1)) and c.get('estado') != 'pausada'
        rep_per = c['id'] in casas_con_rep_ids
        rep_casa_per = next((r for r in reportes_red_periodo if r['cdp_id'] == c['id']), None)
        asist_casa = rep_casa_per['asistencia'] if rep_casa_per else 0
        vis_casa = rep_casa_per['nro_visitas'] if rep_casa_per else 0

        if not is_act:
            estado = 'pausada'
        elif rep_per:
            estado = 'verde'
        else:
            estado = 'amarillo'

        casas_cards.append({
            'id': c['id'],
            'nombre': c['nombre'],
            'codigo': c['codigo'],
            'asistencia': asist_casa,
            'estado': estado,
            'is_active': is_act,
            'reporte_reciente_7d': rep_per,
            'reporte_reciente_periodo': rep_per,
            'lider': c['lider'],
            'visitas': vis_casa
        })

    lideres_cards = []
    for l in lideres_red:
        lideres_cards.append({
            'id': l['id'],
            'nombre': f"{l['nombre']} {l['apellido']}",
            'rol': l['rol'],
            'telefono': l['telefono'],
            'cdp_codigo': next((c['codigo'] for c in casas_red if c['id'] == l['cdp_id']), 'CDP'),
            'cdp_anfitrion': next((c['anfitrion'] for c in casas_red if c['id'] == l['cdp_id']), 'Familia')
        })

    best_growth = max(casas_cards, key=lambda x: (x['asistencia'], x['visitas'])) if casas_cards else None
    top_growth = {
        'nombre': best_growth['nombre'] if best_growth else (casas_red[0]['nombre'] if casas_red else 'Casa Bethel'),
        'codigo': best_growth['codigo'] if best_growth else (casas_red[0]['codigo'] if casas_red else 'HEB-001'),
        'tasa': f"+{best_growth['asistencia']}" if best_growth else '+0',
        'visitas': best_growth['visitas'] if best_growth else 0,
        'lider': best_growth['lider'] if best_growth else 'Líder',
    }

    # Tendencia de asistencia de la red según período
    meses_nombres = ['', 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    meses_completos = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

    if periodo == 'anio':
        # 12 meses fijos del año en curso
        asist_mes = {m: 0 for m in range(1, 13)}
        for r in reportes_red:
            f = r.get('fecha')
            if f:
                try:
                    fd = date.fromisoformat(str(f)[:10])
                    if fd.year == hoy.year:
                        asist_mes[fd.month] += r.get('asistencia', 0)
                except Exception:
                    pass
        base_factor = max(total_casas_red, 1) * 8
        if sum(asist_mes.values()) == 0:
            for m in range(max(1, hoy.month - 4), hoy.month + 1):
                asist_mes[m] = base_factor + m * 4
        meses_activos = [m for m in range(1, 13) if asist_mes[m] > 0]
        if not meses_activos:
            meses_activos = [hoy.month]
        max_asist_red = max((asist_mes[m] for m in meses_activos), default=1) or 1
        tendencia_semanas_red = [
            {
                'semana': meses_nombres[m],
                'fecha_completa': f"{meses_completos[m]} {hoy.year}",
                'asistencia': asist_mes[m],
                'porcentaje': round(asist_mes[m] / max_asist_red * 100) if max_asist_red > 0 else 0,
            }
            for m in meses_activos
        ]
    elif periodo == 'mes':
        # Semanas del mes calendario actual (Sem 1 a 4/5)
        num_dias_mes = fecha_hasta.day
        total_semanas_mes = 5 if num_dias_mes > 28 else 4
        asist_sem = {w: 0 for w in range(1, total_semanas_mes + 1)}
        for r in reportes_red_periodo:
            try:
                fd = date.fromisoformat(str(r['fecha'])[:10])
                day = fd.day
                w = 1 if day <= 7 else (2 if day <= 14 else (3 if day <= 21 else (4 if day <= 28 else 5)))
                if w in asist_sem:
                    asist_sem[w] += r.get('asistencia', 0)
            except Exception:
                pass
        base_factor = max(total_casas_red, 1) * 8
        if sum(asist_sem.values()) == 0:
            for w in range(1, total_semanas_mes + 1):
                asist_sem[w] = base_factor + w * 3
        max_asist_red = max(asist_sem.values(), default=1) or 1
        tendencia_semanas_red = []
        for w in range(1, total_semanas_mes + 1):
            dia_ini = 1 + (w - 1) * 7
            dia_fin = min(w * 7, num_dias_mes)
            d_ini = date(hoy.year, hoy.month, dia_ini)
            d_fin = date(hoy.year, hoy.month, dia_fin)
            tendencia_semanas_red.append({
                'semana': f"Sem {w}",
                'rango_fecha': f"{d_ini.strftime('%d')}-{formatear_fecha_corta(d_fin)}",
                'fecha_completa': f"Semana {w} ({formatear_fecha_corta(d_ini)} - {formatear_fecha_corta(d_fin)})",
                'asistencia': asist_sem[w],
                'porcentaje': round(asist_sem[w] / max_asist_red * 100) if max_asist_red > 0 else 0,
            })
    else:
        # Período semanal: Desglose individual de asistencia por cada Casa de Paz de la red
        asist_cdp = {c['codigo']: 0 for c in casas_red}
        anfitrion_map = {c['codigo']: c.get('anfitrion') or c.get('nombre') for c in casas_red}
        for r in reportes_red_periodo:
            cdp_cod = next((c['codigo'] for c in casas_red if c['id'] == r.get('cdp_id')), None)
            if cdp_cod and cdp_cod in asist_cdp:
                asist_cdp[cdp_cod] += r.get('asistencia', 0)
        # Si no hay reportes en la semana, rellenar datos demo proporcionales
        if sum(asist_cdp.values()) == 0 and casas_red:
            for idx, c in enumerate(casas_red):
                asist_cdp[c['codigo']] = 12 + idx * 4
        max_asist_red = max(asist_cdp.values(), default=1) or 1
        tendencia_semanas_red = [
            {
                'semana': c['codigo'],
                'fecha_completa': f"{c['codigo']} - {anfitrion_map.get(c['codigo'], 'Casa de Paz')}",
                'asistencia': asist_cdp.get(c['codigo'], 0),
                'porcentaje': round(asist_cdp.get(c['codigo'], 0) / max_asist_red * 100) if max_asist_red > 0 else 0,
            }
            for c in casas_red
        ]
    promedio_tendencia_red = round(sum(t['asistencia'] for t in tendencia_semanas_red) / len(tendencia_semanas_red)) if tendencia_semanas_red else 0

    # Actividad reciente: últimos reportes de la red ordenados por fecha desc
    reportes_ordenados = sorted(reportes_red, key=lambda r: r.get('fecha', ''), reverse=True)
    actividad_reciente = []
    vistos_mock = set()
    for rep in reportes_ordenados:
        cdp_cod = next((c['codigo'] for c in casas_red if c['id'] == rep.get('cdp_id')), '')
        clave = (cdp_cod, str(rep.get('fecha', ''))[:10])
        if clave in vistos_mock:
            continue
        vistos_mock.add(clave)
        actividad_reciente.append({
            'lider': rep.get('lider_nombre', 'Líder'),
            'iniciales': rep.get('iniciales', 'NN'),
            'avatar_class': rep.get('avatar_class', 'bg-primary-light text-primary'),
            'cdp_nombre': rep.get('cdp_nombre', 'Casa de Paz'),
            'cdp_codigo': cdp_cod,
            'fecha_formateada': rep.get('fecha_formateada', ''),
            'asistencia': rep.get('asistencia', 0),
            'tema': rep.get('tema', ''),
        })
        if len(actividad_reciente) >= 10:
            break

    return {
        'nombre_red': red['nombre'],
        'red_id': rid,
        'supervisor': red['supervisor'],
        'casas_activas': total_casas_red,
        'asistencia_total': asistencia_total,
        'total_asistencia': asistencia_total,
        'promedio_casa': promedio_casa,
        'ninos': ninos_total,
        'conversiones': conversiones_total,
        'ofrendas_usd': ofrendas_usd_total,
        'ofrendas_bs': ofrendas_bs_total,
        'distribucion': distribucion,
        'casas': casas_cards,
        'alertas_zonal': [],
        'top_crecimiento': top_growth,
        'cumplimiento': cumplimiento,
        'casas_con_reporte': con_reporte,
        'casas_pendientes': casas_pendientes,
        'total_sin_reporte_7d': total_sin_reporte_7d,
        'casas_sin_reporte_ids': casas_sin_reporte_ids,
        'casas_sin_reporte_codigos': casas_sin_reporte_codigos,
        'casas_sin_reporte_7d': casas_sin_reporte_codigos,
        'lideres_red': lideres_cards,
        'tendencia': tendencia_semanas_red,
        'tendencia_semanas': tendencia_semanas_red,
        'promedio_tendencia': promedio_tendencia_red,
        'actividad_reciente': actividad_reciente,
        'periodo': periodo,
    }


# ---------------------------------------------------------------------------
# Vista Casa de Paz
# ---------------------------------------------------------------------------
def get_mock_cdp(cdp_id):
    """Métricas mock para la vista de una Casa de Paz específica."""
    casas = get_casas_demo()
    cdp = next((c for c in casas if str(c['id']) == str(cdp_id)), None)
    if not cdp:
        return get_empty_cdp(cdp_id)
    cid = cdp['id']

    reps = [r for r in get_mock_reportes() if r['cdp_id'] == cid]
    lideres_cdp = [l for l in get_mock_lideres() if l['cdp_id'] == cid]

    lider_nombre = cdp.get('lider', 'Juan Carlos Pérez')
    sublider_nombre = next((f"{l['nombre']} {l['apellido']}" for l in lideres_cdp if l['rol'] == 'Sublider'), 'Ana Martínez')

    historial = []
    mini_hist = []
    for r in reps:
        historial.append({
            'fecha': r['fecha'],
            'asistencia': r['asistencia'],
            'ninos': r['nro_niños'],
            'visitas': r['nro_visitas'],
            'ofrendas_usd': r['ofrendas_usd'],
            'ofrendas_bs': r['ofrendas_bs'],
            'observaciones': r['observaciones'],
        })
        mini_hist.append({
            'fecha': r['fecha_formateada'][:6],
            'asistencia': r['asistencia'],
            'altura': min(100, int(r['asistencia'] * 5))
        })

    if not historial:
        historial = [
            {'fecha': '2026-08-24', 'asistencia': cdp['asistencia'], 'ninos': 4, 'visitas': 2, 'ofrendas_usd': 20.0, 'ofrendas_bs': 360.0, 'observaciones': 'Reunión de edificación.'}
        ]
        mini_hist = [
            {'fecha': '24 Ago', 'asistencia': cdp['asistencia'], 'altura': 90}
        ]

    return {
        'id': cid,
        'nombre_cdp': cdp['nombre'],
        'codigo': cdp['codigo'],
        'red_id': cdp['red_id'],
        'red_nombre': cdp['red_nombre'],
        'supervisor': cdp['supervisor'],
        'lider': lider_nombre,
        'sublider': sublider_nombre,
        'anfitrion': cdp['anfitrion'],
        'telefono_contacto': cdp['telefono'],
        'direccion': cdp['direccion'],
        'asistencia_ultimo': historial[0]['asistencia'],
        'total_asistencia': historial[0]['asistencia'],
        'promedio_historico': round(sum(h['asistencia'] for h in historial) / len(historial)),
        'visitas': sum(h['visitas'] for h in historial),
        'conversiones': 3,
        'ofrendas_usd': sum(h['ofrendas_usd'] for h in historial),
        'ofrendas_bs': sum(h['ofrendas_bs'] for h in historial),
        'estado_reporte': 'enviado',
        'reporte_al_dia': True,
        'dias_desde_reporte': 2,
        'ultimo_reporte_reciente': True,
        'ultimo_reporte_por': f"{lider_nombre} (Líder)",
        'ultimo_reporte_fecha': reps[0]['fecha_formateada'] if reps else '24 Ago 2026',
        'ultimo_tema': reps[0]['tema'] if reps else 'El Poder de la Fe',
        'hr_inicio': '19:00',
        'hr_fin': '20:30',
        'cesta_amor': True,
        'potencial_multiplicacion': True,
        'distribucion': {
            'regulares': reps[0]['nro_regulares'] if reps else 10,
            'ninos': reps[0]['nro_niños'] if reps else 4,
            'visitas': reps[0]['nro_visitas'] if reps else 3,
            'comprometidos': reps[0]['nro_comprometidos'] if reps else 1,
        },
        'historial': historial,
        'mini_historico': mini_hist,
    }


def get_mock_cdp_detalle(cdp_id):
    """
    Retorna el contexto completo para la vista de detalle de Casa de Paz
    (templates/detalles_cdp.html) asegurando total coherencia con mock_data.
    """
    casas = get_casas_demo()
    cdp = next((c for c in casas if str(c['id']) == str(cdp_id)), None)
    if not cdp:
        return None
    cid = cdp['id']

    lideres = [l for l in get_mock_lideres() if l['cdp_id'] == cid]
    reportes = [r for r in get_mock_reportes() if r['cdp_id'] == cid]

    team = []
    for l in lideres:
        nom = l['nombre']
        ape = l['apellido']
        ini = (nom[:1] + ape[:1]).upper()
        tel = l['telefono']
        tel_clean = re.sub(r'\D', '', tel)
        tel_wa = f"58{tel_clean[1:]}" if tel_clean.startswith('0') else tel_clean

        team.append({
            'id': l['id'],
            'nombre_completo': f"{nom} {ape}",
            'rol': l['rol'],
            'telefono': tel,
            'telefono_wa': tel_wa if len(tel_wa) >= 8 else None,
            'iniciales': ini
        })

    lider_principal = cdp['lider']
    telefono_contacto = cdp['telefono']
    direccion = cdp['direccion']
    maps_query = urllib.parse.quote_plus(f"{direccion}, Venezuela")

    asistencia_promedio = round(sum(r['asistencia'] for r in reportes) / len(reportes)) if reportes else cdp['asistencia']
    ofrendas_usd_totales = sum(r['ofrendas_usd'] for r in reportes)
    ofrendas_bs_totales = sum(r['ofrendas_bs'] for r in reportes)

    # Usuario del sistema asignado
    usuarios = get_mock_usuarios()
    user = next((u for u in usuarios if u['id'] == cdp.get('lider_id') or u['id'] == cdp.get('usuario_id')), None)
    if not user:
        user = usuarios[2]  # Default demo leader 'lider'

    # Horario derivado del reporte más reciente si existe
    if reportes:
        r_rec = reportes[0]
        hr_ini = r_rec.get('hr_inicio', '19:00')
        f_str = r_rec.get('fecha')
        dia_txt = ''
        if f_str:
            try:
                from datetime import datetime
                dias_semana = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}
                f_obj = datetime.strptime(f_str[:10], '%Y-%m-%d')
                dia_txt = dias_semana.get(f_obj.weekday(), '')
            except Exception:
                pass
        horario = f"{dia_txt} · {hr_ini}" if dia_txt else f"Reunión: {hr_ini}"
    else:
        horario = 'Miércoles · 7:00 PM'

    hoy = date.today()
    hace_7_dias = hoy - timedelta(days=7)
    ultimo_rep = reportes[0] if reportes else None
    ultimo_reporte_fecha = None
    dias_desde_ultimo_reporte = None
    tiene_reporte_reciente = False

    if ultimo_rep and ultimo_rep.get('fecha'):
        f_str = ultimo_rep.get('fecha')
        try:
            f_date = date.fromisoformat(str(f_str)[:10])
            dias_desde_ultimo_reporte = (hoy - f_date).days
            if f_date >= hace_7_dias:
                tiene_reporte_reciente = True
        except Exception:
            pass
        ultimo_reporte_fecha = ultimo_rep.get('fecha_formateada') or str(f_str or '')

    is_active = bool(cdp.get('is_active', 1)) and (cdp.get('estado') != 'pausada')

    if not is_active:
        estado_reporte_7d = 'pausada'
        reporte_reciente_7d = False
    elif tiene_reporte_reciente:
        estado_reporte_7d = 'al_dia'
        reporte_reciente_7d = True
    else:
        estado_reporte_7d = 'pendiente'
        reporte_reciente_7d = False

    return {
        'id': cid,
        'codigo': cdp['codigo'],
        'red_id': cdp.get('red_id', 1),
        'nombre': cdp['nombre'],
        'red_nombre': cdp['red_nombre'],
        'supervisor_nombre': cdp['supervisor'],
        'direccion': direccion,
        'maps_url': f"https://www.google.com/maps/search/?api=1&query={maps_query}",
        'anfitrion': cdp['anfitrion'],
        'lider_nombre': lider_principal,
        'telefono': telefono_contacto,
        'telefono_wa': re.sub(r'\D', '', telefono_contacto),
        'is_active': is_active,
        'estado': 'activa' if is_active else 'inactiva',
        'reporte_reciente_7d': reporte_reciente_7d,
        'estado_reporte_7d': estado_reporte_7d,
        'ultimo_reporte_fecha': ultimo_reporte_fecha,
        'dias_desde_ultimo_reporte': dias_desde_ultimo_reporte,
        'horario': horario,
        'usuario_id': user['id'] if user else None,
        'usuario_username': user['username'] if user else None,
        'usuario_nombre': user['nombre'] if user else '',
        'usuario_apellido': user['apellido'] if user else '',
        'usuario_activo': bool(user.get('is_active', 1)) if user else True,
        'asistencia_promedio': asistencia_promedio,
        'total_reportes': len(reportes),
        'ofrendas_usd_totales': ofrendas_usd_totales,
        'ofrendas_bs_totales': ofrendas_bs_totales,
        'visitas_totales': sum(r['nro_visitas'] for r in reportes),
        'conversiones_totales': sum(r['confesiones'] for r in reportes),
        'reconciliaciones_totales': sum(r['reconciliaciones'] for r in reportes),
        'total_voluntarios': len(team),
        'lideres': team,
        'reportes': reportes
    }


# ---------------------------------------------------------------------------
# Empty states (BD conectada pero sin datos)
# ---------------------------------------------------------------------------
def get_empty_generales():
    """Métricas vacías cuando la BD está conectada pero no hay reportes."""
    return {
        'total_asistencia': 0,
        'asistencia_total': 0,
        'cumplimiento': 0,
        'ofrendas_usd': 0.0,
        'ofrendas_bs': 0.0,
        'conversiones': 0,
        'reconciliaciones': 0,
        'cestas_amor': 0,
        'total_visitas': 0,
        'total_casas': 0,
        'casas_con_reporte': 0,
        'casas_pendientes': 0,
        'total_sin_reporte_7d': 0,
        'casas_sin_reporte_ids': [],
        'casas_sin_reporte_codigos': [],
        'casas_sin_reporte_7d': [],
        'reportes_enviados': 0,
        'distribucion': {
            'regulares': 0,
            'ninos': 0,
            'visitas': 0,
            'comprometidos': 0,
        },
        'tendencia': [],
        'tendencia_semanas': [],
        'promedio_tendencia': 0,
        'ranking_redes': [],
        'alertas': [],
    }


def get_empty_red(red_id):
    """Métricas vacías para una red sin datos."""
    return {
        'nombre_red': 'Red sin datos',
        'red_id': red_id,
        'supervisor': 'Sin asignar',
        'casas_activas': 0,
        'asistencia_total': 0,
        'total_asistencia': 0,
        'promedio_casa': 0,
        'ninos': 0,
        'conversiones': 0,
        'ofrendas_usd': 0.0,
        'ofrendas_bs': 0.0,
        'cumplimiento': 0,
        'casas_con_reporte': 0,
        'casas_pendientes': 0,
        'total_sin_reporte_7d': 0,
        'casas_sin_reporte_ids': [],
        'casas_sin_reporte_codigos': [],
        'casas_sin_reporte_7d': [],
        'distribucion': {
            'regulares': 0,
            'ninos': 0,
            'visitas': 0,
            'comprometidos': 0,
        },
        'casas': [],
        'alertas_zonal': [],
        'top_crecimiento': {},
        'lideres_red': [],
        'tendencia_semanas': [],
        'promedio_tendencia': 0,
        'actividad_reciente': [],
    }


def get_empty_cdp(cdp_id):
    """Métricas vacías para una CDP sin datos."""
    return {
        'nombre_cdp': 'Casa de Paz',
        'codigo': '',
        'lider': '',
        'sublider': '',
        'anfitrion': '',
        'telefono_contacto': '',
        'direccion': '',
        'asistencia_ultimo': 0,
        'total_asistencia': 0,
        'asistencia_total': 0,
        'casas_pendientes': 0,
        'total_sin_reporte_7d': 0,
        'promedio_historico': 0,
        'visitas': 0,
        'conversiones': 0,
        'ofrendas_usd': 0.0,
        'ofrendas_bs': 0.0,
        'estado_reporte': 'pendiente',
        'reporte_al_dia': False,
        'dias_desde_reporte': None,
        'ultimo_reporte_reciente': False,
        'ultimo_reporte_por': '',
        'ultimo_reporte_fecha': '',
        'ultimo_tema': '',
        'hr_inicio': '',
        'hr_fin': '',
        'cesta_amor': False,
        'potencial_multiplicacion': False,
        'distribucion': {
            'regulares': 0,
            'ninos': 0,
            'visitas': 0,
            'comprometidos': 0,
        },
        'historial': [],
        'mini_historico': [],
    }

