"""
Tests integrales de reactivación y alternancia de estado para Vino Nuevo:
- Casas de Paz (CDP): Reactivación, bloqueo si Red está pausada, sincronización de cuenta de usuario.
- Líderes: Reactivación, bloqueo si CDP está pausada.
- Usuarios: Reactivación y alternancia de estado.
- Rutas HTTP de administración, control de acceso CSRF/roles, y validación de caché.
"""
import unittest
from unittest.mock import patch, MagicMock
from app import app
from db_queries import (
    toggle_estado_cdp,
    toggle_estado_lider,
    toggle_estado_usuario,
)
from services.cdp_service import toggle_cdp_servicio
from services.leader_service import toggle_lider_servicio
from services.user_service import toggle_usuario_servicio


class TestReactivacionEstadoIntegral(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.client = app.test_client()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

    # -------------------------------------------------------------
    # 1. DB Queries: Jerarquía y Sincronización
    # -------------------------------------------------------------
    def test_cdp_reactivacion_bloqueada_si_red_inactiva(self):
        """No se puede reactivar una CDP si su Red asociada está inactiva."""
        cursor = MagicMock()
        cursor.fetchone.return_value = {
            'id': 10,
            'codigo': 'CDP-01',
            'is_active': 0,
            'red_id': 5,
            'usuario_id': 'u-1',
            'red_nombre': 'Red Alfa',
            'red_is_active': 0,
        }

        ok, status, msg = toggle_estado_cdp(cursor, 10)
        self.assertFalse(ok)
        self.assertEqual(status, 'bloqueada')
        self.assertIn('Red', msg)

    def test_cdp_reactivacion_exitosa_sincroniza_usuario(self):
        """Al reactivar una CDP con Red activa, sincroniza usuario.is_active = 1."""
        cursor = MagicMock()
        cursor.fetchone.return_value = {
            'id': 10,
            'codigo': 'CDP-01',
            'is_active': 0,
            'red_id': 5,
            'usuario_id': 'u-1',
            'red_nombre': 'Red Alfa',
            'red_is_active': 1,
        }

        ok, status, msg = toggle_estado_cdp(cursor, 10)
        self.assertTrue(ok)
        self.assertEqual(status, 'reactivada')
        cursor.execute.assert_any_call("UPDATE usuario SET is_active = 1 WHERE id = %s", ('u-1',))

    def test_lider_reactivacion_bloqueada_si_cdp_inactiva(self):
        """No se puede reactivar un Líder si su Casa de Paz está inactiva."""
        cursor = MagicMock()
        cursor.fetchone.return_value = {
            'id': 7,
            'nombre': 'Carlos',
            'apellido': 'Ríos',
            'is_active': 0,
            'cdp_id': 20,
            'cdp_codigo': 'CDP-Norte',
            'cdp_is_active': 0,
        }

        ok, status, msg = toggle_estado_lider(cursor, 7)
        self.assertFalse(ok)
        self.assertEqual(status, 'bloqueada')
        self.assertIn('Casa de Paz', msg)

    def test_lider_reactivacion_exitosa_si_cdp_activa(self):
        """Se reactiva un Líder si su Casa de Paz asignada está activa."""
        cursor = MagicMock()
        cursor.fetchone.return_value = {
            'id': 7,
            'nombre': 'Carlos',
            'apellido': 'Ríos',
            'is_active': 0,
            'cdp_id': 20,
            'cdp_codigo': 'CDP-Norte',
            'cdp_is_active': 1,
        }

        ok, status, msg = toggle_estado_lider(cursor, 7)
        self.assertTrue(ok)
        self.assertEqual(status, 'reactivado')

    def test_usuario_toggle_estado(self):
        """Alterna el estado is_active de una cuenta de usuario."""
        cursor = MagicMock()
        cursor.fetchone.return_value = {'id': 'u-99', 'username': 'pedro', 'is_active': 1}

        ok, status, msg = toggle_estado_usuario(cursor, 'u-99')
        self.assertTrue(ok)
        self.assertEqual(status, 'desactivado')

    # -------------------------------------------------------------
    # 2. Servicios: Cache Invalidation y Manejo Transaccional
    # -------------------------------------------------------------
    @patch('services.cdp_service.get_db_connection')
    @patch('services.cdp_service.invalidate_dashboard_cache')
    def test_toggle_cdp_servicio_invalida_cache(self, mock_inv_cache, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        mock_cursor.fetchone.return_value = {
            'id': 10,
            'codigo': 'CDP-01',
            'is_active': 1,
            'red_id': 5,
            'usuario_id': 'u-1',
            'red_nombre': 'Red Alfa',
            'red_is_active': 1,
        }

        ok, status, msg = toggle_cdp_servicio(10)
        self.assertTrue(ok)
        mock_conn.commit.assert_called_once()
        mock_inv_cache.assert_called_once()

    # -------------------------------------------------------------
    # 3. Rutas HTTP de Administración
    # -------------------------------------------------------------
    @patch('routes.admin_routes.toggle_lider_servicio')
    def test_route_lider_toggle_estado(self, mock_toggle_lider):
        mock_toggle_lider.return_value = (True, 'reactivado', 'Líder reactivado con éxito.')
        with self.client.session_transaction() as sess:
            sess['usuario'] = 'admin'
            sess['rol'] = 'admin'
            sess['usuario_id'] = 'admin-uuid'

        resp = self.client.post('/admin/lider/5/toggle_estado', follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        mock_toggle_lider.assert_called_once_with('5')

    @patch('routes.admin_routes.toggle_cdp_servicio')
    def test_route_cdp_toggle_estado(self, mock_toggle_cdp):
        mock_toggle_cdp.return_value = (True, 'reactivada', 'Casa de Paz reactivada con éxito.')
        with self.client.session_transaction() as sess:
            sess['usuario'] = 'admin'
            sess['rol'] = 'admin'
            sess['usuario_id'] = 'admin-uuid'

        resp = self.client.post('/admin/casa_de_paz/12/toggle_estado', follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        mock_toggle_cdp.assert_called_once_with('12')

    @patch('routes.admin_routes.toggle_usuario_servicio')
    def test_route_usuario_toggle_estado(self, mock_toggle_user):
        mock_toggle_user.return_value = (True, 'reactivado', 'Usuario reactivado.')
        with self.client.session_transaction() as sess:
            sess['usuario'] = 'admin'
            sess['rol'] = 'admin'
            sess['usuario_id'] = 'admin-uuid'

        resp = self.client.post('/admin/usuario/uuid-test/toggle_estado', follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        mock_toggle_user.assert_called_once_with('uuid-test')


if __name__ == '__main__':
    unittest.main()

