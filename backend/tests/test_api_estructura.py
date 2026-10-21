"""
tests/test_api_estructura.py - Pruebas para endpoints REST de Estructura Ministerial.
Valida /api/redes, /api/casas_de_paz y /api/lideres con control de acceso y anti-IDOR.
"""
import unittest
from unittest.mock import patch, MagicMock
from app import app


class TestApiEstructuraEndpoints(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-estructura-123'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_unauthenticated_requests(self):
        """Endpoints de estructura sin autenticación deben retornar 401."""
        self.assertEqual(self.client.get('/api/redes').status_code, 401)
        self.assertEqual(self.client.get('/api/casas_de_paz').status_code, 401)
        self.assertEqual(self.client.get('/api/lideres').status_code, 401)

    def test_get_redes_admin(self):
        """Admin obtiene listado de redes activas."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'admin-uuid-1'
            sess['usuario'] = 'admin'
            sess['rol'] = 'admin'

        response = self.client.get('/api/redes')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('redes', data)
        self.assertIsInstance(data['redes'], list)

    def test_get_redes_supervisor_scoped(self):
        """Supervisor sólo recibe la red que tiene asignada."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'supervisor-uuid-1'
            sess['usuario'] = 'supervisor1'
            sess['rol'] = 'supervisor'

        with patch('routes.api.estructura_api.get_supervisor_red_id', return_value=2):
            response = self.client.get('/api/redes')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertIn('redes', data)
            for red in data['redes']:
                self.assertEqual(red.get('id'), 2)

    def test_get_casas_de_paz_supervisor_anti_idor(self):
        """Supervisor no puede consultar Casas de Paz de otra red (403 Forbidden)."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'supervisor-uuid-1'
            sess['usuario'] = 'supervisor1'
            sess['rol'] = 'supervisor'

        with patch('routes.api.estructura_api.get_supervisor_red_id', return_value=1):
            # Intento de consultar red 2
            res_denied = self.client.get('/api/casas_de_paz?red_id=2')
            self.assertEqual(res_denied.status_code, 403)

            # Consulta legítima de su red 1
            res_allowed = self.client.get('/api/casas_de_paz?red_id=1')
            self.assertEqual(res_allowed.status_code, 200)
            data = res_allowed.get_json()
            self.assertIn('casas', data)

    def test_get_lideres_paginated(self):
        """Admin consulta listado de líderes con paginación."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'admin-uuid-1'
            sess['usuario'] = 'admin'
            sess['rol'] = 'admin'

        response = self.client.get('/api/lideres?page=1&per_page=5')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('lideres', data)
        self.assertIn('total', data)
        self.assertEqual(data.get('page'), 1)


if __name__ == '__main__':
    unittest.main()

