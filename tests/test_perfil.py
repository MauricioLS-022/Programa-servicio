"""
Tests unitarios y de integración para la página de Perfil:
- Funciones de servicio (cambiar_username, cambiar_password, update_perfil)
- Rutas GET y POST de perfil en admin, supervisor y lider_cdp
- Validaciones de longitud, contraseñas actuales y duplicados
"""
import unittest
from unittest.mock import patch, MagicMock
from werkzeug.security import generate_password_hash
from app import app
from services.cdp_service import (
    cambiar_username,
    cambiar_password,
    update_perfil,
    get_perfil_data
)


class TestPerfilService(unittest.TestCase):
    """Pruebas unitarias de las funciones de perfil en cdp_service."""

    def test_cambiar_username_validacion_longitud(self):
        """Rechaza usernames con menos de 3 caracteres."""
        exito, msg = cambiar_username('usr-1', 'ab')
        self.assertFalse(exito)
        self.assertIn('3 caracteres', msg)

    @patch('services.cdp_service.get_db_connection')
    def test_cambiar_username_sin_conexion(self, mock_db):
        """Retorna False si no hay conexión a la base de datos."""
        mock_db.return_value = None
        exito, msg = cambiar_username('usr-1', 'nuevo_usuario')
        self.assertFalse(exito)
        self.assertIn('conectar', msg.lower())

    @patch('services.cdp_service.get_db_connection')
    def test_cambiar_username_duplicado(self, mock_db):
        """Rechaza el cambio si el username ya pertenece a otro usuario."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {'id': 'otro-usuario-id'}
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db.return_value = mock_conn

        exito, msg = cambiar_username('usr-1', 'usuario_existente')
        self.assertFalse(exito)
        self.assertIn('ya está en uso', msg.lower())

    @patch('services.cdp_service.get_db_connection')
    def test_cambiar_username_exito(self, mock_db):
        """Permite cambiar el username si está disponible."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None  # No duplicate
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db.return_value = mock_conn

        exito, msg = cambiar_username('usr-1', 'usuario_nuevo_valido')
        self.assertTrue(exito)
        self.assertIn('exitosamente', msg.lower())
        mock_conn.commit.assert_called_once()

    def test_cambiar_password_validacion_longitud(self):
        """Rechaza contraseñas con menos de 6 caracteres."""
        exito, msg = cambiar_password('usr-1', 'actual123', '12345')
        self.assertFalse(exito)
        self.assertIn('6 caracteres', msg)

    @patch('services.cdp_service.get_db_connection')
    def test_cambiar_password_actual_incorrecta(self, mock_db):
        """Rechaza el cambio si la contraseña actual no coincide con el hash."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        hash_real = generate_password_hash('password_correcta')
        mock_cursor.fetchone.return_value = {'password': hash_real}
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db.return_value = mock_conn

        exito, msg = cambiar_password('usr-1', 'password_erronea', 'nueva_password_123')
        self.assertFalse(exito)
        self.assertIn('incorrecta', msg.lower())

    @patch('services.cdp_service.get_db_connection')
    def test_cambiar_password_exito(self, mock_db):
        """Permite cambiar la contraseña si la actual es válida."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        hash_real = generate_password_hash('password_correcta')
        mock_cursor.fetchone.return_value = {'password': hash_real}
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db.return_value = mock_conn

        exito, msg = cambiar_password('usr-1', 'password_correcta', 'nueva_password_segura')
        self.assertTrue(exito)
        self.assertIn('exitosamente', msg.lower())
        mock_conn.commit.assert_called_once()


