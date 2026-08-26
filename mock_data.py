"""
mock_data.py - Datos de demostración para el dashboard.
Se usan SOLO cuando la base de datos no está disponible (modo demo).
Si la BD está conectada pero vacía, se muestran estados vacíos, NUNCA estos datos.
"""


def get_redes_demo():
    """Lista de redes para los selectores del filtro."""
    return [
        {'id': 1, 'nombre': 'Red Hebrón', 'supervisor': 'Pedro González'},
        {'id': 2, 'nombre': 'Red Sur', 'supervisor': 'María López'},
        {'id': 3, 'nombre': 'Red Central', 'supervisor': 'Carlos Ramírez'},
    ]


def get_casas_demo():
    """Lista de casas de paz para los selectores del filtro."""
    return [
        {'id': 1, 'nombre': 'Casa Bethel', 'codigo': 'HEB-001', 'red_id': 1},
        {'id': 2, 'nombre': 'Casa de Oración Sur', 'codigo': 'SUR-001', 'red_id': 2},
        {'id': 3, 'nombre': 'Casa Nueva Vida', 'codigo': 'CEN-001', 'red_id': 3},
        {'id': 4, 'nombre': 'Casa Luz', 'codigo': 'HEB-002', 'red_id': 1},
    ]


def get_mock_usuarios():
    """Usuarios de demostración para la vista administrativa."""
    return [
        {'id': 'mock-admin', 'username': 'mrodriguez', 'nombre': 'Mateo', 'apellido': 'Rodriguez', 'rol': 'admin', 'is_active': 1},
        {'id': 'mock-supervisor', 'username': 'lmendoza', 'nombre': 'Lucía', 'apellido': 'Mendoza', 'rol': 'supervisor', 'is_active': 1},
        {'id': 'mock-lider', 'username': 'asoler', 'nombre': 'Andrés', 'apellido': 'Soler', 'rol': 'cdp', 'is_active': 0},
    ]


def get_mock_lideres():
    """Líderes de demostración para el directorio administrativo."""
    return [
        {'id': 'mock-leader-1', 'nombre': 'Mateo', 'apellido': 'Rodriguez', 'rol': 'Lider', 'telefono': '+52 55 1234 5678', 'cdp_id': 1, 'cdp_nombre': 'Casa Bethel', 'red_id': 1, 'red_nombre': 'Red Hebrón'},
        {'id': 'mock-leader-2', 'nombre': 'Lucía', 'apellido': 'Mendoza', 'rol': 'Sublider', 'telefono': '+52 55 9876 5432', 'cdp_id': 2, 'cdp_nombre': 'Casa de Oración Sur', 'red_id': 2, 'red_nombre': 'Red Sur'},
        {'id': 'mock-leader-3', 'nombre': 'Andrés', 'apellido': 'Soler', 'rol': 'Sublider', 'telefono': '+52 55 4567 8901', 'cdp_id': 3, 'cdp_nombre': 'Casa Nueva Vida', 'red_id': 3, 'red_nombre': 'Red Central'},
        {'id': 'mock-leader-4', 'nombre': 'Elena', 'apellido': 'Pérez', 'rol': 'Lider', 'telefono': '+52 55 2345 6789', 'cdp_id': 2, 'cdp_nombre': 'Casa de Oración Sur', 'red_id': 2, 'red_nombre': 'Red Sur'},
    ]


# ---------------------------------------------------------------------------
# Vista General
# ---------------------------------------------------------------------------
def get_mock_generales():
    """Métricas mock para la vista general de la iglesia."""
    return {
        'total_asistencia': 1248,
        'cumplimiento': 76,
        'ofrendas': 12450,
        'conversiones': 312,
        'total_casas': 42,
        'reportes_enviados': 32,
        'distribucion': {
            'regulares': 724,
            'ninos': 300,
            'visitas': 124,
            'comprometidos': 100,
        },
        'tendencia_semanas': [
            {'semana': 'Sem 1', 'asistencia': 1080, 'porcentaje': 70},
            {'semana': 'Sem 2', 'asistencia': 1115, 'porcentaje': 74},
            {'semana': 'Sem 3', 'asistencia': 1140, 'porcentaje': 77},
            {'semana': 'Sem 4', 'asistencia': 1180, 'porcentaje': 82},
            {'semana': 'Sem 5', 'asistencia': 1210, 'porcentaje': 86},
            {'semana': 'Sem 6', 'asistencia': 1195, 'porcentaje': 84},
            {'semana': 'Sem 7', 'asistencia': 1230, 'porcentaje': 89},
            {'semana': 'Sem 8', 'asistencia': 1248, 'porcentaje': 92},
        ],
        'ranking_redes': [
            {'nombre': 'Red Central', 'cumplimiento': 88, 'asistencia': 490, 'supervisor': 'Carlos Ramírez', 'color_class': 'central'},
            {'nombre': 'Red Sur', 'cumplimiento': 82, 'asistencia': 410, 'supervisor': 'María López', 'color_class': 'sur'},
            {'nombre': 'Red Hebrón', 'cumplimiento': 65, 'asistencia': 348, 'supervisor': 'Pedro González', 'color_class': 'hebron'},
        ],
        'alertas': [
            {'nombre': 'Casa Luz', 'codigo': 'HEB-002', 'red': 'Red Hebrón', 'dias_sin_reporte': 18, 'lider': 'Roberto M.', 'telefono': '+584241122334'},
            {'nombre': 'Casa de Oración Sur', 'codigo': 'SUR-001', 'red': 'Red Sur', 'dias_sin_reporte': 15, 'lider': 'Elena D.', 'telefono': '+584129988776'},
        ],
    }


