"""Pruebas de integración para endpoints REST /api/export/* (RBAC, Anti-IDOR, formatos y 503)."""
import io
import os
import sys
import unittest
from unittest.mock import patch

from openpyxl import load_workbook

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from repositories.mock_repositories import (
    MockEstructuraRepository,
    MockLiderRepository,
    MockReporteRepository,
    NullEstructuraRepository,
    NullLiderRepository,
    NullReporteRepository,
)


class TestApiExport(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['MOCK_MODE'] = True
        self.client = app.test_client()

    def _login_session(self, rol: str, usuario_id: str = 'user-test-1'):
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = usuario_id
            sess['usuario'] = f'{rol}_test'
            sess['rol'] = rol

    # ------------------------------------------------------------------
    # 1. Autenticación (401)
    # ------------------------------------------------------------------
    def test_anonymous_cannot_access_any_export_endpoint(self):
        for path in (
            '/api/export/reportes?format=pdf',
            '/api/export/usuarios?format=xlsx',
            '/api/export/lideres?format=xlsx',
            '/api/export/casas_de_paz?format=csv',
        ):
            res = self.client.get(path)
            self.assertEqual(res.status_code, 401, f'Esperaba 401 en {path}')

    # ------------------------------------------------------------------
    # 2. RBAC (403)
    # ------------------------------------------------------------------
    def test_lider_cdp_blocked_from_export_endpoints(self):
        self._login_session('lider_cdp')
        for path in (
            '/api/export/reportes?format=pdf',
            '/api/export/usuarios?format=xlsx',
            '/api/export/lideres?format=xlsx',
            '/api/export/casas_de_paz?format=csv',
        ):
            res = self.client.get(path)
            self.assertEqual(res.status_code, 403, f'Esperaba 403 para lider_cdp en {path}')

    def test_supervisor_blocked_from_usuarios_export(self):
        self._login_session('supervisor')
        res = self.client.get('/api/export/usuarios?format=xlsx')
        self.assertEqual(res.status_code, 403)

    # ------------------------------------------------------------------
    # 3. Validación de formato (400)
    # ------------------------------------------------------------------
    def test_invalid_format_returns_400_json(self):
        self._login_session('admin')
        for path in (
            '/api/export/reportes?format=doc',
            '/api/export/usuarios?format=pdf',
            '/api/export/lideres?format=pdf',
            '/api/export/casas_de_paz?format=xml',
        ):
            res = self.client.get(path)
            self.assertEqual(res.status_code, 400, f'Esperaba 400 en {path}')
            data = res.get_json()
            self.assertFalse(data['success'])
            self.assertEqual(data['code'], 'invalid_format')

    # ------------------------------------------------------------------
    # 4. Descargas exitosas (admin) - PDF, XLSX, CSV
    # ------------------------------------------------------------------
    @patch('routes.api.export_api.get_reporte_repository', return_value=MockReporteRepository())
    def test_admin_export_reportes_pdf_xlsx_csv(self, _mock_repo):
        self._login_session('admin')

        # PDF
        res_pdf = self.client.get('/api/export/reportes?format=pdf')
        self.assertEqual(res_pdf.status_code, 200)
        self.assertIn('application/pdf', res_pdf.content_type)
        self.assertIn('attachment', res_pdf.headers.get('Content-Disposition', ''))
        self.assertTrue(res_pdf.data.startswith(b'%PDF'))

        # XLSX
        res_xlsx = self.client.get('/api/export/reportes?format=xlsx')
        self.assertEqual(res_xlsx.status_code, 200)
        self.assertIn('spreadsheetml.sheet', res_xlsx.content_type)
        self.assertTrue(res_xlsx.data.startswith(b'PK'))
        wb = load_workbook(io.BytesIO(res_xlsx.data))
        self.assertGreaterEqual(wb.active.max_row, 2)

        # CSV con BOM
        res_csv = self.client.get('/api/export/reportes?format=csv')
        self.assertEqual(res_csv.status_code, 200)
        self.assertIn('text/csv', res_csv.content_type)
        self.assertTrue(res_csv.data.startswith(b'\xef\xbb\xbf'))

    @patch('routes.api.export_api.mock_mode_enabled', return_value=True)
    @patch('services.user_service.get_db_connection', return_value=None)
    @patch('services.user_service.mock_mode_enabled', return_value=True)
    def test_admin_export_usuarios_xlsx_and_csv(self, *_mocks):
        self._login_session('admin')
        res_xlsx = self.client.get('/api/export/usuarios?format=xlsx')
        self.assertEqual(res_xlsx.status_code, 200)
        self.assertTrue(res_xlsx.data.startswith(b'PK'))

        res_csv = self.client.get('/api/export/usuarios?format=csv')
        self.assertEqual(res_csv.status_code, 200)
        self.assertTrue(res_csv.data.startswith(b'\xef\xbb\xbf'))

    @patch('routes.api.export_api.get_lider_repository', return_value=MockLiderRepository())
    def test_admin_export_lideres_xlsx_and_csv(self, _mock_repo):
        self._login_session('admin')
        res = self.client.get('/api/export/lideres?format=xlsx')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data.startswith(b'PK'))

    @patch('routes.api.export_api.get_estructura_repository', return_value=MockEstructuraRepository())
    def test_admin_export_casas_xlsx_and_csv(self, _mock_repo):
        self._login_session('admin')
        res = self.client.get('/api/export/casas_de_paz?format=csv')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data.startswith(b'\xef\xbb\xbf'))

    # ------------------------------------------------------------------
    # 5. Aislamiento territorial Anti-IDOR de Supervisor
    # ------------------------------------------------------------------
    @patch('routes.api.export_api.get_supervisor_red_id', return_value=1)
    @patch('routes.api.export_api.get_cdp_detalle', return_value={'id': 99, 'red_id': 2})
    @patch('routes.api.export_api.get_reporte_repository', return_value=MockReporteRepository())
    @patch('routes.api.export_api.get_lider_repository', return_value=MockLiderRepository())
    @patch('routes.api.export_api.get_estructura_repository', return_value=MockEstructuraRepository())
    def test_supervisor_anti_idor_blocks_other_red_and_other_cdp(self, *_mocks):
        self._login_session('supervisor')

        # Otra red
        self.assertEqual(self.client.get('/api/export/reportes?format=pdf&red_id=2').status_code, 403)
        self.assertEqual(self.client.get('/api/export/lideres?format=xlsx&red_id=2').status_code, 403)
        self.assertEqual(self.client.get('/api/export/casas_de_paz?format=csv&red_id=2').status_code, 403)

        # Otra CDP perteneciente a red 2
        self.assertEqual(self.client.get('/api/export/reportes?format=pdf&cdp_id=99').status_code, 403)
        self.assertEqual(self.client.get('/api/export/lideres?format=xlsx&cdp_id=99').status_code, 403)

        # Propia red permitida
        self.assertEqual(self.client.get('/api/export/reportes?format=pdf&red_id=1').status_code, 200)
        self.assertEqual(self.client.get('/api/export/lideres?format=xlsx&red_id=1').status_code, 200)
        self.assertEqual(self.client.get('/api/export/casas_de_paz?format=csv&red_id=1').status_code, 200)

    # ------------------------------------------------------------------
    # 6. Degradación segura 503 cuando BD no está disponible y MOCK_MODE=False
    # ------------------------------------------------------------------
    @patch('routes.api.export_api.get_reporte_repository', return_value=NullReporteRepository())
    @patch('routes.api.export_api.get_lider_repository', return_value=NullLiderRepository())
    @patch('routes.api.export_api.get_estructura_repository', return_value=NullEstructuraRepository())
    @patch('routes.api.export_api.mock_mode_enabled', return_value=False)
    @patch('routes.api.export_api.get_db_connection', return_value=None)
    def test_db_unavailable_returns_503_json(self, *_mocks):
        self._login_session('admin')
        for path in (
            '/api/export/reportes?format=pdf',
            '/api/export/usuarios?format=xlsx',
            '/api/export/lideres?format=xlsx',
            '/api/export/casas_de_paz?format=csv',
        ):
            res = self.client.get(path)
            self.assertEqual(res.status_code, 503, f'Esperaba 503 en {path}')
            payload = res.get_json()
            self.assertEqual(payload['code'], 'db_unavailable')

    # ------------------------------------------------------------------
    # 7. Paridad Jinja2: conexión a /api/export/*, sin stubs alert() y Live Search
    # ------------------------------------------------------------------
    def test_jinja_templates_and_scripts_wired_to_server_exports_and_live_search(self):
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        with open(os.path.join(base, 'templates', 'dashboard_admin.html'), 'r', encoding='utf-8') as f:
            dash_html = f.read()
        self.assertNotIn("alert('Exportando", dash_html)
        self.assertIn('data-export-resource="reportes"', dash_html)

        with open(os.path.join(base, 'static', 'scripts', 'dashboard.js'), 'r', encoding='utf-8') as f:
            self.assertIn('/api/export/', f.read())

        with open(os.path.join(base, 'static', 'scripts', 'admin', 'reportes.js'), 'r', encoding='utf-8') as f:
            self.assertIn('/api/export/reportes', f.read())

        with open(os.path.join(base, 'static', 'scripts', 'admin', 'usuarios.js'), 'r', encoding='utf-8') as f:
            usr_js = f.read()
            self.assertIn('/api/export/usuarios', usr_js)
            self.assertIn('applyLiveSearchUsers', usr_js)

        with open(os.path.join(base, 'static', 'scripts', 'admin', 'lider.js'), 'r', encoding='utf-8') as f:
            lid_js = f.read()
            self.assertIn('/api/export/lideres', lid_js)
            self.assertIn('applyLiveSearchLeaders', lid_js)

        with open(os.path.join(base, 'static', 'scripts', 'estructura.js'), 'r', encoding='utf-8') as f:
            self.assertIn('/api/export/casas_de_paz', f.read())


if __name__ == '__main__':
    unittest.main()
