"""
Tests unitarios para:
1. Candados de integridad al eliminar líderes en eliminar_lider_servicio y eliminar_pausar_lider (bloqueo ante reportes históricos).
2. Eliminación física permitida cuando el líder no tiene reportes asociados.
3. Ruta admin.lider_eliminar y su delegación en eliminar_lider_servicio.
"""
import unittest
from unittest.mock import patch, MagicMock
from app import app
from services.leader_service import eliminar_lider_servicio
from db_queries import eliminar_pausar_lider


class TestLiderDeleteGuards(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.client = app.test_client()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

    def test_eliminar_lider_id_invalido(self):
        """Debe rechazar identificadores no numéricos."""
        exito, categoria, mensaje = eliminar_lider_servicio("invalido")
        self.assertFalse(exito)
        self.assertEqual(categoria, "danger")
        self.assertIn("no válido", mensaje)

    @patch('services.leader_service.get_db_connection')
    def test_eliminar_lider_con_reportes_bloqueado(self, mock_get_conn):
        """No debe permitir eliminar un líder si tiene reportes asociados para evitar datos huérfanos."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.side_effect = [
            {'id': 5, 'nombre': 'Andrés', 'apellido': 'Soler', 'is_active': 1},  # Líder existe
            {'total': 15},  # Tiene 15 reportes
        ]
        mock_get_conn.return_value = mock_conn

        exito, categoria, mensaje = eliminar_lider_servicio(5)
        self.assertFalse(exito)
        self.assertEqual(categoria, "danger")
        self.assertIn("15 reporte(s)", mensaje)
        self.assertIn("ponerlo en pausa", mensaje)
        mock_conn.rollback.assert_called_once()
        # Verificar que no se haya ejecutado DELETE
        for call_args in mock_cursor.execute.call_args_list:
            self.assertNotIn("DELETE FROM lider", str(call_args))

    @patch('services.leader_service.get_db_connection')
    def test_eliminar_lider_sin_reportes_exitoso(self, mock_get_conn):
        """Debe permitir eliminar un líder de forma física si no tiene reportes asociados."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.side_effect = [
            {'id': 10, 'nombre': 'Carlos', 'apellido': 'Mendoza', 'is_active': 1},  # Líder existe
            {'total': 0},  # Sin reportes
        ]
        mock_get_conn.return_value = mock_conn

        exito, categoria, mensaje = eliminar_lider_servicio(10)
        self.assertTrue(exito)
        self.assertEqual(categoria, "success")
        self.assertIn("eliminado exitosamente", mensaje)
        mock_conn.commit.assert_called_once()
        mock_cursor.execute.assert_any_call("DELETE FROM lider WHERE id = %s", (10,))

    @patch('routes.admin_routes.eliminar_lider_servicio')
    def test_ruta_admin_lider_eliminar_delegacion_y_redirect(self, mock_eliminar):
        """La ruta admin.lider_eliminar debe invocar eliminar_lider_servicio y redirigir a admin.lider."""
        mock_eliminar.return_value = (False, "danger", "Bloqueado por reportes")

        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'admin-uuid'
            sess['rol'] = 'admin'

        response = self.client.post('/admin/lider/5/eliminar')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/lider', response.headers['Location'])
        mock_eliminar.assert_called_once_with(5)


if __name__ == '__main__':
    unittest.main()
