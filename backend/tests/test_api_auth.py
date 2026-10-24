"""
tests/test_api_auth.py - Pruebas para API REST Foundation y Autenticación.
Valida /api/health, /api/auth/login, /api/auth/me, /api/auth/logout y soporte CORS.
"""
import unittest
from unittest.mock import patch
from app import app


class TestApiAuthEndpoints(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-api-secret-key-123456'
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['CORS_ORIGINS'] = ['http://localhost:5173', 'http://127.0.0.1:5173']
        self.client = app.test_client()

    def test_health_check_get_and_head(self):
        """Verifica que /api/health responda con status 200 y JSON correspondiente."""
        res_get = self.client.get('/api/health')
        self.assertEqual(res_get.status_code, 200)
        data = res_get.get_json()
        self.assertEqual(data.get('status'), 'ok')
        self.assertEqual(data.get('app'), 'vino-nuevo')

        res_head = self.client.head('/api/health')
        self.assertEqual(res_head.status_code, 200)

    def test_cors_headers_in_api(self):
        """Verifica que las peticiones a la API desde orígenes autorizados incluyan cabeceras CORS."""
        response = self.client.get('/api/health', headers={'Origin': 'http://localhost:5173'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('Access-Control-Allow-Origin'), 'http://localhost:5173')
        self.assertEqual(response.headers.get('Access-Control-Allow-Credentials'), 'true')

    def test_api_auth_me_unauthenticated(self):
        """Petición a /api/auth/me sin sesión debe retornar 401 y authenticated: False."""
        response = self.client.get('/api/auth/me')
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertFalse(data.get('authenticated'))

    def test_api_auth_login_missing_fields(self):
        """Login con campos vacíos debe retornar código 400."""
        response = self.client.post('/api/auth/login', json={})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data.get('success'))

    def test_api_auth_login_invalid_credentials(self):
        """Login con credenciales incorrectas debe retornar 401."""
        response = self.client.post('/api/auth/login', json={
            'username': 'usuario_inexistente_xyz',
            'password': 'clave_incorrecta_123'
        })
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertFalse(data.get('success'))

    def test_api_auth_login_and_me_flow(self):
        """Flujo completo: login exitoso, verificación de /me y cierre de sesión con /logout."""
        # 1. Login exitoso (modo dev/testing con credenciales demo o BD mock)
        login_res = self.client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'admin'
        })
        self.assertEqual(login_res.status_code, 200)
        login_data = login_res.get_json()
        self.assertTrue(login_data.get('success'))
        self.assertEqual(login_data['user']['username'], 'admin')
        self.assertEqual(login_data['user']['rol'], 'admin')

        # 2. Comprobación de identidad en /me con la cookie de sesión activa
        me_res = self.client.get('/api/auth/me')
        self.assertEqual(me_res.status_code, 200)
        me_data = me_res.get_json()
        self.assertTrue(me_data.get('authenticated'))
        self.assertEqual(me_data['user']['username'], 'admin')
        self.assertEqual(me_data['user']['rol'], 'admin')

        # 3. Logout
        logout_res = self.client.post('/api/auth/logout')
        self.assertEqual(logout_res.status_code, 200)
        logout_data = logout_res.get_json()
        self.assertTrue(logout_data.get('success'))

        # 4. /me debe responder 401 tras invalidar la sesión
        me_after_logout = self.client.get('/api/auth/me')
        self.assertEqual(me_after_logout.status_code, 401)
        self.assertFalse(me_after_logout.get_json().get('authenticated'))

    def test_api_auth_login_with_db_user(self):
        """Valida que la autenticación con BD active sesión correctamente con roles asignados."""
        fake_user = {
            'id': 'd290f1ee-6c54-4b01-90e6-d701748f0851',
            'username': 'supervisor_test',
            'password': 'pbkdf2:sha256:260000$dummy$hash',
            'tipo_usuario': 'supervisor',
            'is_active': 1,
            'nombre': 'Carlos',
            'apellido': 'Pérez'
        }

        mock_cur = unittest.mock.MagicMock()
        mock_cur.fetchone.return_value = fake_user
        mock_conn = unittest.mock.MagicMock()
        mock_conn.cursor.return_value = mock_cur

        with patch('routes.api.auth_api.get_db_connection', return_value=mock_conn), \
             patch('routes.api.auth_api._check_password', return_value=True):
            response = self.client.post('/api/auth/login', json={
                'username': 'supervisor_test',
                'password': 'PasswordValido123!'
            })
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data.get('success'))
            self.assertEqual(data['user']['username'], 'supervisor_test')
            self.assertEqual(data['user']['rol'], 'supervisor')
            self.assertEqual(data['user']['nombre'], 'Carlos')

    def test_api_auth_config(self):
        """Verifica que /api/auth/config retorne 200 con siteKey e isDev."""
        response = self.client.get('/api/auth/config')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('siteKey', data)
        self.assertIn('isDev', data)

    def test_api_auth_login_recaptcha_failure(self):
        """Verifica que un token de reCAPTCHA inválido o con bajo puntaje sea rechazado."""
        app.config['FLASK_ENV'] = 'production'
        app.config['DEBUG'] = False
        app.config['TESTING'] = False

        recaptcha_mock = unittest.mock.MagicMock()
        recaptcha_mock.json.return_value = {"success": False, "score": 0.3, "action": "login"}

        with patch('requests.post', return_value=recaptcha_mock):
            response = self.client.post('/api/auth/login', json={
                'username': 'admin',
                'password': 'Password123!',
                'recaptcha_token': 'fake-invalid-token'
            })
            self.assertEqual(response.status_code, 400)
            data = response.get_json()
            self.assertFalse(data.get('success'))
            self.assertIn("verificación de seguridad fallida", data.get('error', ''))

        app.config['TESTING'] = True
        app.config['FLASK_ENV'] = 'development'

    def test_api_auth_login_recaptcha_success_production(self):
        """Verifica que reCAPTCHA válido en producción permita autenticar."""
        app.config['FLASK_ENV'] = 'production'
        app.config['DEBUG'] = False
        app.config['TESTING'] = False

        fake_user = {
            'id': 'd290f1ee-6c54-4b01-90e6-d701748f0851',
            'username': 'prod_admin',
            'password': 'pbkdf2:sha256:260000$dummy$hash',
            'tipo_usuario': 'admin',
            'is_active': 1,
            'nombre': 'Admin',
            'apellido': 'Prod'
        }

        mock_cur = unittest.mock.MagicMock()
        mock_cur.fetchone.return_value = fake_user
        mock_conn = unittest.mock.MagicMock()
        mock_conn.cursor.return_value = mock_cur

        recaptcha_mock = unittest.mock.MagicMock()
        recaptcha_mock.json.return_value = {"success": True, "score": 0.9, "action": "login"}

        with patch('requests.post', return_value=recaptcha_mock), \
             patch('routes.api.auth_api.get_db_connection', return_value=mock_conn), \
             patch('routes.api.auth_api._check_password', return_value=True):
            response = self.client.post('/api/auth/login', json={
                'username': 'prod_admin',
                'password': 'PasswordValido123!',
                'g-recaptcha-response': 'fake-valid-token'
            })
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data.get('success'))
            self.assertEqual(data['user']['username'], 'prod_admin')

        app.config['TESTING'] = True
        app.config['FLASK_ENV'] = 'development'

    def test_api_auth_login_rate_limiting(self):
        """Verifica que el decorador limiter responda con 429 al exceder 5 intentos por minuto."""
        from extensions import limiter
        limiter.enabled = True
        try:
            for _ in range(5):
                self.client.post('/api/auth/login', json={'username': 'test_rate', 'password': 'wrong'})
            
            response = self.client.post('/api/auth/login', json={'username': 'test_rate', 'password': 'wrong'})
            self.assertEqual(response.status_code, 429)
        finally:
            limiter.enabled = False
            limiter.reset()


if __name__ == '__main__':
    unittest.main()

