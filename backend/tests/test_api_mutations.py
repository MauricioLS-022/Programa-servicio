"""
tests/test_api_mutations.py - Pruebas automatizadas de integración para los nuevos endpoints REST:
1. Soporte de identificadores UUID en actualización y eliminación de reportes.
2. Endpoints REST de administración de usuarios (listado, creación, edición, toggle, eliminación con candados).
3. Endpoints REST de estructura ministerial (ficha técnica de CDP con aislamiento territorial, mutaciones de redes y líderes).
4. Endpoints REST de perfil de usuario (consulta, actualización de username y password con validación de complejidad).
"""
import unittest
from unittest.mock import patch, MagicMock
from app import app
from utils.cache import invalidate_dashboard_cache


class TestApiMutationsIntegration(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        invalidate_dashboard_cache()

    def tearDown(self):
        invalidate_dashboard_cache()

    # -------------------------------------------------------------------------
    # 1. Reportes: Soporte de UUID en PUT y DELETE
    # -------------------------------------------------------------------------
    @patch('routes.api.reportes_api.actualizar_reporte')
    def test_api_reportes_put_uuid_supported(self, mock_act):
        """PUT /api/reportes/<uuid> no debe dar 404 por incompatibilidad de tipo."""
        mock_act.return_value = (True, "Reporte actualizado exitosamente.")
        uuid_str = "e2b17a10-23a9-4b68-98f5-96144e5ad623"

        with self.client.session_transaction() as sess:
            sess['usuario_id'] = "admin-uuid"
            sess['rol'] = 'admin'

        response = self.client.put(f'/api/reportes/{uuid_str}', json={'tema': 'Nuevo Tema'})
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue(json_data.get('success'))
        mock_act.assert_called_once()
        self.assertEqual(mock_act.call_args[0][0], uuid_str)

    @patch('routes.api.reportes_api.eliminar_reporte')
    def test_api_reportes_delete_uuid_supported(self, mock_elim):
        """DELETE /api/reportes/<uuid> debe recibir la cadena UUID correctamente."""
        mock_elim.return_value = (True, "Reporte eliminado exitosamente.")
        uuid_str = "e2b17a10-23a9-4b68-98f5-96144e5ad623"

        with self.client.session_transaction() as sess:
            sess['usuario_id'] = "admin-uuid"
            sess['rol'] = 'admin'

        response = self.client.delete(f'/api/reportes/{uuid_str}')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue(json_data.get('success'))
        mock_elim.assert_called_once()
        self.assertEqual(mock_elim.call_args[0][0], uuid_str)

    # -------------------------------------------------------------------------
    # 2. Usuarios REST: Permisos y Candados
    # -------------------------------------------------------------------------
    def test_api_usuarios_requires_admin(self):
        """Usuarios no admin deben recibir 403 Forbidden."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = "sup-uuid"
            sess['rol'] = 'supervisor'

        response = self.client.get('/api/usuarios')
        self.assertEqual(response.status_code, 403)

    @patch('routes.api.usuarios_api.get_usuarios_context')
    def test_api_usuarios_list_admin(self, mock_context):
        """Admin debe poder listar usuarios con estadísticas."""
        mock_context.return_value = {
            'usuarios': [{'id': 'u1', 'username': 'admin', 'nombre': 'Admin', 'apellido': 'Sys', 'rol': 'admin', 'is_active': 1}],
            'total_usuarios': 1,
            'total_activos': 1,
            'page': 1,
            'pages': 1
        }
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = "admin-uuid"
            sess['rol'] = 'admin'

        response = self.client.get('/api/usuarios')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get('total'), 1)
        self.assertEqual(data.get('total_activos'), 1)

    @patch('routes.api.usuarios_api.eliminar_usuario_servicio')
    def test_api_usuarios_delete_guard(self, mock_eliminar):
        """Eliminar usuario con candado debe retornar 400 con mensaje descriptivo."""
        mock_eliminar.return_value = (False, 'danger', 'No se puede eliminar: el usuario es supervisor de una red.')

        with self.client.session_transaction() as sess:
            sess['usuario_id'] = "admin-uuid"
            sess['rol'] = 'admin'

        response = self.client.delete('/api/usuarios/target-uuid')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data.get('success'))
        self.assertIn('supervisor', data.get('error', '').lower())

    # -------------------------------------------------------------------------
    # 3. Estructura REST: Detalle CDP y Aislamiento Territorial
    # -------------------------------------------------------------------------
    @patch('routes.api.estructura_api.get_cdp_detalle')
    def test_api_cdp_detalle_supervisor_isolation(self, mock_detalle):
        """Supervisor no puede consultar una Casa de Paz fuera de su red asignada (403 Anti-IDOR)."""
        mock_detalle.return_value = {
            'id': 10,
            'codigo': 'CDP-010',
            'red_id': 2, # Red ajena
            'anfitrion': 'Juan Perez'
        }

        with self.client.session_transaction() as sess:
            sess['usuario_id'] = "sup-uuid"
            sess['rol'] = 'supervisor'

        with patch('routes.api.estructura_api.get_supervisor_red_id', return_value=1): # Red 1 asignada
            response = self.client.get('/api/casas_de_paz/10')
            self.assertEqual(response.status_code, 403)
            data = response.get_json()
            self.assertIn('No autorizado', data.get('error', ''))

    @patch('routes.api.estructura_api.get_cdp_detalle')
    def test_api_cdp_detalle_admin_success(self, mock_detalle):
        """Admin puede consultar la ficha completa de cualquier Casa de Paz."""
        mock_detalle.return_value = {
            'id': 5,
            'codigo': 'HEB-001',
            'red_id': 1,
            'anfitrion': 'Carlos Gomez',
            'asistencia_promedio': 22,
            'total_reportes': 8
        }

        with self.client.session_transaction() as sess:
            sess['usuario_id'] = "admin-uuid"
            sess['rol'] = 'admin'

        response = self.client.get('/api/casas_de_paz/5')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('cdp', data)
        self.assertEqual(data['cdp']['codigo'], 'HEB-001')

    # -------------------------------------------------------------------------
    # 4. Perfil REST: Consulta y Actualización
    # -------------------------------------------------------------------------
    @patch('routes.api.auth_api.get_perfil_data')
    def test_api_perfil_get(self, mock_perfil):
        """Usuario autenticado puede consultar sus datos de perfil y asignaciones."""
        mock_perfil.return_value = {
            'id': 'user-1',
            'username': 'pastor',
            'nombre': 'David',
            'apellido': 'Vino',
            'tipo_usuario': 'admin',
            'asignacion_admin': 'Acceso Global'
        }

        with self.client.session_transaction() as sess:
            sess['usuario_id'] = "user-1"
            sess['usuario'] = "pastor"
            sess['rol'] = "admin"

        response = self.client.get('/api/perfil')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['perfil']['username'], 'pastor')

    def test_api_perfil_password_validation(self):
        """Validar política de complejidad en cambio de contraseña."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = "user-1"
            sess['usuario'] = "pastor"
            sess['rol'] = "admin"

        # Contraseña débil (sin mayúsculas o números)
        response = self.client.post('/api/perfil/password', json={
            'password_actual': 'Actual123!',
            'password_nueva': 'debil',
            'password_confirmar': 'debil'
        })
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data.get('success'))


if __name__ == '__main__':
    unittest.main()

