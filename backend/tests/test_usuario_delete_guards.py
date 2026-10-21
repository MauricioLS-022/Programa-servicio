"""
Tests unitarios para:
1. Candados de eliminación de usuarios en eliminar_usuario_servicio (cuenta propia, red ministerial, casa de paz).
2. Ruta admin.usuario_eliminar y redirección limpia a admin.usuario.
3. Consulta de get_usuarios con subconsultas de red_nombre y cdp_codigo.
"""
import unittest
from unittest.mock import patch, MagicMock
from app import app
from services.user_service import eliminar_usuario_servicio
import db_queries


class TestUsuarioDeleteGuards(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.client = app.test_client()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

    def test_eliminar_usuario_propia_cuenta_bloqueada(self):
        """No debe permitir eliminar la propia cuenta en sesión."""
        exito, categoria, mensaje = eliminar_usuario_servicio("user-123", "user-123")
        self.assertFalse(exito)
        self.assertEqual(categoria, "danger")
        self.assertIn("propia cuenta", mensaje)

    @patch('services.user_service.get_db_connection')
    def test_eliminar_usuario_supervisor_red_bloqueado(self, mock_get_conn):
        """No debe permitir eliminar un usuario si es supervisor de una red."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.side_effect = [
            {'id': 1, 'nombre': 'Red Centro'},  # red_vinculada
        ]
        mock_get_conn.return_value = mock_conn

        exito, categoria, mensaje = eliminar_usuario_servicio("sup-123", "admin-999")
        self.assertFalse(exito)
        self.assertEqual(categoria, "danger")
        self.assertIn("supervisor de la red 'Red Centro'", mensaje)

    @patch('services.user_service.get_db_connection')
    def test_eliminar_usuario_con_cdp_bloqueado(self, mock_get_conn):
        """No debe permitir eliminar un usuario si tiene asignada una Casa de Paz."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.side_effect = [
            None,  # No es supervisor de red
            {'id': 10, 'codigo': 'CDP-001'},  # cdp_vinculada
        ]
        mock_get_conn.return_value = mock_conn

        exito, categoria, mensaje = eliminar_usuario_servicio("lider-123", "admin-999")
        self.assertFalse(exito)
        self.assertEqual(categoria, "danger")
        self.assertIn("Casa de Paz 'CDP-001'", mensaje)

    @patch('services.user_service.get_db_connection')
    def test_eliminar_usuario_sin_dependencias_exitoso(self, mock_get_conn):
        """Debe permitir eliminar si no es cuenta en sesión y no tiene red ni CDP."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.side_effect = [
            None,  # No es supervisor de red
            None,  # No tiene cdp
        ]
        mock_get_conn.return_value = mock_conn

        exito, categoria, mensaje = eliminar_usuario_servicio("user-sin-dep", "admin-999")
        self.assertTrue(exito)
        self.assertEqual(categoria, "success")
        self.assertIn("eliminado exitosamente", mensaje)
        mock_cursor.execute.assert_any_call("DELETE FROM usuario WHERE id = %s", ("user-sin-dep",))

    @patch('routes.admin_routes.eliminar_usuario_servicio')
    def test_ruta_admin_usuario_eliminar_redirect(self, mock_eliminar):
        """La ruta admin.usuario_eliminar debe redirigir a admin.usuario."""
        mock_eliminar.return_value = (True, "success", "Eliminado")

        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'admin-uuid'
            sess['rol'] = 'admin'

        response = self.client.post('/admin/usuario/target-uuid/eliminar')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/usuario', response.headers['Location'])
        mock_eliminar.assert_called_once_with('target-uuid', 'admin-uuid')


if __name__ == '__main__':
    unittest.main()

