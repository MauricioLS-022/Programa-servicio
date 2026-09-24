"""
Pruebas de verificación para las remediaciones de seguridad:
1. Prevención de Open Redirect con is_safe_url y safe_redirect.
2. Aislamiento territorial estricto en /supervisor/casa_de_paz/<id>:
   - Bloqueo (403) a supervisores sin red asignada.
   - Bloqueo (403) a supervisores intentando acceder a CDPs de otras redes (IDOR).
   - Acceso permitido (200) a supervisores en CDPs de su propia red.
3. Optimización en memoria de _ensure_currency_columns en db_queries.
"""
import unittest
from unittest.mock import patch, MagicMock
from app import app
from utils.auth import is_safe_url, safe_redirect
import db_queries


class TestSecurityRemediations(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.client = app.test_client()
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test-secret-key-123'

    # ------------------------------------------------------------------
    # 1. Pruebas de Open Redirect Prevention
    # ------------------------------------------------------------------
    def test_is_safe_url_internal_vs_external(self):
        """is_safe_url debe permitir URLs locales y rechazar URLs externas o maliciosas."""
        with self.app.test_request_context('http://localhost:5000/admin/usuario'):
            # Rutas relativas seguras
            self.assertTrue(is_safe_url('/admin/usuario'))
            self.assertTrue(is_safe_url('/admin/reportes?q=test'))
            self.assertTrue(is_safe_url('http://localhost:5000/admin/estructura'))

            # URLs externas maliciosas (Open Redirect)
            self.assertFalse(is_safe_url('https://evil.com/phishing'))
            self.assertFalse(is_safe_url('http://attacker.org'))
            self.assertFalse(is_safe_url('//evil.com'))
            self.assertFalse(is_safe_url('javascript:alert(1)'))
            self.assertFalse(is_safe_url(None))
            self.assertFalse(is_safe_url(''))

    def test_safe_redirect_behavior(self):
        """safe_redirect debe volver al referrer local seguro o al fallback institucional si es externo."""
        with self.app.test_request_context(
            '/admin/usuario/1/toggle_estado',
            base_url='http://localhost:5000',
            headers={'Referer': 'http://localhost:5000/admin/usuario?page=2'}
        ):
            resp = safe_redirect('admin.usuario')
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.headers['Location'], 'http://localhost:5000/admin/usuario?page=2')

        with self.app.test_request_context(
            '/admin/usuario/1/toggle_estado',
            base_url='http://localhost:5000',
            headers={'Referer': 'https://attacker.com/malicious'}
        ):
            resp = safe_redirect('admin.usuario')
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.headers['Location'], '/admin/usuario')

    # ------------------------------------------------------------------
    # 2. Pruebas de Aislamiento Territorial para Supervisor
    # ------------------------------------------------------------------
    @patch('routes.supervisor_routes.get_supervisor_red_id', return_value=None)
    def test_supervisor_unassigned_denied_casa_de_paz(self, mock_sup_red):
        """Un supervisor sin red asignada debe recibir 403 Forbidden al intentar ver cualquier CDP."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'sup-unassigned-uuid'
            sess['usuario'] = 'supervisor_sin_red'
            sess['rol'] = 'supervisor'

        resp = self.client.get('/supervisor/casa_de_paz/1')
        self.assertEqual(resp.status_code, 403)

    @patch('routes.supervisor_routes.get_supervisor_red_id', return_value=1)
    @patch('services.cdp_service.get_cdp_detalle')
    def test_supervisor_cross_network_denied_casa_de_paz(self, mock_cdp_det, mock_sup_red):
        """Un supervisor con red 1 debe recibir 403 Forbidden al intentar ver una CDP de red 2."""
        mock_cdp_det.return_value = {
            'id': 99,
            'codigo': 'CDP-99',
            'red_id': 2,
            'red_nombre': 'Red Diferente',
        }

        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'sup-red1-uuid'
            sess['usuario'] = 'supervisor_red1'
            sess['rol'] = 'supervisor'

        resp = self.client.get('/supervisor/casa_de_paz/99')
        self.assertEqual(resp.status_code, 403)

    @patch('routes.supervisor_routes.get_supervisor_red_id', return_value=1)
    @patch('services.cdp_service.get_cdp_detalle')
    def test_supervisor_own_network_allowed_casa_de_paz(self, mock_cdp_det, mock_sup_red):
        """Un supervisor con red 1 debe acceder exitosamente (200) a una CDP de red 1."""
        from mock_data import get_mock_cdp_detalle
        mock_cdp_det.return_value = get_mock_cdp_detalle(1)

        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'sup-red1-uuid'
            sess['usuario'] = 'supervisor_red1'
            sess['rol'] = 'supervisor'

        resp = self.client.get('/supervisor/casa_de_paz/1')
        self.assertEqual(resp.status_code, 200)

    # ------------------------------------------------------------------
    # 3. Optimización de Memoria en db_queries
    # ------------------------------------------------------------------
    def test_ensure_currency_columns_cached(self):
        """_ensure_currency_columns solo debe ejecutar queries a MySQL la primera vez."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {'Field': 'ofrendas_bs'}

        db_queries._currency_columns_checked = False
        db_queries._ensure_currency_columns(mock_cursor)

        # La primera vez corre SHOW COLUMNS
        self.assertTrue(mock_cursor.execute.called)
        self.assertTrue(db_queries._currency_columns_checked)

        mock_cursor.reset_mock()
        # La segunda llamada debe omitirse de inmediato
        db_queries._ensure_currency_columns(mock_cursor)
        mock_cursor.execute.assert_not_called()


if __name__ == '__main__':
    unittest.main()
