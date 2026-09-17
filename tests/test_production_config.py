"""
Tests unitarios y de integración para la Configuración Segura de Producción:
- Verificación estricta de DEBUG=False y flags seguras en ProductionConfig.
- Validación Fail-Fast de credenciales y variables de entorno obligatorias.
- Neutralización absoluta de MOCK_MODE y fallbacks demo en entornos productivos.
- Bloqueo de inicios de sesión demo (admin/admin, supervisor/supervisor, lider/lider) en producción.
- Protección de endpoints de detalle contra fugas de mock data sin base de datos.
"""
import unittest
from unittest.mock import patch, MagicMock
from flask import Flask

import config
from config import ProductionConfig, validate_production_config
import database
from services import dashboard_service, cdp_service
from app import app


class TestProductionConfigAttributes(unittest.TestCase):
    """Verifica que las directivas de seguridad en ProductionConfig sean estrictas."""

    def test_production_config_flags(self):
        """ProductionConfig debe tener DEBUG=False, MOCK_MODE=False y cookies seguras."""
        self.assertFalse(ProductionConfig.DEBUG, "DEBUG debe ser estrictamente False en ProductionConfig")
        self.assertFalse(getattr(ProductionConfig, 'TESTING', False), "TESTING debe ser False en ProductionConfig")
        self.assertFalse(ProductionConfig.MOCK_MODE, "MOCK_MODE debe ser estrictamente False en ProductionConfig")
        self.assertTrue(ProductionConfig.SESSION_COOKIE_SECURE, "SESSION_COOKIE_SECURE debe ser True en producción")
        self.assertTrue(ProductionConfig.SESSION_COOKIE_HTTPONLY, "SESSION_COOKIE_HTTPONLY debe ser True en producción")
        self.assertEqual(ProductionConfig.SESSION_COOKIE_SAMESITE, 'Lax')
        self.assertEqual(ProductionConfig.FLASK_ENV, 'production')


class TestValidateProductionConfig(unittest.TestCase):
    """Verifica la validación Fail-Fast de variables obligatorias en producción."""

    def _get_valid_prod_config(self):
        return {
            'DEBUG': False,
            'TESTING': False,
            'MOCK_MODE': False,
            'SECRET_KEY': 'a-very-long-and-secure-cryptographic-key-1234567890',
            'DB_HOST': 'db.vinonuevo.cloud',
            'DB_USER': 'vinonuevo_prod_user',
            'DB_PASSWORD': 'SuperSecurePassword987!',
            'DB_NAME': 'serv_comunitario_prod',
            'RECAPTCHA_SITE_KEY': '6LcYU7stAAAAAPXACptpxKgKmuHSrRXtB4YVZuSX',
            'RECAPTCHA_SECRET_KEY': '6LcYU7stAAAAAAj-TjOddvIqjx6unLXCuqzW2-LH',
            'SESSION_COOKIE_SECURE': True,
        }

    def test_valid_production_config_passes(self):
        """Una configuración completa y segura debe superar la validación sin excepciones."""
        cfg = self._get_valid_prod_config()
        try:
            validate_production_config(cfg)
        except RuntimeError as e:
            self.fail(f"validate_production_config falló inesperadamente: {e}")

    def test_missing_secret_key_fails(self):
        """Falta de SECRET_KEY debe lanzar RuntimeError."""
        cfg = self._get_valid_prod_config()
        cfg['SECRET_KEY'] = ''
        with self.assertRaises(RuntimeError) as ctx:
            validate_production_config(cfg)
        self.assertIn("SECRET_KEY es obligatoria", str(ctx.exception))

    def test_insecure_default_secret_key_fails(self):
        """Uso de la clave de desarrollo por defecto debe lanzar RuntimeError."""
        cfg = self._get_valid_prod_config()
        cfg['SECRET_KEY'] = 'dev-secret-key-change-in-production'
        with self.assertRaises(RuntimeError) as ctx:
            validate_production_config(cfg)
        self.assertIn("SECRET_KEY contiene un valor de desarrollo inseguro", str(ctx.exception))

    def test_short_secret_key_fails(self):
        """SECRET_KEY menor a 16 caracteres debe lanzar RuntimeError."""
        cfg = self._get_valid_prod_config()
        cfg['SECRET_KEY'] = 'shortkey123'
        with self.assertRaises(RuntimeError) as ctx:
            validate_production_config(cfg)
        self.assertIn("longitud mínima de 16 caracteres", str(ctx.exception))

    def test_empty_db_password_fails(self):
        """DB_PASSWORD vacía en producción debe lanzar RuntimeError."""
        cfg = self._get_valid_prod_config()
        cfg['DB_PASSWORD'] = ''
        with self.assertRaises(RuntimeError) as ctx:
            validate_production_config(cfg)
        self.assertIn("DB_PASSWORD es obligatoria", str(ctx.exception))

    def test_missing_db_fields_fails(self):
        """Falta de DB_HOST, DB_USER o DB_NAME debe lanzar RuntimeError con lista detallada."""
        cfg = self._get_valid_prod_config()
        cfg['DB_HOST'] = ''
        cfg['DB_USER'] = ''
        cfg['DB_NAME'] = ''
        with self.assertRaises(RuntimeError) as ctx:
            validate_production_config(cfg)
        err = str(ctx.exception)
        self.assertIn("DB_HOST", err)
        self.assertIn("DB_USER", err)
        self.assertIn("DB_NAME", err)

    def test_missing_recaptcha_keys_fails(self):
        """Falta de llaves reCAPTCHA en producción debe lanzar RuntimeError."""
        cfg = self._get_valid_prod_config()
        cfg['RECAPTCHA_SITE_KEY'] = ''
        cfg['RECAPTCHA_SECRET_KEY'] = ''
        with self.assertRaises(RuntimeError) as ctx:
            validate_production_config(cfg)
        self.assertIn("RECAPTCHA_SITE_KEY", str(ctx.exception))

    def test_debug_true_fails(self):
        """DEBUG=True en producción debe ser rechazado inmediatamente."""
        cfg = self._get_valid_prod_config()
        cfg['DEBUG'] = True
        with self.assertRaises(RuntimeError) as ctx:
            validate_production_config(cfg)
        self.assertIn("DEBUG no puede ser True", str(ctx.exception))

    def test_mock_mode_true_fails(self):
        """MOCK_MODE=True en producción debe ser rechazado inmediatamente."""
        cfg = self._get_valid_prod_config()
        cfg['MOCK_MODE'] = True
        with self.assertRaises(RuntimeError) as ctx:
            validate_production_config(cfg)
        self.assertIn("MOCK_MODE no puede ser True", str(ctx.exception))

    def test_insecure_cookie_fails(self):
        """SESSION_COOKIE_SECURE=False en producción debe lanzar RuntimeError."""
        cfg = self._get_valid_prod_config()
        cfg['SESSION_COOKIE_SECURE'] = False
        with self.assertRaises(RuntimeError) as ctx:
            validate_production_config(cfg)
        self.assertIn("SESSION_COOKIE_SECURE debe ser True", str(ctx.exception))


