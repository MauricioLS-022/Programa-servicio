"""
tests/test_api_reportes.py - Pruebas para endpoints REST de Reportes.
Valida GET, POST, PUT, DELETE /api/reportes, control de roles y blindaje anti-IDOR.
"""
import unittest
from unittest.mock import patch, MagicMock
from app import app


class TestApiReportesEndpoints(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-reportes-123'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_reportes_unauthenticated(self):
        """Petición a /api/reportes sin sesión activa debe retornar 401."""
        res_get = self.client.get('/api/reportes')
        self.assertEqual(res_get.status_code, 401)

        res_post = self.client.post('/api/reportes', json={})
        self.assertEqual(res_post.status_code, 401)

    def test_get_reportes_admin(self):
        """Admin puede listar y filtrar reportes de cualquier red y CDP."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'admin-uuid-1'
            sess['usuario'] = 'admin'
            sess['rol'] = 'admin'

        response = self.client.get('/api/reportes?page=1&per_page=5')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('reportes', data)
        self.assertIn('total', data)
        self.assertEqual(data.get('page'), 1)

    def test_get_reportes_supervisor_anti_idor(self):
        """Supervisor sólo puede consultar reportes de su red asignada (403 si intenta otra)."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'supervisor-uuid-1'
            sess['usuario'] = 'supervisor1'
            sess['rol'] = 'supervisor'

        with patch('routes.api.reportes_api.get_supervisor_red_id', return_value=1):
            # Intento de consultar red 2 siendo supervisor de red 1
            res_denied = self.client.get('/api/reportes?red_id=2')
            self.assertEqual(res_denied.status_code, 403)

            # Consulta legítima de su propia red
            res_allowed = self.client.get('/api/reportes?red_id=1')
            self.assertEqual(res_allowed.status_code, 200)

    def test_get_reportes_lider_cdp_scoped(self):
        """Líder CDP sólo puede ver reportes de su propia Casa de Paz."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'lider-uuid-1'
            sess['usuario'] = 'lider1'
            sess['rol'] = 'lider_cdp'

        with patch('routes.api.reportes_api.get_cdp_datos_usuario', return_value=({'id': 10, 'codigo': 'NOR-001'}, [])):
            # Intento de consultar CDP 99
            res_denied = self.client.get('/api/reportes?cdp_id=99')
            self.assertEqual(res_denied.status_code, 403)

            # Consulta legítima de su CDP 10
            res_allowed = self.client.get('/api/reportes')
            self.assertEqual(res_allowed.status_code, 200)

    def test_post_reporte_lider_cdp(self):
        """Líder CDP registra un reporte usando process_reporte."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'lider-uuid-1'
            sess['usuario'] = 'lider1'
            sess['rol'] = 'lider_cdp'

        payload = {
            'fecha': '2026-10-21',
            'tema': 'La Fe en Acción',
            'asistencia': 15,
            'ofrenda_usd': 20.0,
            'ofrenda_bs': 500.0
        }

        with patch('routes.api.reportes_api.get_cdp_datos_usuario', return_value=({'id': 10}, [])), \
             patch('routes.api.reportes_api.process_reporte', return_value=(True, "Reporte guardado exitosamente.")):
            response = self.client.post('/api/reportes', json=payload)
            self.assertEqual(response.status_code, 201)
            data = response.get_json()
            self.assertTrue(data.get('success'))
            self.assertEqual(data.get('cdp_id'), 10)

    def test_put_reporte(self):
        """Actualización de un reporte existente con respuesta JSON."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'lider-uuid-1'
            sess['usuario'] = 'lider1'
            sess['rol'] = 'lider_cdp'

        with patch('routes.api.reportes_api.get_cdp_datos_usuario', return_value=({'id': 10}, [])), \
             patch('routes.api.reportes_api.actualizar_reporte', return_value=(True, "Reporte actualizado.")):
            response = self.client.put('/api/reportes/5', json={'asistencia': 18})
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data.get('success'))

    def test_delete_reporte(self):
        """Eliminación de un reporte con validación de permisos."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'lider-uuid-1'
            sess['usuario'] = 'lider1'
            sess['rol'] = 'lider_cdp'

        with patch('routes.api.reportes_api.get_cdp_datos_usuario', return_value=({'id': 10}, [])), \
             patch('routes.api.reportes_api.eliminar_reporte', return_value=(True, "Reporte eliminado.")):
            response = self.client.delete('/api/reportes/5')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data.get('success'))


if __name__ == '__main__':
    unittest.main()

