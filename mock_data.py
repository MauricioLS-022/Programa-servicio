"""
mock_data.py - Datos de demostración para el dashboard y navegación sin base de datos.
Se usan cuando MOCK_MODE está activado o cuando la base de datos no está disponible.
Garantiza coherencia relacional estricta entre Redes, Casas de Paz, Líderes, Supervisores y Reportes.
"""
import urllib.parse
import re


def get_redes_demo():
    """Lista de redes para los selectores del filtro y vistas de estructura."""
    return [
        {
            'id': 1,
            'nombre': 'Red Hebrón',
            'supervisor': 'Pedro González',
            'supervisor_id': 'ca58cfc6-8337-11f1-8217-2016d8516279',
            'telefono': '+58 414 111 2233',
        },
        {
            'id': 2,
            'nombre': 'Red Sur',
            'supervisor': 'María López',
            'supervisor_id': 'mock-sup-2',
            'telefono': '+58 414 222 3344',
        },
        {
            'id': 3,
            'nombre': 'Red Central',
            'supervisor': 'Carlos Ramírez',
            'supervisor_id': 'mock-sup-3',
            'telefono': '+58 414 333 4455',
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
            'lider_id': '1d4f7c99-7d51-11f1-bf9e-2016d8516279',
            'telefono': '+58 412 123 4567',
            'asistencia': 18,
            'estado': 'activa',
            'horario': 'Martes · 7:30 PM'
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
            'lider_id': 'mock-leader-2',
            'telefono': '+58 414 987 6543',
            'asistencia': 14,
            'estado': 'activa',
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
            'lider_id': 'mock-asoler',
            'telefono': '+58 424 567 8901',
            'asistencia': 22,
            'estado': 'activa',
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
            'lider_id': 'mock-leader-4',
            'telefono': '+58 416 345 6789',
            'asistencia': 12,
            'estado': 'activa',
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
    return [
        {
            'id': 'mock-rep-1',
            'fecha': '2026-08-24',
            'fecha_formateada': '24 Ago 2026',
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
            'ofrendas': 25.00,
            'ofrendas_usd': 25.00,
            'ofrendas_bs': 450.00,
            'cesta_amor': 1,
            'cesta_amor_desc': 'Sí',
            'tema': 'El poder del perdón',
            'observaciones': 'Excelente participación de nuevas familias del sector.',
        },
        {
            'id': 'mock-rep-2',
            'fecha': '2026-08-22',
            'fecha_formateada': '22 Ago 2026',
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
            'ofrendas': 20.00,
            'ofrendas_usd': 20.00,
            'ofrendas_bs': 360.00,
            'cesta_amor': 1,
            'cesta_amor_desc': 'Sí',
            'tema': 'Fe inquebrantable',
            'observaciones': 'Se recibieron 2 nuevos visitantes en el sector Las Flores.',
        },
        {
            'id': 'mock-rep-3',
            'fecha': '2026-08-20',
            'fecha_formateada': '20 Ago 2026',
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
            'ofrendas': 22.00,
            'ofrendas_usd': 22.00,
            'ofrendas_bs': 390.00,
            'cesta_amor': 1,
            'cesta_amor_desc': 'Sí',
            'tema': 'La oración transforma',
            'observaciones': 'Tiempo especial de oración y acción de gracias.',
        },
        {
            'id': 'mock-rep-4',
            'fecha': '2026-08-18',
            'fecha_formateada': '18 Ago 2026',
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
            'ofrendas': 35.00,
            'ofrendas_usd': 35.00,
            'ofrendas_bs': 630.00,
            'cesta_amor': 1,
            'cesta_amor_desc': 'Sí',
            'tema': 'Discipulado y comunidad',
            'observaciones': 'Reunión especial con gran respuesta de los asistentes.',
        },
        {
            'id': 'mock-rep-5',
            'fecha': '2026-08-17',
            'fecha_formateada': '17 Ago 2026',
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
            'ofrendas': 20.00,
            'ofrendas_usd': 20.00,
            'ofrendas_bs': 360.00,
            'cesta_amor': 1,
            'cesta_amor_desc': 'Sí',
            'tema': 'Creciendo en Sabiduría',
            'observaciones': 'Estudio participativo y confraternidad.',
        },
    ]


# ---------------------------------------------------------------------------
# Vista General
# ---------------------------------------------------------------------------
def get_mock_generales():
    """Métricas mock para la vista general de la iglesia."""
    reportes = get_mock_reportes()
    casas = get_casas_demo()
    
    total_asistencia = sum(c['asistencia'] for c in casas)
    total_ofrendas = sum(r['ofrendas_usd'] for r in reportes)
    total_ofrendas_bs = sum(r['ofrendas_bs'] for r in reportes)
    total_visitas = sum(r['nro_visitas'] for r in reportes)
    total_reconciliaciones = sum(r['reconciliaciones'] for r in reportes)
    total_confesiones = sum(r['confesiones'] for r in reportes)

    return {
        'total_asistencia': total_asistencia,
        'cumplimiento': 85,
        'ofrendas': total_ofrendas,
        'ofrendas_usd': total_ofrendas,
        'ofrendas_bs': total_ofrendas_bs,
        'conversiones': total_confesiones,
        'reconciliaciones': total_reconciliaciones,
        'cestas_amor': sum(r['cesta_amor'] for r in reportes),
        'total_visitas': total_visitas,
        'total_casas': len(casas),
        'casas_con_reporte': len(set(r['cdp_id'] for r in reportes)),
        'reportes_enviados': len(reportes),
        'distribucion': {
            'regulares': sum(r['nro_regulares'] for r in reportes),
            'ninos': sum(r['nro_niños'] for r in reportes),
            'visitas': total_visitas,
            'comprometidos': sum(r['nro_comprometidos'] for r in reportes),
        },
        'tendencia_semanas': [
            {'semana': 'Sem 1', 'asistencia': 54, 'porcentaje': 75},
            {'semana': 'Sem 2', 'asistencia': 58, 'porcentaje': 80},
            {'semana': 'Sem 3', 'asistencia': 62, 'porcentaje': 85},
            {'semana': 'Sem 4', 'asistencia': 66, 'porcentaje': 90},
        ],
        'ranking_redes': [
            {'nombre': 'Red Hebrón', 'cumplimiento': 90, 'asistencia': 30, 'supervisor': 'Pedro González', 'color_class': 'hebron'},
            {'nombre': 'Red Central', 'cumplimiento': 85, 'asistencia': 22, 'supervisor': 'Carlos Ramírez', 'color_class': 'central'},
            {'nombre': 'Red Sur', 'cumplimiento': 80, 'asistencia': 14, 'supervisor': 'María López', 'color_class': 'sur'},
        ],
        'alertas': [],
    }


# ---------------------------------------------------------------------------
# Vista Red
# ---------------------------------------------------------------------------
def get_mock_red(red_id):
    """Métricas mock para la vista de una red específica."""
    redes = get_redes_demo()
    red = next((r for r in redes if str(r['id']) == str(red_id)), redes[0])
    rid = red['id']

    casas_red = [c for c in get_casas_demo() if c['red_id'] == rid]
    reportes_red = [rep for rep in get_mock_reportes() if rep['red_id'] == rid]
    lideres_red = [l for l in get_mock_lideres() if l['red_id'] == rid]

    asistencia_total = sum(c['asistencia'] for c in casas_red)
    promedio_casa = round(asistencia_total / len(casas_red)) if casas_red else 0
    ofrendas_total = sum(rep.get('ofrendas_usd', 0.0) for rep in reportes_red)
    ofrendas_bs_total = sum(rep.get('ofrendas_bs', 0.0) for rep in reportes_red)
    ninos_total = sum(rep.get('nro_niños', 0) for rep in reportes_red)
    conversiones_total = sum(rep.get('confesiones', 0) for rep in reportes_red)

    casas_cards = []
    for c in casas_red:
        casas_cards.append({
            'id': c['id'],
            'nombre': c['nombre'],
            'codigo': c['codigo'],
            'asistencia': c['asistencia'],
            'estado': 'verde' if c['asistencia'] >= 15 else 'amarillo',
            'lider': c['lider'],
            'visitas': 3
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

    return {
        'nombre_red': red['nombre'],
        'red_id': rid,
        'supervisor': red['supervisor'],
        'casas_activas': len(casas_red),
        'asistencia_total': asistencia_total,
        'promedio_casa': promedio_casa,
        'ninos': ninos_total,
        'conversiones': conversiones_total,
        'ofrendas': ofrendas_total,
        'ofrendas_usd': ofrendas_total,
        'ofrendas_bs': ofrendas_bs_total,
        'distribucion': {
            'regulares': sum(rep.get('nro_regulares', 0) for rep in reportes_red) or 20,
            'ninos': ninos_total or 8,
            'visitas': sum(rep.get('nro_visitas', 0) for rep in reportes_red) or 5,
            'comprometidos': sum(rep.get('nro_comprometidos', 0) for rep in reportes_red) or 2,
        },
        'casas': casas_cards,
        'alertas_zonal': [],
        'top_crecimiento': {
            'nombre': casas_red[0]['nombre'] if casas_red else 'Casa Bethel',
            'codigo': casas_red[0]['codigo'] if casas_red else 'HEB-001',
            'tasa': '+12%',
            'visitas': 3,
            'lider': casas_red[0]['lider'] if casas_red else 'Líder',
        },
        'cumplimiento': 85,
        'casas_con_reporte': len(reportes_red),
        'casas_pendientes': max(0, len(casas_red) - len(reportes_red)),
        'lideres_red': lideres_cards,
    }


# ---------------------------------------------------------------------------
# Vista Casa de Paz
# ---------------------------------------------------------------------------
def get_mock_cdp(cdp_id):
    """Métricas mock para la vista de una Casa de Paz específica."""
    casas = get_casas_demo()
    cdp = next((c for c in casas if str(c['id']) == str(cdp_id)), casas[0])
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
            'ofrenda': r['ofrendas'],
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
            {'fecha': '2026-08-24', 'asistencia': cdp['asistencia'], 'ninos': 4, 'visitas': 2, 'ofrenda': 20.0, 'ofrendas_usd': 20.0, 'ofrendas_bs': 360.0, 'observaciones': 'Reunión de edificación.'}
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
        'promedio_historico': round(sum(h['asistencia'] for h in historial) / len(historial)),
        'visitas': sum(h['visitas'] for h in historial),
        'conversiones': 3,
        'ofrendas_usd': sum(h['ofrendas_usd'] for h in historial),
        'ofrendas_bs': sum(h['ofrendas_bs'] for h in historial),
        'estado_reporte': 'enviado',
        'ultimo_reporte_por': f"{lider_nombre} (Líder)",
        'ultimo_reporte_fecha': reps[0]['fecha_formateada'] if reps else '24 Ago 2026',
        'ultimo_tema': reps[0]['tema'] if reps else 'El Poder de la Fe',
        'hr_inicio': '19:00',
        'hr_fin': '20:30',
        'cesta_amor': True,
        'potencial_multiplicacion': True,
        'distribucion': {
            'regulares': 10,
            'ninos': 4,
            'visitas': 3,
            'comprometidos': 1,
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
    cdp = next((c for c in casas if str(c['id']) == str(cdp_id)), casas[0])
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

    return {
        'id': cid,
        'codigo': cdp['codigo'],
        'nombre': cdp['nombre'],
        'red_nombre': cdp['red_nombre'],
        'supervisor_nombre': cdp['supervisor'],
        'direccion': direccion,
        'maps_url': f"https://www.google.com/maps/search/?api=1&query={maps_query}",
        'anfitrion': cdp['anfitrion'],
        'lider_nombre': lider_principal,
        'telefono': telefono_contacto,
        'telefono_wa': re.sub(r'\D', '', telefono_contacto),
        'estado': cdp['estado'],
        'horario': cdp['horario'],
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
        'cumplimiento': 0,
        'ofrendas': 0,
        'ofrendas_usd': 0,
        'ofrendas_bs': 0,
        'conversiones': 0,
        'reconciliaciones': 0,
        'cestas_amor': 0,
        'total_visitas': 0,
        'total_casas': 0,
        'casas_con_reporte': 0,
        'reportes_enviados': 0,
        'distribucion': {
            'regulares': 0,
            'ninos': 0,
            'visitas': 0,
            'comprometidos': 0,
        },
        'tendencia_semanas': [],
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
        'promedio_casa': 0,
        'ninos': 0,
        'conversiones': 0,
        'ofrendas': 0,
        'ofrendas_usd': 0,
        'ofrendas_bs': 0,
        'cumplimiento': 0,
        'casas_con_reporte': 0,
        'casas_pendientes': 0,
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
        'promedio_historico': 0,
        'visitas': 0,
        'conversiones': 0,
        'ofrendas_usd': 0,
        'ofrendas_bs': 0,
        'estado_reporte': 'pendiente',
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