# ---------------------------------------------------------------------------
# Vista Red
# ---------------------------------------------------------------------------
def get_mock_red(red_id):
    """Métricas mock para la vista de una red específica."""
    redes = get_redes_demo()
    red = next((r for r in redes if r['id'] == red_id), redes[0])

    return {
        'nombre_red': red['nombre'],
        'red_id': red_id,
        'supervisor': red['supervisor'],
        'casas_activas': 14,
        'asistencia_total': 486,
        'promedio_casa': 38,
        'ninos': 142,
        'ofrendas': 4850,
        'distribucion': {
            'regulares': 266,
            'ninos': 142,
            'visitas': 48,
            'comprometidos': 30,
        },
        'casas': [
            {'nombre': 'Casa Bethel', 'codigo': 'HEB-001', 'asistencia': 47, 'estado': 'verde', 'lider': 'Juan Pérez', 'visitas': 12},
            {'nombre': 'Casa Shalom', 'codigo': 'HEB-003', 'asistencia': 35, 'estado': 'amarillo', 'lider': 'Marcos V.', 'visitas': 6},
            {'nombre': 'Casa Luz', 'codigo': 'HEB-002', 'asistencia': 22, 'estado': 'rojo', 'lider': 'Roberto M.', 'visitas': 2},
        ],
        'alertas_zonal': [
            {'nombre': 'Casa Luz', 'codigo': 'HEB-002', 'dias_sin_reporte': 18, 'motivo': '2 semanas sin reporte', 'lider': 'Roberto M.', 'telefono': '+584240001122'},
        ],
        'top_crecimiento': {
            'nombre': 'Casa Bethel',
            'codigo': 'HEB-001',
            'tasa': '+12%',
            'visitas': 12,
            'lider': 'Juan Pérez',
        },
        'supervisores': [
            {'nombre': red['supervisor'], 'rol': 'Supervisor Principal', 'telefono': '+584121234567'},
            {'nombre': 'Carmen Ruiz', 'rol': 'Asistente Zonal', 'telefono': '+584147654321'},
        ],
    }


