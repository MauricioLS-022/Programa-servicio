"""
Tests unitarios y de integración para la optimización del Dashboard:
1. R1: Tendencia de asistencia semanal coherente (6-8 semanas consecutivas con formato de fecha corta).
2. R2: Tooltips accesibles e interactivos en barras y donut (estructura DOM y ARIA).
3. R3: Restricción del ranking de redes al podio de los 3 primeros (#1, #2, #3).
4. R4: Unificación de métricas a la semana activa y coherencia de datos entre niveles.
"""
import unittest
from datetime import date, datetime, timedelta
from unittest.mock import patch, MagicMock
from app import app
import mock_data
import db_queries
from services.dashboard_service import sanitize_metricas, get_dashboard_context


from utils.cache import invalidate_dashboard_cache


class TestDashboardMetricsAndVisuals(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.client = app.test_client()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        invalidate_dashboard_cache()

    def tearDown(self):
        invalidate_dashboard_cache()

    # -------------------------------------------------------------------------
    # Helper de formateo de fecha corta
    # -------------------------------------------------------------------------
    def test_formatear_fecha_corta_valid_dates(self):
        """Verifica que fechas tipo date o datetime se formateen correctamente en formato corto ('dd Mes')."""
        d = date(2026, 9, 14)
        formatted = mock_data.formatear_fecha_corta(d)
        self.assertEqual(formatted, "14 Sep")

        dt = datetime(2026, 8, 28, 10, 30)
        formatted_dt = db_queries.formatear_fecha_corta(dt)
        self.assertEqual(formatted_dt, "28 Ago")

        d_str = "2026-05-04"
        formatted_str = mock_data.formatear_fecha_corta(d_str)
        self.assertEqual(formatted_str, "04 May")

    def test_formatear_fecha_corta_fallbacks(self):
        """Verifica que fechas None o inválidas retornen un fallback seguro sin crashear."""
        self.assertEqual(mock_data.formatear_fecha_corta(None), "")
        self.assertEqual(db_queries.formatear_fecha_corta("invalido"), "invalido")

    # -------------------------------------------------------------------------
    # R1 & R4: Mock Data General - Coherencia semanal, distribución y tendencia
    # -------------------------------------------------------------------------
    def test_mock_generales_distribution_and_kpi_consistency(self):
        """El total de asistencia semanal debe coincidir exactamente con la suma de la distribución."""
        data = mock_data.get_mock_generales()
        dist = data['distribucion']
        suma_dist = dist['regulares'] + dist['ninos'] + dist['visitas'] + dist['comprometidos']

        self.assertEqual(data['total_asistencia'], suma_dist,
                         "El total_asistencia KPI general debe igualar a la suma de la distribución donut")
        self.assertGreater(data['total_asistencia'], 0)

    def test_mock_generales_weekly_trend(self):
        """La tendencia debe contener 8 semanas consecutivas con fechas cortas y porcentajes relativos al pico."""
        data = mock_data.get_mock_generales()
        tendencia = data['tendencia_semanas']

        self.assertEqual(len(tendencia), 8, "Debe retornar 8 semanas históricas")
        max_asist = max(item['asistencia'] for item in tendencia)

        for item in tendencia:
            self.assertIn('semana', item)
            self.assertIn('asistencia', item)
            self.assertIn('porcentaje', item)
            self.assertIn('fecha_completa', item)
            self.assertLessEqual(item['porcentaje'], 100)
            self.assertGreaterEqual(item['porcentaje'], 0)
            # El pico debe tener porcentaje 100
            if item['asistencia'] == max_asist:
                self.assertEqual(item['porcentaje'], 100)

    # -------------------------------------------------------------------------
    # R3: Restricción del Ranking de Redes al Top 3
    # -------------------------------------------------------------------------
    def test_mock_generales_ranking_restricted_to_top_3(self):
        """El ranking de redes retornado debe tener como máximo 3 posiciones."""
        data = mock_data.get_mock_generales()
        ranking = data['ranking_redes']
        self.assertLessEqual(len(ranking), 3, "El ranking no debe exceder de 3 redes")

    def test_sanitize_metricas_enforces_top_3_and_default_trend(self):
        """sanitize_metricas debe forzar que ranking_redes se limite a 3 y tendencia_semanas exista."""
        metricas_raw = {
            'ranking_redes': [
                {'nombre': 'Red 1', 'asistencia': 50},
                {'nombre': 'Red 2', 'asistencia': 40},
                {'nombre': 'Red 3', 'asistencia': 30},
                {'nombre': 'Red 4', 'asistencia': 20},
                {'nombre': 'Red 5', 'asistencia': 10},
            ]
        }
        sanitized = sanitize_metricas(metricas_raw)
        self.assertEqual(len(sanitized['ranking_redes']), 3)
        self.assertIn('tendencia_semanas', sanitized)
        self.assertEqual(sanitized['tendencia_semanas'], [])

    def test_sanitize_metricas_handles_none_and_empty(self):
        """sanitize_metricas debe ser resiliente a None y diccionarios vacíos."""
        res = sanitize_metricas(None)
        self.assertIsInstance(res, dict)
        self.assertEqual(res['ranking_redes'], [])
        self.assertEqual(res['tendencia_semanas'], [])

        empty = sanitize_metricas({})
        self.assertEqual(empty['ranking_redes'], [])
        self.assertEqual(empty['tendencia_semanas'], [])

    # -------------------------------------------------------------------------
    # R4: Mock Data Red & CDP - Consolidación semanal y coherencia
    # -------------------------------------------------------------------------
    def test_mock_red_consistency_with_houses_and_distribution(self):
        """En nivel Red, el total de asistencia debe coincidir con la suma de casas y con la distribución."""
        data = mock_data.get_mock_red(1)
        dist = data['distribucion']
        suma_dist = dist['regulares'] + dist['ninos'] + dist['visitas'] + dist['comprometidos']

        self.assertEqual(data['total_asistencia'], suma_dist,
                         "El total_asistencia de la red debe coincidir con la suma de la distribución")

        # Suma de asistencia de las casas del listado
        casas = data['casas']
        suma_casas = sum(c['asistencia'] for c in casas)
        self.assertEqual(data['total_asistencia'], suma_casas,
                         "El total_asistencia de la red debe coincidir con la suma de asistencia de sus casas")

    def test_mock_cdp_consistency(self):
        """En nivel CDP, la distribución debe sumar la asistencia reportada."""
        data = mock_data.get_mock_cdp(1)
        dist = data['distribucion']
        suma_dist = dist['regulares'] + dist['ninos'] + dist['visitas'] + dist['comprometidos']
        self.assertEqual(data['total_asistencia'], suma_dist,
                         "En nivel CDP, total_asistencia debe coincidir con la suma de su distribución")

    # -------------------------------------------------------------------------
    # R2 & R3: Renderizado HTML - Tooltips accesibles, SVG y Podio
    # -------------------------------------------------------------------------
    @patch('services.dashboard_service.mock_mode_enabled', return_value=True)
    def test_admin_dashboard_render_contains_accessible_tooltips_and_podium(self, mock_enabled):
        """La vista general renderizada debe incluir los elementos de tooltip de barras, donut y podio."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'admin-test-uuid'
            sess['rol'] = 'admin'
            sess['usuario'] = 'Administrador Test'

        response = self.client.get('/admin/dashboard?nivel=general')
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)

        # R1: Contenedor y barras de tendencia
        self.assertIn('trend-bars-container', html)
        self.assertIn('trend-bar-col', html)
        self.assertIn('trend-tooltip', html)
        self.assertIn('role="tooltip"', html)
        self.assertIn('role="graphics-symbol"', html)

        # R2: Donut y tooltips de leyenda
        self.assertIn('donut-wrapper', html)
        self.assertIn('donut-ring', html)
        self.assertIn('donut-tooltip', html)
        self.assertIn('legend-tooltip', html)

        # R3: Podio top 3
        self.assertIn('podium-1', html)
        self.assertIn('pos-1', html)

    # -------------------------------------------------------------------------
    # Edge Cases: Ranking de Redes (0, 1, 2, 3, >3 redes)
    # -------------------------------------------------------------------------
    def test_ranking_redes_with_zero_networks(self):
        """Si hay 0 redes, debe renderizarse el estado vacío sin romper el diseño."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'admin-test'
            sess['rol'] = 'admin'
            sess['usuario'] = 'Admin'

        with patch('services.dashboard_service.get_metricas') as mock_m:
            mock_m.return_value = {
                **sanitize_metricas({
                    'total_asistencia': 0,
                    'total_casas': 0,
                    'ranking_redes': [],
                    'distribucion': {'regulares': 0, 'ninos': 0, 'visitas': 0, 'comprometidos': 0},
                    'tendencia_semanas': [],
                }),
                'mock_used': False,
            }
            response = self.client.get('/admin/dashboard?nivel=general')
            self.assertEqual(response.status_code, 200)
            html = response.get_data(as_text=True)
            self.assertIn('Aún no hay redes con reportes para comparar.', html)
            self.assertNotIn('podium-1', html)

    def test_ranking_redes_with_one_and_two_networks(self):
        """Con 1 o 2 redes, el podio debe mostrar únicamente los puestos existentes sin romper el diseño."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'admin-test'
            sess['rol'] = 'admin'
            sess['usuario'] = 'Admin'

        # Caso: 1 sola red
        with patch('services.dashboard_service.get_metricas') as mock_m:
            mock_m.return_value = {
                **sanitize_metricas({
                    'total_asistencia': 15,
                    'total_casas': 1,
                    'ranking_redes': [
                        {'nombre': 'Red Única', 'asistencia': 15, 'cumplimiento': 100, 'supervisor': 'Sup 1', 'color_class': 'hebron'}
                    ],
                    'distribucion': {'regulares': 10, 'ninos': 3, 'visitas': 1, 'comprometidos': 1},
                    'tendencia_semanas': [],
                }),
                'mock_used': False,
            }
            res = self.client.get('/admin/dashboard?nivel=general')
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)
            self.assertIn('podium-1', html)
            self.assertIn('pos-1', html)
            self.assertNotIn('podium-2', html)
            self.assertNotIn('pos-2', html)

        # Caso: 2 redes
        with patch('services.dashboard_service.get_metricas') as mock_m:
            mock_m.return_value = {
                **sanitize_metricas({
                    'total_asistencia': 35,
                    'total_casas': 2,
                    'ranking_redes': [
                        {'nombre': 'Red Oro', 'asistencia': 25, 'cumplimiento': 100, 'supervisor': 'Sup A', 'color_class': 'hebron'},
                        {'nombre': 'Red Plata', 'asistencia': 10, 'cumplimiento': 50, 'supervisor': 'Sup B', 'color_class': 'sur'},
                    ],
                    'distribucion': {'regulares': 20, 'ninos': 5, 'visitas': 5, 'comprometidos': 5},
                    'tendencia_semanas': [],
                }),
                'mock_used': False,
            }
            res2 = self.client.get('/admin/dashboard?nivel=general')
            self.assertEqual(res2.status_code, 200)
            html2 = res2.get_data(as_text=True)
            self.assertIn('podium-1', html2)
            self.assertIn('podium-2', html2)
            self.assertNotIn('podium-3', html2)

    def test_ranking_redes_with_more_than_three_networks(self):
        """Con más de 3 redes registradas, se restringe estrictamente a los 3 primeros."""
        raw = {
            'ranking_redes': [
                {'nombre': f'Red {i}', 'asistencia': 100 - i * 10, 'cumplimiento': 100 - i * 5}
                for i in range(1, 8)
            ]
        }
        sanitized = sanitize_metricas(raw)
        self.assertEqual(len(sanitized['ranking_redes']), 3)
        self.assertEqual(sanitized['ranking_redes'][0]['nombre'], 'Red 1')
        self.assertEqual(sanitized['ranking_redes'][2]['nombre'], 'Red 3')

    # -------------------------------------------------------------------------
    # Edge Cases: Tendencia Semanal (0, 1, >8 semanas, asistencia en 0)
    # -------------------------------------------------------------------------
    def test_weekly_trend_zero_and_single_week(self):
        """Tendencia con 0 y 1 semana no debe crashear y debe renderizar adecuadamente."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'admin-test'
            sess['rol'] = 'admin'
            sess['usuario'] = 'Admin'

        # 0 semanas
        with patch('services.dashboard_service.get_metricas') as mock_m:
            mock_m.return_value = {
                **sanitize_metricas({
                    'total_asistencia': 0,
                    'total_casas': 0,
                    'tendencia_semanas': [],
                    'ranking_redes': [],
                    'distribucion': {'regulares': 0, 'ninos': 0, 'visitas': 0, 'comprometidos': 0},
                }),
                'mock_used': False,
            }
            res = self.client.get('/admin/dashboard?nivel=general')
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)
            self.assertIn('Aún no hay reportes para mostrar una tendencia.', html)

        # 1 semana (sin error de división por cero en variación ni en porcentaje)
        with patch('services.dashboard_service.get_metricas') as mock_m:
            mock_m.return_value = {
                **sanitize_metricas({
                    'total_asistencia': 40,
                    'total_casas': 1,
                    'tendencia_semanas': [
                        {'semana': '14 Sep', 'asistencia': 40, 'porcentaje': 100, 'fecha_completa': '14 Sep 2026'}
                    ],
                    'ranking_redes': [],
                    'distribucion': {'regulares': 25, 'ninos': 5, 'visitas': 5, 'comprometidos': 5},
                }),
                'mock_used': False,
            }
            res = self.client.get('/admin/dashboard?nivel=general')
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)
            self.assertIn('14 Sep', html)
            self.assertIn('40', html)

    def test_weekly_trend_zero_attendance_across_all_weeks(self):
        """Semanas con asistencia 0 no deben provocar ZeroDivisionError en cálculos."""
        raw = {
            'tendencia_semanas': [
                {'semana': '01 Sep', 'asistencia': 0},
                {'semana': '08 Sep', 'asistencia': 0},
                {'semana': '15 Sep', 'asistencia': 0},
            ]
        }
        sanitized = sanitize_metricas(raw)
        for t in sanitized['tendencia_semanas']:
            self.assertEqual(t['porcentaje'], 0)
        self.assertEqual(sanitized['promedio_tendencia'], 0)

    def test_weekly_trend_enforces_max_eight_weeks(self):
        """sanitize_metricas debe recortar la tendencia a las últimas 8 semanas."""
        raw = {
            'tendencia_semanas': [
                {'semana': f'Sem {i}', 'asistencia': i * 10}
                for i in range(1, 15)
            ]
        }
        sanitized = sanitize_metricas(raw)
        self.assertEqual(len(sanitized['tendencia_semanas']), 8)
        self.assertEqual(sanitized['tendencia_semanas'][-1]['semana'], 'Sem 14')
        self.assertEqual(sanitized['tendencia_semanas'][0]['semana'], 'Sem 7')

    # -------------------------------------------------------------------------
    # Edge Cases: Donut Chart (Todas las categorías en 0, datos vacíos)
    # -------------------------------------------------------------------------
    def test_donut_with_all_zero_categories(self):
        """Distribución con todas las categorías en 0 debe renderizar seguro con 0 en centro y leyenda."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'admin-test'
            sess['rol'] = 'admin'
            sess['usuario'] = 'Admin'

        with patch('services.dashboard_service.get_metricas') as mock_m:
            mock_m.return_value = {
                **sanitize_metricas({
                    'total_asistencia': 0,
                    'total_casas': 1,
                    'distribucion': {'regulares': 0, 'ninos': 0, 'visitas': 0, 'comprometidos': 0},
                    'tendencia_semanas': [],
                    'ranking_redes': [],
                }),
                'mock_used': False,
            }
            res = self.client.get('/admin/dashboard?nivel=general')
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)
            self.assertIn('data-regular="0"', html)
            self.assertIn('data-ninos="0"', html)
            self.assertIn('data-visitas="0"', html)
            self.assertIn('data-comprometidos="0"', html)

    # -------------------------------------------------------------------------
    # R2: Validación de Atributos ARIA en Renderizado
    # -------------------------------------------------------------------------
    def test_aria_describedby_and_tooltip_id_linkage(self):
        """Cada item de leyenda y barra debe tener aria-describedby apuntando al id de su tooltip."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'admin-test'
            sess['rol'] = 'admin'
            sess['usuario'] = 'Admin'

        with patch('services.dashboard_service.mock_mode_enabled', return_value=True):
            response = self.client.get('/admin/dashboard?nivel=general')
            html = response.get_data(as_text=True)

            # Barras de tendencia: aria-describedby="trend-tip-1" -> id="trend-tip-1"
            self.assertIn('aria-describedby="trend-tip-1"', html)
            self.assertIn('id="trend-tip-1"', html)

            # Leyenda General: aria-describedby="legend-tip-reg-gen" -> id="legend-tip-reg-gen"
            self.assertIn('aria-describedby="legend-tip-reg-gen"', html)
            self.assertIn('id="legend-tip-reg-gen"', html)
            self.assertIn('aria-describedby="legend-tip-nin-gen"', html)
            self.assertIn('id="legend-tip-nin-gen"', html)
            self.assertIn('aria-describedby="legend-tip-vis-gen"', html)
            self.assertIn('id="legend-tip-vis-gen"', html)
            self.assertIn('aria-describedby="legend-tip-com-gen"', html)
            self.assertIn('id="legend-tip-com-gen"', html)

    # -------------------------------------------------------------------------
    # Integridad Real MySQL (si está activo el servicio)
    # -------------------------------------------------------------------------
    def test_real_db_queries_live_if_connected(self):
        """Verifica que las consultas reales de db_queries mantengan coherencia si MySQL está encendido."""
        import pymysql
        try:
            conn = pymysql.connect(
                host='localhost',
                user='root',
                password='',
                database='serv_comunitario',
                cursorclass=pymysql.cursors.DictCursor
            )
        except Exception:
            # Si el servicio local MySQL no está corriendo, omitir sin fallar suite
            self.skipTest("MySQL no disponible localmente para live test")
            return

        try:
            # 1. Vista General
            mg = db_queries.get_metricas_generales(conn)
            dist_g = mg['distribucion']
            sum_g = dist_g['regulares'] + dist_g['ninos'] + dist_g['visitas'] + dist_g['comprometidos']
            self.assertEqual(mg['total_asistencia'], sum_g, "Suma de distribución debe igualar a total_asistencia")
            self.assertLessEqual(len(mg['ranking_redes']), 3, "Ranking en BD real debe ser máx 3")
            self.assertLessEqual(len(mg['tendencia_semanas']), 8, "Tendencia semanal en BD real debe ser máx 8")
            self.assertIn('promedio_tendencia', mg)
            self.assertIn('tendencia', mg)

            # 2. Vista Red (si existe red 1)
            mr = db_queries.get_metricas_red(conn, 1)
            if mr:
                self.assertEqual(mr['total_asistencia'], mr['asistencia_total'],
                                 "total_asistencia debe ser alias idéntico de asistencia_total en Red")
                dist_r = mr['distribucion']
                sum_r = dist_r['regulares'] + dist_r['ninos'] + dist_r['visitas'] + dist_r['comprometidos']
                self.assertEqual(mr['asistencia_total'], sum_r, "En Red, asistencia_total debe igualar suma de distribución")

            # 3. Vista CDP (si existe CDP 1)
            mc = db_queries.get_metricas_cdp(conn, 1)
            if mc:
                self.assertEqual(mc['total_asistencia'], mc['asistencia_ultimo'],
                                 "total_asistencia debe ser alias idéntico de asistencia_ultimo en CDP")
                dist_c = mc['distribucion']
                sum_c = dist_c['regulares'] + dist_c['ninos'] + dist_c['visitas'] + dist_c['comprometidos']
                self.assertEqual(mc['asistencia_ultimo'], sum_c, "En CDP, asistencia_ultimo debe igualar suma de distribución")
        finally:
            conn.close()

    # -------------------------------------------------------------------------
    # QA & Hardening: Sanitize metricas malformed types, None handling, edge cases
    # -------------------------------------------------------------------------
    def test_sanitize_metricas_malformed_types_and_lists(self):
        """Verifica que sanitize_metricas tolere cadenas no numéricas, números negativos y listas con elementos no-dict."""
        raw = {
            'total_asistencia': 'invalid',
            'promedio_casa': -5,
            'ofrendas_usd': 'NaN',
            'ofrendas_bs': None,
            'tendencia_semanas': [
                None,
                "texto_invalido",
                123,
                {'semana': '14 Sep', 'asistencia': '50', 'porcentaje': '80.5'},
                {'semana': '21 Sep', 'asistencia': -10, 'porcentaje': -5},
                {'semana': '28 Sep', 'asistencia': 'invalido'},
            ],
            'ranking_redes': [
                None,
                {'nombre': 'Red A', 'asistencia': '45', 'cumplimiento': '90'},
                {'nombre': 'Red B', 'asistencia': -5, 'cumplimiento': -10},
                {'nombre': 'Red C', 'asistencia': 'abc', 'cumplimiento': 'xyz'},
            ],
            'alertas': None,
            'alertas_zonal': None,
            'casas': None,
            'mini_historico': None,
        }
        sanitized = sanitize_metricas(raw)
        self.assertIsInstance(sanitized, dict)
        self.assertEqual(sanitized['total_asistencia'], 0)
        self.assertEqual(sanitized['promedio_casa'], 0.0)
        self.assertEqual(sanitized['ofrendas_usd'], 0.0)
        self.assertEqual(sanitized['ofrendas_bs'], 0.0)

        # Debe haber filtrado elementos no-dict en tendencia_semanas
        self.assertEqual(len(sanitized['tendencia_semanas']), 3)
        self.assertEqual(sanitized['tendencia_semanas'][0]['asistencia'], 50)
        self.assertEqual(sanitized['tendencia_semanas'][1]['asistencia'], 0)
        self.assertEqual(sanitized['tendencia_semanas'][2]['asistencia'], 0)

        # Debe haber filtrado elementos no-dict en ranking_redes y limitado a 3
        self.assertEqual(len(sanitized['ranking_redes']), 3)
        self.assertEqual(sanitized['ranking_redes'][0]['asistencia'], 45)
        self.assertEqual(sanitized['ranking_redes'][0]['cumplimiento'], 90)
        self.assertEqual(sanitized['ranking_redes'][1]['asistencia'], 0)
        self.assertEqual(sanitized['ranking_redes'][1]['cumplimiento'], 0)
        self.assertEqual(sanitized['ranking_redes'][2]['asistencia'], 0)
        self.assertEqual(sanitized['ranking_redes'][2]['cumplimiento'], 0)

        # Listas vacías garantizadas
        self.assertEqual(sanitized['alertas'], [])
        self.assertEqual(sanitized['alertas_zonal'], [])
        self.assertEqual(sanitized['casas'], [])
        self.assertEqual(sanitized['mini_historico'], [])

    def test_mock_data_empty_functions_completeness(self):
        """Verifica que get_empty_generales, get_empty_red y get_empty_cdp tengan todas las claves necesarias."""
        eg = mock_data.get_empty_generales()
        self.assertIn('total_asistencia', eg)
        self.assertIn('asistencia_total', eg)
        self.assertIn('casas_pendientes', eg)
        self.assertIn('total_sin_reporte_7d', eg)
        self.assertIn('distribucion', eg)
        self.assertEqual(eg['distribucion']['regulares'], 0)

        er = mock_data.get_empty_red(1)
        self.assertIn('total_asistencia', er)
        self.assertIn('asistencia_total', er)
        self.assertIn('casas_pendientes', er)
        self.assertIn('total_sin_reporte_7d', er)
        self.assertIn('distribucion', er)

        ec = mock_data.get_empty_cdp(1)
        self.assertIn('total_asistencia', ec)
        self.assertIn('asistencia_ultimo', ec)
        self.assertIn('distribucion', ec)

    def test_template_rendering_resilient_to_none_and_empty_metricas(self):
        """El template dashboard_admin.html no debe fallar con TypeError si las métricas contienen None o están vacías."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'admin-qa'
            sess['rol'] = 'admin'
            sess['usuario'] = 'Admin QA'

        metricas_con_nones = {
            'total_asistencia': None,
            'asistencia_total': None,
            'total_casas': None,
            'cumplimiento': None,
            'reportes_recibidos': None,
            'reportes_esperados': None,
            'casas_pendientes': None,
            'total_sin_reporte_7d': None,
            'promedio_casa': None,
            'ninos': None,
            'visitas': None,
            'conversiones': None,
            'reconciliaciones': None,
            'ofrendas_usd': None,
            'ofrendas_bs': None,
            'cestas_amor': None,
            'total_visitas': None,
            'distribucion': None,
            'tendencia_semanas': None,
            'ranking_redes': None,
            'alertas': None,
            'alertas_zonal': None,
            'casas': None,
            'lideres_red': None,
            'top_crecimiento': None,
            'historial': None,
            'mini_historico': None,
        }

        # Nivel General con None values
        with patch('routes.admin_routes.get_dashboard_context') as mock_ctx:
            mock_ctx.return_value = {
                'nivel': 'general',
                'red_id': None,
                'cdp_id': None,
                'redes': [{'id': 1, 'nombre': 'Red 1'}],
                'casas': [{'id': 1, 'codigo': 'CDP-01', 'nombre': 'CDP 1', 'red_id': 1}],
                'cdps': [{'id': 1, 'codigo': 'CDP-01', 'nombre': 'CDP 1', 'red_id': 1}],
                'metricas': sanitize_metricas(metricas_con_nones),
                'mock_used': True,
            }
            res_gen = self.client.get('/admin/dashboard?nivel=general')
            self.assertEqual(res_gen.status_code, 200, "Nivel general debe renderizar sin crashear con Nones")

        # Nivel Red con None values
        with patch('routes.admin_routes.get_dashboard_context') as mock_ctx:
            mock_ctx.return_value = {
                'nivel': 'red',
                'red_id': 1,
                'cdp_id': None,
                'redes': [{'id': 1, 'nombre': 'Red 1'}],
                'casas': [{'id': 1, 'codigo': 'CDP-01', 'nombre': 'CDP 1', 'red_id': 1}],
                'cdps': [{'id': 1, 'codigo': 'CDP-01', 'nombre': 'CDP 1', 'red_id': 1}],
                'metricas': sanitize_metricas({
                    **metricas_con_nones,
                    'nombre_red': 'Red Test',
                    'supervisor': 'Supervisor Test',
                    'casas_activas': None,
                }),
                'mock_used': True,
            }
            res_red = self.client.get('/admin/dashboard?nivel=red&red_id=1')
            self.assertEqual(res_red.status_code, 200, "Nivel red debe renderizar sin crashear con Nones")

        # Nivel CDP con None values
        with patch('routes.admin_routes.get_dashboard_context') as mock_ctx:
            mock_ctx.return_value = {
                'nivel': 'cdp',
                'red_id': 1,
                'cdp_id': 1,
                'redes': [{'id': 1, 'nombre': 'Red 1'}],
                'casas': [{'id': 1, 'codigo': 'CDP-01', 'nombre': 'CDP 1', 'red_id': 1}],
                'cdps': [{'id': 1, 'codigo': 'CDP-01', 'nombre': 'CDP 1', 'red_id': 1}],
                'metricas': sanitize_metricas({
                    **metricas_con_nones,
                    'nombre_cdp': 'CDP Test',
                    'codigo': 'CDP-01',
                    'lider': 'Lider Test',
                    'sublider': 'Sublider Test',
                    'asistencia_ultimo': None,
                    'promedio_historico': None,
                }),
                'mock_used': True,
            }
            res_cdp = self.client.get('/admin/dashboard?nivel=cdp&red_id=1&cdp_id=1')
            self.assertEqual(res_cdp.status_code, 200, "Nivel cdp debe renderizar sin crashear con Nones")

    def test_formatear_fecha_corta_edge_cases_leap_year_and_rollover(self):
        """Verifica formatear_fecha_corta en años bisiestos, cambios de año, fechas con hora y formatos alternativos."""
        for mod in (mock_data, db_queries):
            # Año bisiesto
            self.assertEqual(mod.formatear_fecha_corta(date(2024, 2, 29)), "29 Feb")
            self.assertEqual(mod.formatear_fecha_corta("2024-02-29"), "29 Feb")
            self.assertEqual(mod.formatear_fecha_corta(" 2024-02-29 "), "29 Feb")
            self.assertEqual(mod.formatear_fecha_corta("29/02/2024"), "29 Feb")

            # Fin de año y cambio de año
            self.assertEqual(mod.formatear_fecha_corta(date(2026, 12, 31)), "31 Dic")
            self.assertEqual(mod.formatear_fecha_corta("2026-12-31"), "31 Dic")
            self.assertEqual(mod.formatear_fecha_corta("31/12/2026"), "31 Dic")
            self.assertEqual(mod.formatear_fecha_corta("2026/12/31"), "31 Dic")
            self.assertEqual(mod.formatear_fecha_corta(date(2027, 1, 1)), "01 Ene")
            self.assertEqual(mod.formatear_fecha_corta("2027-01-01"), "01 Ene")
            self.assertEqual(mod.formatear_fecha_corta("01/01/2027"), "01 Ene")

            # Datetime con hora
            self.assertEqual(mod.formatear_fecha_corta(datetime(2026, 8, 28, 19, 45, 12)), "28 Ago")
            self.assertEqual(mod.formatear_fecha_corta("2026-08-28 19:45:12"), "28 Ago")

            # Fallbacks seguros
            self.assertEqual(mod.formatear_fecha_corta(None), "")
            self.assertEqual(mod.formatear_fecha_corta(""), "")
            self.assertEqual(mod.formatear_fecha_corta(12345), "12345")
            self.assertEqual(mod.formatear_fecha_corta("texto-no-fecha"), "texto-no-fecha")

    def test_sanitize_metricas_tendencia_clamping_and_zero_peak_recalibration(self):
        """Verifica que tendencia_semanas se limite a 8 semanas y se recalibren porcentajes relativos al pico del periodo."""
        # 1. Clamping de >8 semanas a exactamente las últimas 8
        items = [{'semana': f'Sem {i}', 'asistencia': i * 10} for i in range(1, 13)]
        res = sanitize_metricas({'tendencia_semanas': items})
        self.assertEqual(len(res['tendencia_semanas']), 8)
        self.assertEqual(res['tendencia_semanas'][0]['semana'], 'Sem 5')
        self.assertEqual(res['tendencia_semanas'][-1]['semana'], 'Sem 12')

        # El pico de las 8 semanas restantes es 120 (Sem 12) -> debe ser 100%
        self.assertEqual(res['tendencia_semanas'][-1]['porcentaje'], 100)
        # Sem 5 (asistencia 50 / 120 * 100) -> 42%
        self.assertEqual(res['tendencia_semanas'][0]['porcentaje'], 42)

        # 2. Todas las asistencias en 0 -> todos los porcentajes en 0%
        items_cero = [{'semana': f'Sem {i}', 'asistencia': 0, 'porcentaje': 80} for i in range(1, 6)]
        res_cero = sanitize_metricas({'tendencia_semanas': items_cero})
        self.assertEqual(len(res_cero['tendencia_semanas']), 5)
        for it in res_cero['tendencia_semanas']:
            self.assertEqual(it['asistencia'], 0)
            self.assertEqual(it['porcentaje'], 0)
        self.assertEqual(res_cero['promedio_tendencia'], 0)

    def test_template_rendering_with_numeric_strings_and_integer_telephones(self):
        """El template dashboard_admin.html no debe fallar cuando los teléfonos son enteros y las ofrendas cadenas numéricas."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'admin-qa'
            sess['rol'] = 'admin'
            sess['usuario'] = 'Admin QA'

        metricas_con_tipos = {
            'total_asistencia': 30,
            'total_casas': 2,
            'cumplimiento': 100,
            'ofrendas_usd': '125.50',
            'ofrendas_bs': '450.00',
            'distribucion': {'regulares': '15', 'ninos': '5', 'visitas': '5', 'comprometidos': '5'},
            'alertas': [
                {
                    'nombre': 'Casa Test',
                    'codigo': 'CP-01',
                    'red': 'Red 1',
                    'lider': 'Lider Test',
                    'dias_sin_reporte': 20,
                    'telefono': 584141112233,  # Entero
                }
            ],
            'ranking_redes': [
                {
                    'nombre': 'Red 1',
                    'supervisor': 'Supervisor 1',
                    'cumplimiento': '100',
                    'asistencia': '30',
                    'asistencia_total': '200',
                    'casas_reportadas': '2',
                    'total_casas': '2',
                    'color_class': 'hebron',
                }
            ],
            'tendencia_semanas': [
                {'semana': '14 Sep', 'asistencia': 30, 'porcentaje': 100, 'fecha_completa': '14 Sep 2026'}
            ],
        }

        with patch('routes.admin_routes.get_dashboard_context') as mock_ctx:
            mock_ctx.return_value = {
                'nivel': 'general',
                'red_id': None,
                'cdp_id': None,
                'redes': [{'id': 1, 'nombre': 'Red 1'}],
                'casas': [{'id': 1, 'codigo': 'CDP-01', 'nombre': 'CDP 1', 'red_id': 1}],
                'metricas': sanitize_metricas(metricas_con_tipos),
                'mock_used': True,
            }
            res = self.client.get('/admin/dashboard?nivel=general')
            self.assertEqual(res.status_code, 200, "Debe renderizar correctamente con números como strings y teléfonos enteros")
            html = res.get_data(as_text=True)
            self.assertIn('$125.50', html)
            self.assertIn('Bs. 450.00', html)
            self.assertIn('wa.me/584141112233', html)

    # -------------------------------------------------------------------------
    # Red sin Casas de Paz en nivel CDP no debe mostrar datos de otra red
    # -------------------------------------------------------------------------
    def test_dashboard_context_red_without_cdps_does_not_leak_other_network_cdp(self):
        """Verifica que una red sin CDPs asignadas en nivel 'cdp' no filtre datos de otra red."""
        from services.dashboard_service import get_dashboard_context

        # Mock selectores con dos redes: Red 1 (con CDPs) y Red 2 (sin CDPs)
        mock_redes = [
            {'id': 1, 'nombre': 'Red Sur', 'supervisor': 'Juan Perez'},
            {'id': 2, 'nombre': 'Elohim', 'supervisor': 'Sin asignar'},
        ]
        mock_casas = [
            {'id': 10, 'codigo': 'CA-3.2', 'nombre': 'CA-3.2', 'anfitrion': 'María Márquez', 'red_id': 1, 'lider': 'María Márquez'},
            {'id': 11, 'codigo': 'CA-3.3', 'nombre': 'CA-3.3', 'anfitrion': 'Pedro Gomez', 'red_id': 1, 'lider': 'Pedro Gomez'},
        ]

        with self.app.test_request_context('/admin/dashboard?nivel=cdp&red_id=2'):
            with patch('services.dashboard_service.get_selectores', return_value=(mock_redes, mock_casas)):
                ctx = get_dashboard_context(usuario_id='admin-uuid', is_supervisor=False, default_nivel='general')
                self.assertEqual(ctx['nivel'], 'cdp')
                self.assertEqual(ctx['red_id'], 2)
                self.assertIsNone(ctx['cdp_id'], "El cdp_id debe ser None para una red que no tiene CDPs")
                self.assertEqual(ctx['metricas'].get('codigo', ''), '', "No debe contener el código de una CDP ajena")
                self.assertEqual(ctx['metricas'].get('nombre_red'), 'Elohim')

    def test_view_cdp_empty_state_rendered_when_no_cdp(self):
        """Verifica que la plantilla renderice el estado vacío cuando nivel='cdp' y cdp_id es None."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'admin-test-uuid'
            sess['rol'] = 'admin'
            sess['usuario'] = 'Administrador Test'

        with patch('routes.admin_routes.get_dashboard_context') as mock_ctx:
            mock_ctx.return_value = {
                'usuario': 'Admin',
                'nivel': 'cdp',
                'red_id': 2,
                'cdp_id': None,
                'redes': [{'id': 2, 'nombre': 'Elohim'}],
                'casas': [{'id': 10, 'codigo': 'CA-3.2', 'nombre': 'CA-3.2', 'red_id': 1}],
                'metricas': {
                    'nombre_red': 'Elohim',
                    'nombre_cdp': 'Casa de Paz',
                    'codigo': '',
                    'total_asistencia': 0,
                    'distribucion': {'regulares': 0, 'ninos': 0, 'visitas': 0, 'comprometidos': 0},
                    'ranking_redes': [],
                    'tendencia_semanas': [],
                    'top_crecimiento': {},
                    'bottom_crecimiento': {},
                },
                'db_connected': True,
                'mock_used': False,
                'sin_red_asignada': False,
            }
            res = self.client.get('/admin/dashboard?nivel=cdp&red_id=2')
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)
            self.assertIn('Sin Casas de Paz Asignadas', html)
            self.assertIn('Elohim', html)
            self.assertNotIn('CA-3.2 - María Márquez', html)

    @patch('services.dashboard_service.mock_mode_enabled', return_value=True)
    def test_view_red_renders_tendencia_and_actividad_reciente_and_no_semaforo(self, mock_enabled):
        """Verifica que la vista de nivel 'red' renderice Tendencia de Asistencia y Actividad Reciente sin el semáforo."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'admin-test-uuid'
            sess['rol'] = 'admin'
            sess['usuario'] = 'Administrador Test'

        response = self.client.get('/admin/dashboard?nivel=red&red_id=1')
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)

        # 1. Semáforo eliminado
        self.assertNotIn('Semáforo de Cumplimiento Zonal', html)
        self.assertNotIn('semaforo-grid', html)

        # 2. Tendencia de Asistencia presente
        self.assertIn('Tendencia de Asistencia', html)
        self.assertIn('trend-tip-red-', html)
        self.assertIn('trend-bars-container', html)

        # 3. Actividad Reciente presente
        self.assertIn('Actividad Reciente', html)
        self.assertIn('activity-feed', html)
        self.assertIn('activity-item', html)
        self.assertIn('activity-avatar', html)
        self.assertIn('activity-badge', html)

    def test_alertas_seguimiento_renders_contador_and_faltan_por_reporte(self):
        """Verifica que Alertas de Seguimiento muestre cuántas faltan por reporte y el badge con el conteo."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'admin-test-uuid'
            sess['rol'] = 'admin'
            sess['usuario'] = 'Administrador Test'

        with patch('routes.admin_routes.get_dashboard_context') as mock_ctx:
            mock_ctx.return_value = {
                'nivel': 'general',
                'red_id': None,
                'cdp_id': None,
                'redes': [{'id': 1, 'nombre': 'Red 1'}],
                'casas': [{'id': 1, 'codigo': 'CA-1', 'nombre': 'Casa 1', 'red_id': 1}],
                'cdps': [{'id': 1, 'codigo': 'CA-1', 'nombre': 'Casa 1', 'red_id': 1}],
                'metricas': {
                    'total_asistencia': 100,
                    'total_casas': 10,
                    'cumplimiento': 50,
                    'casas_con_reporte': 5,
                    'casas_pendientes': 5,
                    'reportes_enviados': 5,
                    'distribucion': {'regulares': 50, 'ninos': 20, 'visitas': 10, 'comprometidos': 20},
                    'tendencia_semanas': [],
                    'ranking_redes': [],
                    'alertas': [
                        {'nombre': 'Casa 1', 'codigo': 'CA-1', 'red': 'Red 1', 'dias_sin_reporte': 18, 'lider': 'Líder 1', 'telefono': '123'},
                        {'nombre': 'Casa 2', 'codigo': 'CA-2', 'red': 'Red 1', 'dias_sin_reporte': 21, 'lider': 'Líder 2', 'telefono': '456'},
                        {'nombre': 'Casa 3', 'codigo': 'CA-3', 'red': 'Red 1', 'dias_sin_reporte': 30, 'lider': 'Líder 3', 'telefono': '789'},
                        {'nombre': 'Casa 4', 'codigo': 'CA-4', 'red': 'Red 1', 'dias_sin_reporte': 40, 'lider': 'Líder 4', 'telefono': '012'},
                    ],
                },
                'mock_used': False,
            }
            res = self.client.get('/admin/dashboard?nivel=general')
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)

            # Badge con número de alertas (4)
            self.assertIn('alert-header-badge', html)
            self.assertIn('Faltan 4 por reporte (&gt;2 sem)', html)

    # -------------------------------------------------------------------------
    # Plan B: Nivel CDP con evaluación semanal (<= 7 días) y trazabilidad
    # -------------------------------------------------------------------------
    def test_get_metricas_cdp_weekly_status_recent_report(self):
        """Verifica que un reporte de hace <= 7 días marque estado_reporte='enviado' y reporte_al_dia=True."""
        hoy = date.today()
        fecha_reciente = hoy - timedelta(days=3)

        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur

        # Mock CDP
        mock_cur.fetchone.side_effect = [
            {'id': 1, 'codigo': 'CDP-01', 'anfitrion': 'Familia Pérez', 'direccion': 'Calle 1', 'telefono': '04141234567', 'usuario_id': None},
            # ultimo reporte
            {
                'id': 10,
                'cdp_id': 1,
                'fecha': fecha_reciente,
                'nro_regulares': 10,
                'nro_niños': 3,
                'nro_visitas': 2,
                'nro_comprometidos': 1,
                'confesiones': 1,
                'ofrendas_usd': 15.0,
                'ofrendas_bs': 300.0,
                'tema': 'El Buen Pastor',
                'hr_inicio': '19:00:00',
                'hr_fin': '20:30:00',
                'cesta_amor': 1,
                'enviado_por_nombre': 'Pedro Líder',
            },
            # promedio_historico
            {'promedio': 16.0},
        ]
        mock_cur.fetchall.side_effect = [
            # lideres
            [{'nombre': 'Pedro', 'apellido': 'Líder', 'rol': 'Lider', 'telefono': '04141234567'}],
            # historial
            [],
            # mini
            [],
        ]

        res = db_queries.get_metricas_cdp(mock_conn, 1)
        self.assertIsNotNone(res)
        self.assertTrue(res['reporte_al_dia'])
        self.assertEqual(res['estado_reporte'], 'enviado')
        self.assertEqual(res['dias_desde_reporte'], 3)
        self.assertEqual(res['asistencia_ultimo'], 16)
        self.assertEqual(res['distribucion']['regulares'], 10)

    def test_get_metricas_cdp_weekly_status_stale_report(self):
        """Verifica que un reporte de hace > 7 días marque estado_reporte='pendiente' pero conserve los datos del servicio."""
        hoy = date.today()
        fecha_antigua = hoy - timedelta(days=12)

        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur

        # Mock CDP
        mock_cur.fetchone.side_effect = [
            {'id': 1, 'codigo': 'CDP-01', 'anfitrion': 'Familia Pérez', 'direccion': 'Calle 1', 'telefono': '04141234567', 'usuario_id': None},
            # ultimo reporte
            {
                'id': 10,
                'cdp_id': 1,
                'fecha': fecha_antigua,
                'nro_regulares': 8,
                'nro_niños': 2,
                'nro_visitas': 1,
                'nro_comprometidos': 1,
                'confesiones': 0,
                'ofrendas_usd': 10.0,
                'ofrendas_bs': 200.0,
                'tema': 'Creciendo en Fe',
                'hr_inicio': '19:00:00',
                'hr_fin': '20:30:00',
                'cesta_amor': 0,
                'enviado_por_nombre': 'Pedro Líder',
            },
            # promedio_historico
            {'promedio': 12.0},
        ]
        mock_cur.fetchall.side_effect = [
            # lideres
            [{'nombre': 'Pedro', 'apellido': 'Líder', 'rol': 'Lider', 'telefono': '04141234567'}],
            # historial
            [],
            # mini
            [],
        ]

        res = db_queries.get_metricas_cdp(mock_conn, 1)
        self.assertIsNotNone(res)
        self.assertFalse(res['reporte_al_dia'])
        self.assertEqual(res['estado_reporte'], 'pendiente')
        self.assertEqual(res['dias_desde_reporte'], 12)
        # Los datos del último servicio se conservan intactos
        self.assertEqual(res['asistencia_ultimo'], 12)
        self.assertEqual(res['distribucion']['regulares'], 8)

    def test_view_cdp_renders_weekly_badges_and_traceability(self):
        """Verifica que la plantilla renderice las nuevas etiquetas semanales para 'Al día' y 'Pendiente'."""
        with self.client.session_transaction() as sess:
            sess['usuario'] = 'admin'
            sess['rol'] = 'admin'
            sess['usuario_id'] = 'admin-uuid'

        # 1. Al día
        with patch('routes.admin_routes.get_dashboard_context') as mock_ctx:
            mock_ctx.return_value = {
                'nivel': 'cdp',
                'red_id': 1,
                'cdp_id': 1,
                'redes': [{'id': 1, 'nombre': 'Red 1'}],
                'casas': [{'id': 1, 'codigo': 'CDP-01', 'nombre': 'CDP 1', 'red_id': 1}],
                'cdps': [{'id': 1, 'codigo': 'CDP-01', 'nombre': 'CDP 1', 'red_id': 1}],
                'metricas': sanitize_metricas({
                    'nombre_cdp': 'CDP Test',
                    'codigo': 'CDP-01',
                    'lider': 'Pedro Líder',
                    'estado_reporte': 'enviado',
                    'reporte_al_dia': True,
                    'dias_desde_reporte': 2,
                    'asistencia_ultimo': 15,
                    'historial': [{'fecha': '2026-09-14', 'asistencia': 15, 'ninos': 3, 'visitas': 2, 'ofrendas_usd': 10, 'ofrendas_bs': 200}],
                    'distribucion': {'regulares': 10, 'ninos': 3, 'visitas': 2, 'comprometidos': 0},
                }),
                'mock_used': True,
            }
            res_env = self.client.get('/admin/dashboard?nivel=cdp&red_id=1&cdp_id=1')
            self.assertEqual(res_env.status_code, 200)
            html_env = res_env.get_data(as_text=True)
            self.assertIn('Al día (Esta semana)', html_env)
            self.assertIn('Reporte de esta semana recibido', html_env)

        # 2. Pendiente pero con reporte previo
        with patch('routes.admin_routes.get_dashboard_context') as mock_ctx:
            mock_ctx.return_value = {
                'nivel': 'cdp',
                'red_id': 1,
                'cdp_id': 1,
                'redes': [{'id': 1, 'nombre': 'Red 1'}],
                'casas': [{'id': 1, 'codigo': 'CDP-01', 'nombre': 'CDP 1', 'red_id': 1}],
                'cdps': [{'id': 1, 'codigo': 'CDP-01', 'nombre': 'CDP 1', 'red_id': 1}],
                'metricas': sanitize_metricas({
                    'nombre_cdp': 'CDP Test',
                    'codigo': 'CDP-01',
                    'lider': 'Pedro Líder',
                    'estado_reporte': 'pendiente',
                    'reporte_al_dia': False,
                    'dias_desde_reporte': 14,
                    'asistencia_ultimo': 12,
                    'historial': [{'fecha': '2026-09-02', 'asistencia': 12, 'ninos': 2, 'visitas': 1, 'ofrendas_usd': 5, 'ofrendas_bs': 100}],
                    'distribucion': {'regulares': 8, 'ninos': 2, 'visitas': 1, 'comprometidos': 1},
                }),
                'mock_used': True,
            }
            res_pend = self.client.get('/admin/dashboard?nivel=cdp&red_id=1&cdp_id=1')
            self.assertEqual(res_pend.status_code, 200)
            html_pend = res_pend.get_data(as_text=True)
            self.assertIn('Pendiente esta semana', html_pend)
            self.assertIn('Reporte de esta semana pendiente', html_pend)
            self.assertIn('hace 14 días', html_pend)


if __name__ == '__main__':
    unittest.main()