class TestPerfilRoutes(unittest.TestCase):
    """Pruebas de integración de las rutas /perfil en todos los roles."""

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key-perfil'
        self.client = app.test_client()

    def test_perfil_requiere_login(self):
        """El acceso anónimo a /admin/perfil debe redirigir al login."""
        response = self.client.get('/admin/perfil')
        self.assertEqual(response.status_code, 302)

    @patch('services.cdp_service.get_db_connection')
    def test_perfil_admin_get(self, mock_db):
        """El perfil de admin debe cargar exitosamente los datos y la plantilla."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            'id': 'admin-uuid-1',
            'username': 'admin',
            'nombre': 'Mauricio',
            'apellido': 'Leal',
            'tipo_usuario': 'admin'
        }
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db.return_value = mock_conn

        with self.client.session_transaction() as sess:
            sess['usuario'] = 'admin'
            sess['usuario_id'] = 'admin-uuid-1'
            sess['rol'] = 'admin'

        response = self.client.get('/admin/perfil')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Mi Perfil', response.data)
        self.assertIn(b'Cambiar Usuario', response.data)
        self.assertIn(b'Cambiar Contrase', response.data)
        self.assertIn(b'Apariencia', response.data)

    @patch('services.cdp_service.get_db_connection')
    def test_perfil_supervisor_get(self, mock_db):
        """El perfil de supervisor debe cargar con rol supervisor."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            'id': 'super-uuid-1',
            'username': 'super',
            'nombre': 'Carlos',
            'apellido': 'Mendoza',
            'tipo_usuario': 'supervisor'
        }
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db.return_value = mock_conn

        with self.client.session_transaction() as sess:
            sess['usuario'] = 'super'
            sess['usuario_id'] = 'super-uuid-1'
            sess['rol'] = 'supervisor'

        response = self.client.get('/supervisor/perfil')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Mi Perfil', response.data)

    @patch('services.cdp_service.get_db_connection')
    def test_perfil_lider_get(self, mock_db):
        """El perfil de líder de CDP debe cargar con rol lider_cdp."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            'id': 'lider-uuid-1',
            'username': 'lider',
            'nombre': 'Pedro',
            'apellido': 'García',
            'tipo_usuario': 'lider_cdp'
        }
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db.return_value = mock_conn

        with self.client.session_transaction() as sess:
            sess['usuario'] = 'lider'
            sess['usuario_id'] = 'lider-uuid-1'
            sess['rol'] = 'lider_cdp'

        response = self.client.get('/lider_cdp/perfil')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Mi Perfil', response.data)

    @patch('services.cdp_service.cambiar_username')
    @patch('services.cdp_service.get_perfil_data')
    def test_perfil_post_cambiar_username(self, mock_perfil, mock_change_usr):
        """El envío de formulario para cambiar username debe llamar al servicio y redirigir."""
        mock_change_usr.return_value = (True, 'Nombre de usuario actualizado exitosamente')

        with self.client.session_transaction() as sess:
            sess['usuario'] = 'admin'
            sess['usuario_id'] = 'admin-uuid-1'
            sess['rol'] = 'admin'

        response = self.client.post('/admin/perfil', data={
            'action': 'cambiar_username',
            'nuevo_username': 'admin_renovado'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/perfil', response.headers.get('Location', ''))

    @patch('services.cdp_service.cambiar_password')
    @patch('services.cdp_service.get_perfil_data')
    def test_perfil_post_cambiar_password(self, mock_perfil, mock_change_pwd):
        """El envío de formulario para cambiar contraseña debe llamar al servicio."""
        mock_change_pwd.return_value = (True, 'Contraseña actualizada exitosamente')

        with self.client.session_transaction() as sess:
            sess['usuario'] = 'admin'
            sess['usuario_id'] = 'admin-uuid-1'
            sess['rol'] = 'admin'

        response = self.client.post('/admin/perfil', data={
            'action': 'cambiar_password',
            'password_actual': 'admin',
            'password_nueva': 'nueva_clave_123',
            'password_confirmar': 'nueva_clave_123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/perfil', response.headers.get('Location', ''))

    def test_perfil_post_password_mismatch(self):
        """Si la confirmación de contraseña no coincide, no se actualiza."""
        with self.client.session_transaction() as sess:
            sess['usuario'] = 'admin'
            sess['usuario_id'] = 'admin-uuid-1'
            sess['rol'] = 'admin'

        response = self.client.post('/admin/perfil', data={
            'action': 'cambiar_password',
            'password_actual': 'admin',
            'password_nueva': 'clave12345',
            'password_confirmar': 'claveDiferente'
        })
        self.assertEqual(response.status_code, 302)


if __name__ == '__main__':
    unittest.main()