# ---------------------------------------------------------------------------
# Vista Casa de Paz
# ---------------------------------------------------------------------------
def get_mock_cdp(cdp_id):
    """Métricas mock para la vista de una Casa de Paz específica."""
    casas = get_casas_demo()
    cdp = next((c for c in casas if c['id'] == cdp_id), casas[0])

    return {
        'nombre_cdp': cdp['nombre'],
        'codigo': cdp['codigo'],
        'lider': 'Juan Pérez',
        'sublider': 'Ana García',
        'anfitrion': 'Familia Morales',
        'telefono_contacto': '+584141112233',
        'direccion': 'Calle Principal #123, Sector Norte',
        'asistencia_ultimo': 47,
        'promedio_historico': 42,
        'visitas': 28,
        'conversiones': 8,
        'estado_reporte': 'enviado',
        'ultimo_reporte_por': 'Juan Pérez (Líder)',
        'ultimo_reporte_fecha': '10 Ago 2026',
        'potencial_multiplicacion': True,
        'distribucion': {
            'regulares': 30,
            'ninos': 12,
            'visitas': 5,
            'comprometidos': 0,
        },
        'historial': [
            {'fecha': '2026-08-10', 'asistencia': 47, 'ninos': 12, 'visitas': 5, 'ofrenda': 450, 'observaciones': 'Excelente asistencia familiar y comunitaria. Se recibieron 2 nuevas visitas que mostraron gran interés en integrarse al grupo.'},
            {'fecha': '2026-08-03', 'asistencia': 44, 'ninos': 10, 'visitas': 3, 'ofrenda': 380, 'observaciones': 'Estudio de tema sobre fe y servicio. Ambiente de comunión.'},
            {'fecha': '2026-07-27', 'asistencia': 41, 'ninos': 9, 'visitas': 4, 'ofrenda': 420, 'observaciones': 'Reunión de oración y testimonios.'},
            {'fecha': '2026-07-20', 'asistencia': 45, 'ninos': 11, 'visitas': 6, 'ofrenda': 510, 'observaciones': 'Celebración especial con participación de jóvenes.'},
        ],
        'mini_historico': [
            {'fecha': '20 Jul', 'asistencia': 45, 'altura': 80},
            {'fecha': '27 Jul', 'asistencia': 41, 'altura': 72},
            {'fecha': '03 Ago', 'asistencia': 44, 'altura': 78},
            {'fecha': '10 Ago', 'asistencia': 47, 'altura': 85},
        ],
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
        'conversiones': 0,
        'total_casas': 0,
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
        'nombre_red': 'Red',
        'red_id': red_id,
        'supervisor': '',
        'casas_activas': 0,
        'asistencia_total': 0,
        'promedio_casa': 0,
        'ninos': 0,
        'ofrendas': 0,
        'distribucion': {
            'regulares': 0,
            'ninos': 0,
            'visitas': 0,
            'comprometidos': 0,
        },
        'casas': [],
        'alertas_zonal': [],
        'top_crecimiento': {},
        'supervisores': [],
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
        'estado_reporte': 'pendiente',
        'ultimo_reporte_por': '',
        'ultimo_reporte_fecha': '',
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


def get_mock_reportes():
    """Reportes de demostración para la vista administrativa y de supervisores."""
    return [
        {
            'id': 'mock-rep-1',
            'fecha': '2023-10-24',
            'fecha_formateada': '24 Oct 2023',
            'lider_nombre': 'Ricardo Molina',
            'iniciales': 'RM',
            'avatar_class': 'bg-primary-light text-primary',
            'cdp_id': 1,
            'cdp_nombre': 'Bethel - Sector Sur',
            'red_id': 2,
            'red_nombre': 'Red Sur',
            'hr_inicio': '18:00',
            'hr_fin': '20:00',
            'nro_regulares': 15,
            'nro_niños': 5,
            'nro_visitas': 3,
            'nro_comprometidos': 1,
            'asistencia': 24,
            'reconciliaciones': 2,
            'confesiones': 1,
            'ofrendas': 1250.00,
            'cesta_amor': 1,
            'cesta_amor_desc': 'Canasta básica familiar',
            'tema': 'El poder del perdón',
            'observaciones': 'Testimonio de sanidad al finalizar',
        },
        {
            'id': 'mock-rep-2',
            'fecha': '2023-10-22',
            'fecha_formateada': '22 Oct 2023',
            'lider_nombre': 'Elena Pérez',
            'iniciales': 'EP',
            'avatar_class': 'bg-secondary-light text-secondary',
            'cdp_id': 2,
            'cdp_nombre': 'Sion - Los Olivos',
            'red_id': 1,
            'red_nombre': 'Red Hebrón',
            'hr_inicio': '18:30',
            'hr_fin': '20:30',
            'nro_regulares': 10,
            'nro_niños': 4,
            'nro_visitas': 2,
            'nro_comprometidos': 2,
            'asistencia': 18,
            'reconciliaciones': 1,
            'confesiones': 0,
            'ofrendas': 840.50,
            'cesta_amor': 1,
            'cesta_amor_desc': 'Ropa para niños',
            'tema': 'Fe inquebrantable',
            'observaciones': 'Se recibieron 2 nuevos visitantes',
        },
        {
            'id': 'mock-rep-3',
            'fecha': '2023-10-20',
            'fecha_formateada': '20 Oct 2023',
            'lider_nombre': 'David Sánchez',
            'iniciales': 'DS',
            'avatar_class': 'bg-primary-light text-primary',
            'cdp_id': 3,
            'cdp_nombre': 'Manantial - Centro',
            'red_id': 3,
            'red_nombre': 'Red Central',
            'hr_inicio': '17:00',
            'hr_fin': '19:30',
            'nro_regulares': 20,
            'nro_niños': 6,
            'nro_visitas': 3,
            'nro_comprometidos': 2,
            'asistencia': 31,
            'reconciliaciones': 3,
            'confesiones': 2,
            'ofrendas': 2100.00,
            'cesta_amor': 1,
            'cesta_amor_desc': 'Alimentos no perecederos',
            'tema': 'Discipulado y comunidad',
            'observaciones': 'Reunión especial de jóvenes',
        },
        {
            'id': 'mock-rep-4',
            'fecha': '2023-10-19',
            'fecha_formateada': '19 Oct 2023',
            'lider_nombre': 'Ricardo Molina',
            'iniciales': 'RM',
            'avatar_class': 'bg-secondary-light text-secondary',
            'cdp_id': 1,
            'cdp_nombre': 'Bethel - Sector Sur',
            'red_id': 2,
            'red_nombre': 'Red Sur',
            'hr_inicio': '18:00',
            'hr_fin': '20:00',
            'nro_regulares': 12,
            'nro_niños': 4,
            'nro_visitas': 4,
            'nro_comprometidos': 2,
            'asistencia': 22,
            'reconciliaciones': 1,
            'confesiones': 1,
            'ofrendas': 1100.00,
            'cesta_amor': 1,
            'cesta_amor_desc': 'Manteca, arroz, azúcar',
            'tema': 'La oración transforma',
            'observaciones': 'Visitas se integraron al grupo',
        },
    ]

