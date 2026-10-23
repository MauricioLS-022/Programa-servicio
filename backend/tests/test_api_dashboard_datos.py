"""
tests/test_api_dashboard_datos.py - Pruebas de integración para el endpoint REST /api/dashboard/datos.
Valida:
1. Agregaciones y coherencia matemática de métricas con BD conectada.
2. Comportamiento en modo demo (MOCK_MODE=True) y estructura neutral sin BD (MOCK_MODE=False).
3. Aislamiento territorial estricto y anti-IDOR para rol supervisor.
4. Coerción de parámetros y resiliencia ante inputs malformados.
"""
import unittest
from unittest.mock import patch, MagicMock
from app import app
from utils.cache import invalidate_dashboard_cache


class TestApiDashboardDatosIntegration(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        invalidate_dashboard_cache()

    def tearDown(self):
        invalidate_dashboard_cache()

    # -------------------------------------------------------------------------
    # 1. Base de datos conectada: Contrato y coherencia de datos
    # -------------------------------------------------------------------------
    @patch('services.dashboard_service.get_db_connection')
    @patch('services.dashboard_service.get_metricas_generales')
    def test_api_dashboard_datos_db_connected_general(self, mock_get_gen, mock_db):
        """Con BD conectada, /api/dashboard/datos debe retornar datos reales con mock_used=False."""
        mock_conn = MagicMock()
        mock_db.return_value = mock_conn

        mock_get_gen.return_value = {
            'total_asistencia': 120,
            'total_casas': 10,
            'casas_con_reporte': 8,
            'cumplimiento': 80,
            'ofrendas_usd': 350.5,
            'ofrendas_bs': 12500.0,
            'conversiones': 15,
            'distribucion': {
                'regulares': 60,
                'ninos': 25,
                'visitas': 20,
                'comprometidos': 15,
            },
            'ranking_redes': [
                {'nombre': 'Red Hebrón', 'asistencia': 50, 'cumplimiento': 90, 'supervisor': 'Pedro G'},
                {'nombre': 'Red Sur', 'asistencia': 40, 'cumplimiento': 85, 'supervisor': 'María L'},
                {'nombre': 'Red Central', 'asistencia': 30, 'cumplimiento': 70, 'supervisor': 'Carlos R'},
            ],
            'tendencia_semanas': [
                {'semana': 'Red Hebrón', 'asistencia': 50, 'porcentaje': 100},
                {'semana': 'Red Sur', 'asistencia': 40, 'porcentaje': 80},
                {'semana': 'Red Central', 'asistencia': 30, 'porcentaje': 60},
            ]
        }

        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'admin-uuid-1'
            sess['usuario'] = 'admin'
            sess['rol'] = 'admin'

        res = self.client.get('/api/dashboard/datos?nivel=general&periodo=semana')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, dict)
        self.assertFalse(data.get('mock_used'))
        self.assertEqual(data.get('total_asistencia'), 120)

        # Verificación de coherencia matemática: suma distribución = total_asistencia
        dist = data.get('distribucion', {})
        suma_dist = dist.get('regulares', 0) + dist.get('ninos', 0) + dist.get('visitas', 0) + dist.get('comprometidos', 0)
        self.assertEqual(suma_dist, data.get('total_asistencia'))

        # Verificación de ranking restringido a 3
        ranking = data.get('ranking_redes', [])
        self.assertLessEqual(len(ranking), 3)

    @patch('services.dashboard_service.get_db_connection')
    @patch('services.dashboard_service.get_metricas_red')
    def test_api_dashboard_datos_db_connected_red(self, mock_get_red, mock_db):
        """Con BD conectada, nivel red debe solicitar la red especificada y retornar sus métricas."""
        mock_conn = MagicMock()
        mock_db.return_value = mock_conn

        mock_get_red.return_value = {
            'nombre_red': 'Red Hebrón',
            'supervisor': 'Pedro González',
            'casas_activas': 5,
            'asistencia_total': 50,
            'promedio_casa': 10,
            'conversiones': 6,
            'ofrendas_usd': 150.0,
            'ofrendas_bs': 5000.0,
            'distribucion': {'regulares': 25, 'ninos': 10, 'visitas': 10, 'comprometidos': 5},
            'casas': [{'id': 1, 'codigo': 'HEB-001', 'asistencia': 18}],
            'actividad_reciente': [{'lider': 'Juan Pérez', 'cdp_codigo': 'HEB-001', 'asistencia': 18}],
            'lideres_red': [{'nombre': 'Juan Pérez', 'rol': 'Líder', 'cdp_codigo': 'HEB-001'}]
        }

        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'admin-uuid-1'
            sess['usuario'] = 'admin'
            sess['rol'] = 'admin'

        res = self.client.get('/api/dashboard/datos?nivel=red&red_id=1&periodo=semana')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get('nombre_red'), 'Red Hebrón')
        self.assertEqual(data.get('asistencia_total'), 50)
        self.assertFalse(data.get('mock_used'))

    # -------------------------------------------------------------------------
    # 2. Sin conexión a BD: Modo Mock (MOCK_MODE=True) vs Neutro (MOCK_MODE=False)
    # -------------------------------------------------------------------------
    @patch('services.dashboard_service.get_db_connection', return_value=None)
    @patch('services.dashboard_service.mock_mode_enabled', return_value=True)
    def test_api_dashboard_datos_mock_mode_enabled(self, mock_enabled, mock_db):
        """Con MOCK_MODE=True y sin BD, /api/dashboard/datos debe retornar datos demo con mock_used=True."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'admin-uuid-1'
            sess['usuario'] = 'admin'
            sess['rol'] = 'admin'

        res = self.client.get('/api/dashboard/datos?nivel=general&periodo=semana')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('mock_used'))
        self.assertGreater(data.get('total_asistencia', 0), 0)
        self.assertIn('distribucion', data)
        self.assertIn('ranking_redes', data)

        # Nivel red en mock
        res_red = self.client.get('/api/dashboard/datos?nivel=red&red_id=1')
        self.assertEqual(res_red.status_code, 200)
        data_red = res_red.get_json()
        self.assertTrue(data_red.get('mock_used'))
        self.assertEqual(data_red.get('nombre_red'), 'Red Hebrón')

        # Nivel cdp en mock
        res_cdp = self.client.get('/api/dashboard/datos?nivel=cdp&cdp_id=1')
        self.assertEqual(res_cdp.status_code, 200)
        data_cdp = res_cdp.get_json()
        self.assertTrue(data_cdp.get('mock_used'))
        self.assertIn('historial', data_cdp)

    @patch('services.dashboard_service.get_db_connection', return_value=None)
    @patch('services.dashboard_service.mock_mode_enabled', return_value=False)
    def test_api_dashboard_datos_mock_mode_disabled_empty_structure(self, mock_enabled, mock_db):
        """Con MOCK_MODE=False y sin BD, debe responder estructura sanitizada neutra con mock_used=False."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'admin-uuid-1'
            sess['usuario'] = 'admin'
            sess['rol'] = 'admin'

        res = self.client.get('/api/dashboard/datos?nivel=general&periodo=semana')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertFalse(data.get('mock_used'))
        self.assertEqual(data.get('total_asistencia'), 0)
        self.assertEqual(data.get('total_casas', 0), 0)
        self.assertEqual(data.get('ranking_redes'), [])
        self.assertEqual(data.get('tendencia_semanas'), [])
        self.assertIn('distribucion', data)

    # -------------------------------------------------------------------------
    # 3. Control de acceso y aislamiento territorial de Supervisor
    # -------------------------------------------------------------------------
    @patch('routes.api.dashboard_api.get_supervisor_red_id', return_value=2)
    @patch('services.dashboard_service.get_db_connection', return_value=None)
    @patch('services.dashboard_service.mock_mode_enabled', return_value=True)
    def test_supervisor_coercion_to_assigned_red(self, mock_enabled, mock_db, mock_sup_red):
        """Supervisor intentando consultar nivel 'general' o red ajena debe ser confinado a su red."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'sup-uuid-2'
            sess['usuario'] = 'supervisor2'
            sess['rol'] = 'supervisor'

        # Intento de consultar nivel general -> se confina a nivel red con red_id=2
        res = self.client.get('/api/dashboard/datos?nivel=general&red_id=1')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get('nombre_red'), 'Red Sur')

    @patch('routes.api.dashboard_api.get_supervisor_red_id', return_value=1)
    @patch('services.dashboard_service.get_selectores', return_value=([], [{'id': 1, 'red_id': 1}, {'id': 2, 'red_id': 2}]))
    def test_supervisor_anti_idor_cdp(self, mock_selectores, mock_sup_red):
        """Supervisor intentando consultar una Casa de Paz de otra red recibe 403 Forbidden."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'sup-uuid-1'
            sess['usuario'] = 'supervisor1'
            sess['rol'] = 'supervisor'

        res = self.client.get('/api/dashboard/datos?nivel=cdp&cdp_id=2')
        self.assertEqual(res.status_code, 403)

    # -------------------------------------------------------------------------
    # 4. Coerción de parámetros malformados
    # -------------------------------------------------------------------------
    @patch('services.dashboard_service.get_db_connection', return_value=None)
    @patch('services.dashboard_service.mock_mode_enabled', return_value=True)
    def test_api_dashboard_datos_malformed_params_graceful(self, mock_enabled, mock_db):
        """Parámetros no numéricos o desconocidos deben ser manejados sin excepción 500."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'admin-uuid-1'
            sess['usuario'] = 'admin'
            sess['rol'] = 'admin'

        res = self.client.get('/api/dashboard/datos?nivel=red&red_id=invalido&periodo=inexistente&mes=99')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get('periodo'), 'semana')


if __name__ == '__main__':
    unittest.main()
