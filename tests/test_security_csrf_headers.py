"""
tests/test_security_csrf_headers.py - Pruebas para cabeceras HTTP, CSRF, API RBAC e IDOR.
"""

import unittest
from unittest.mock import patch
from app import app


class TestSecurityHeadersAndCookies(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-security-secret-123'
        self.client = app.test_client()

    def test_security_headers_present(self):
        """Verifica que las cabeceras defensivas HTTP (OWASP) se inyecten en las respuestas."""
        response = self.client.get('/iniciar_sesion')
        self.assertEqual(response.status_code, 200)

        # X-Frame-Options
        self.assertEqual(response.headers.get('X-Frame-Options'), 'SAMEORIGIN')

        # X-Content-Type-Options
        self.assertEqual(response.headers.get('X-Content-Type-Options'), 'nosniff')

        # Referrer-Policy
        self.assertEqual(response.headers.get('Referrer-Policy'), 'strict-origin-when-cross-origin')

        # Permissions-Policy
        self.assertIn('geolocation=()', response.headers.get('Permissions-Policy', ''))

        # Content-Security-Policy
        csp = response.headers.get('Content-Security-Policy', '')
        self.assertIn("default-src 'self'", csp)
        self.assertIn("frame-ancestors 'self'", csp)

    def test_session_cookie_security_config(self):
        """Verifica la configuración de endurecimiento de cookies de sesión."""
        self.assertTrue(app.config.get('SESSION_COOKIE_HTTPONLY'))
        self.assertEqual(app.config.get('SESSION_COOKIE_SAMESITE'), 'Lax')


class TestCSRFProtection(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-security-secret-123'
        app.config['FORCE_CSRF_IN_TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = True
        self.client = app.test_client()

    def tearDown(self):
        app.config['FORCE_CSRF_IN_TESTING'] = False
        app.config['WTF_CSRF_ENABLED'] = False

    def test_post_without_csrf_is_rejected(self):
        """Un POST sin token CSRF debe ser bloqueado con código 400."""
        response = self.client.post('/iniciar_sesion', data={
            'usuario': 'admin',
            'contrasena': 'admin'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'400', response.data)


class TestApiAccessAndIDOR(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-security-secret-123'
        self.client = app.test_client()

    def test_api_dashboard_unauthenticated(self):
        """Peticiones anónimas a /api/dashboard/datos deben ser redirigidas al login."""
        response = self.client.get('/api/dashboard/datos')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/iniciar_sesion', response.headers.get('Location', ''))

    def test_api_dashboard_supervisor_scoping(self):
        """Un supervisor sólo puede consultar métricas de su propia red (prevención IDOR)."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'sup-user-id'
            sess['usuario'] = 'supervisor1'
            sess['rol'] = 'supervisor'

        with patch('routes.api_routes.get_supervisor_red_id', return_value=2), \
             patch('routes.api_routes.get_metricas', return_value={'asistencia': 100}) as mock_metricas:
            # Intento de consultar red_id=1 siendo supervisor de la red 2
            response = self.client.get('/api/dashboard/datos?nivel=general&red_id=1')
            self.assertEqual(response.status_code, 200)
            # Debe forzar nivel='red' y red_id=2
            mock_metricas.assert_called_once_with('red', 2, None)

    def test_supervisor_cdp_idor_prevention(self):
        """Un supervisor no puede ver detalles de una CDP que pertenece a otra red (403 Forbidden)."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'sup-user-id'
            sess['usuario'] = 'supervisor1'
            sess['rol'] = 'supervisor'

        with patch('routes.supervisor_routes.get_supervisor_red_id', return_value=1), \
             patch('services.cdp_service.get_cdp_detalle', return_value={'id': 99, 'codigo': 'SUR-001', 'red_id': 2}):
            # Supervisor de Red 1 intenta ver Casa de Paz perteneciente a Red 2
            response = self.client.get('/supervisor/casa_de_paz/99')
            self.assertEqual(response.status_code, 403)


if __name__ == '__main__':
    unittest.main()
