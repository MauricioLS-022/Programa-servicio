"""
tests/test_api_dashboard_lider.py - Pruebas para el endpoint REST GET /api/lider/dashboard.
Valida autenticación (401), control de roles (403), serialización homogénea (200) y paginación.
"""
import unittest
from unittest.mock import patch
from app import app


class TestApiDashboardLider(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-dashboard-lider'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_dashboard_lider_unauthenticated(self):
        """Petición sin sesión debe retornar 401 Unauthorized."""
        response = self.client.get('/api/lider/dashboard')
        self.assertEqual(response.status_code, 401)

    def test_dashboard_lider_forbidden_role(self):
        """Usuarios con rol supervisor no deben acceder a /api/lider/dashboard (403)."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'sup-123'
            sess['usuario'] = 'supervisor_test'
            sess['rol'] = 'supervisor'

        response = self.client.get('/api/lider/dashboard')
        self.assertEqual(response.status_code, 403)

    def test_dashboard_lider_success(self):
        """Líder de CDP autenticado debe recibir 200 con estructura de datos del dashboard."""
        mock_data = {
            'cdp': {'id': 10, 'codigo': 'CDP-10', 'anfitrion': 'Familia Rodríguez'},
            'lideres': [
                {'id': 1, 'nombre': 'Juan', 'apellido': 'Pérez', 'rol': 'Lider', 'telefono': '04141234567'}
            ],
            'metricas': {
                'total_reportes': 12,
                'asistencia_promedio': 18.5,
                'ofrendas_usd_totales': 150.0,
                'ofrendas_bs_totales': 6200.5,
                'visitas_totales': 8,
                'conversiones_totales': 3,
                'reconciliaciones_totales': 1,
                'reporte_esta_semana': True,
                'dias_cierre_texto': 'Próximo cierre: Domingo 6:00 PM',
            },
            'reportes': [
                {
                    'id': 'rep-1',
                    'fecha': '2026-11-01',
                    'fecha_formateada': '01 Nov 2026',
                    'hr_inicio': '18:00',
                    'hr_fin': '19:30',
                    'lider_nombre': 'Juan Pérez',
                    'iniciales': 'JP',
                    'tema': 'El Poder de la Fe',
                    'asistencia': 20,
                    'ofrendas_usd': 25.0,
                    'ofrendas_bs': 1000.0,
                }
            ],
            'total_reportes': 12,
            'page': 1,
            'pages': 3,
            'tiene_cdp': True
        }

        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'lider-uuid-1'
            sess['usuario'] = 'lider1'
            sess['rol'] = 'lider_cdp'

        with patch('routes.api.dashboard_api.get_lider_dashboard_data', return_value=mock_data) as mock_service:
            response = self.client.get('/api/lider/dashboard?page=2&per_page=5')
            self.assertEqual(response.status_code, 200)
            mock_service.assert_called_once_with('lider-uuid-1', page=2, per_page=5)

            data = response.get_json()
            self.assertIn('cdp', data)
            self.assertEqual(data['cdp']['codigo'], 'CDP-10')
            self.assertIn('metricas', data)
            self.assertEqual(data['metricas']['total_reportes'], 12)
            self.assertEqual(data['total_reportes'], 12)
            self.assertEqual(data['page'], 1)
            self.assertEqual(data['pages'], 3)
            self.assertTrue(data['tiene_cdp'])
            self.assertEqual(len(data['reportes']), 1)
            self.assertEqual(data['reportes'][0]['tema'], 'El Poder de la Fe')

    def test_dashboard_lider_admin_access(self):
        """Admin puede consultar dashboard de un líder específico o propio."""
        mock_data = {
            'cdp': {'id': 5, 'codigo': 'CDP-05', 'anfitrion': 'Casa Test'},
            'lideres': [],
            'metricas': {'total_reportes': 0},
            'reportes': [],
            'total_reportes': 0,
            'page': 1,
            'pages': 1,
            'tiene_cdp': True
        }

        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'admin-uuid-1'
            sess['usuario'] = 'admin'
            sess['rol'] = 'admin'

        with patch('routes.api.dashboard_api.get_lider_dashboard_data', return_value=mock_data) as mock_service:
            response = self.client.get('/api/lider/dashboard?usuario_id=target-lider-uuid')
            self.assertEqual(response.status_code, 200)
            mock_service.assert_called_once_with('target-lider-uuid', page=1, per_page=5)