class TestProductionDemoModeNeutralization(unittest.TestCase):
    """Verifica que en entornos de producción no se filtre ningún dato demo ni se permita modo mock."""

    def test_database_is_mock_mode_strictly_false_in_production(self):
        """database.is_mock_mode() debe retornar False incondicionalmente si FLASK_ENV=production."""
        with app.app_context():
            app.config['FLASK_ENV'] = 'production'
            app.config['MOCK_MODE'] = True
            self.assertFalse(database.is_mock_mode(), "is_mock_mode debe ser False en producción aún con MOCK_MODE=True")

    def test_dashboard_mock_mode_enabled_strictly_false_in_production(self):
        """dashboard_service.mock_mode_enabled() debe retornar False incondicionalmente en producción."""
        with app.app_context():
            app.config['FLASK_ENV'] = 'production'
            app.config['MOCK_MODE'] = True
            self.assertFalse(dashboard_service.mock_mode_enabled(), "mock_mode_enabled debe ser False en producción")

    def test_get_cdp_detalle_returns_none_when_db_down_in_production(self):
        """Si la BD no responde y mock_mode está inactivo (producción), get_cdp_detalle debe retornar None."""
        with app.app_context():
            app.config['FLASK_ENV'] = 'production'
            app.config['MOCK_MODE'] = False
            with patch('services.cdp_service.get_db_connection', return_value=None):
                detalle = cdp_service.get_cdp_detalle(1)
                self.assertIsNone(detalle, "En producción sin BD no debe hacer fallback a mock_data")


class TestProductionAuthHardening(unittest.TestCase):
    """Verifica que el login en producción no permita usuarios demo y no muestre banner de desarrollo."""

    def setUp(self):
        self.client = app.test_client()
        self._orig_env = app.config.get('FLASK_ENV')
        self._orig_mock = app.config.get('MOCK_MODE')
        self._orig_debug = app.config.get('DEBUG')
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

    def tearDown(self):
        app.config['FLASK_ENV'] = self._orig_env
        app.config['MOCK_MODE'] = self._orig_mock
        app.config['DEBUG'] = self._orig_debug

    def test_login_demo_credentials_blocked_in_production_when_db_down(self):
        """En producción con BD caída, intentar admin/admin o supervisor/supervisor debe ser denegado."""
        app.config['FLASK_ENV'] = 'production'
        app.config['DEBUG'] = False
        app.config['MOCK_MODE'] = False

        # Simulamos respuesta exitosa de reCAPTCHA pero base de datos caída
        recaptcha_mock = MagicMock()
        recaptcha_mock.json.return_value = {"success": True, "score": 0.9, "action": "login"}

        with patch('requests.post', return_value=recaptcha_mock), \
             patch('routes.auth_routes.get_db_connection', return_value=None):

            resp = self.client.post('/iniciar_sesion', data={
                'usuario': 'admin',
                'contrasena': 'admin',
                'g-recaptcha-response': 'fake-token'
            })

            # Debe retornar a login con mensaje de servicio no disponible y NO redirigir a dashboard
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Servicio no disponible temporalmente", resp.get_data(as_text=True))

            # Comprobar que no hay sesión creada
            with self.client.session_transaction() as sess:
                self.assertNotIn('usuario', sess)
                self.assertNotIn('rol', sess)

    def test_login_dev_banner_hidden_in_production(self):
        """La pantalla de login NO debe mostrar el banner de credenciales de prueba en producción."""
        app.config['FLASK_ENV'] = 'production'
        app.config['DEBUG'] = False
        app.config['MOCK_MODE'] = False

        resp = self.client.get('/iniciar_sesion')
        html = resp.get_data(as_text=True)
        self.assertNotIn("Entorno de Desarrollo", html)
        self.assertNotIn("Usuarios de prueba", html)


if __name__ == '__main__':
    unittest.main()

