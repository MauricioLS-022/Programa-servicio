"""
Tests unitarios para:
1. Fix de seguridad: Supervisor sin red asignada (get_supervisor_red_id retorna None y sin_red_asignada=True).
2. Filtros en cascada: Coerción y deducción de red_id / cdp_id en get_dashboard_context.
3. Asignación opcional de red y CDP al crear usuarios.
"""
import unittest
from unittest.mock import patch, MagicMock
from app import app
from services.dashboard_service import get_supervisor_red_id, get_dashboard_context
from services.leader_service import crear_nuevo_usuario, get_opciones_asignacion
import db_queries


class TestSupervisorAndCascading(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.client = app.test_client()
        app.config['TESTING'] = True

    @patch('services.dashboard_service.get_db_connection')
    def test_get_supervisor_red_id_unassigned(self, mock_get_conn):
        """Un supervisor sin red asignada debe retornar None, no 1."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None  # No hay red asociada
        mock_get_conn.return_value = mock_conn

        red_id = get_supervisor_red_id('unassigned-uuid')
        self.assertIsNone(red_id)

    @patch('services.dashboard_service.get_supervisor_red_id', return_value=None)
    @patch('services.dashboard_service.get_db_connection', return_value=None)
    def test_dashboard_context_supervisor_unassigned(self, mock_conn, mock_sup_red):
        """Cuando el supervisor no tiene red asignada, el contexto debe tener sin_red_asignada=True."""
        with self.app.test_request_context('/supervisor/dashboard?nivel=red'):
            context = get_dashboard_context('unassigned-uuid', is_supervisor=True)
            self.assertTrue(context['sin_red_asignada'])
            self.assertEqual(context['redes'], [])
            self.assertEqual(context['casas'], [])
            self.assertIsNone(context['red_id'])

    @patch('services.dashboard_service.get_selectores')
    def test_cascading_filters_cdp_to_red_deduction(self, mock_selectores):
        """Si en nivel cdp se da un cdp_id pero no red_id, debe deducirse el red_id del CDP."""
        mock_redes = [{'id': 1, 'nombre': 'Red 1'}, {'id': 2, 'nombre': 'Red 2'}]
        mock_casas = [
            {'id': 10, 'codigo': 'CDP-1', 'red_id': 1},
            {'id': 20, 'codigo': 'CDP-2', 'red_id': 2},
        ]
        mock_selectores.return_value = (mock_redes, mock_casas)

        with self.app.test_request_context('/admin/dashboard?nivel=cdp&cdp_id=20'):
            context = get_dashboard_context('admin-uuid', is_supervisor=False)
            self.assertEqual(context['cdp_id'], 20)
            self.assertEqual(context['red_id'], 2)

    @patch('services.dashboard_service.get_selectores')
    def test_cascading_filters_red_coercion(self, mock_selectores):
        """Si en nivel cdp se selecciona una red y un cdp_id de otra red, se debe corregir al primer CDP de esa red."""
        mock_redes = [{'id': 1, 'nombre': 'Red 1'}, {'id': 2, 'nombre': 'Red 2'}]
        mock_casas = [
            {'id': 10, 'codigo': 'CDP-1', 'red_id': 1},
            {'id': 20, 'codigo': 'CDP-2', 'red_id': 2},
        ]
        mock_selectores.return_value = (mock_redes, mock_casas)

        with self.app.test_request_context('/admin/dashboard?nivel=cdp&red_id=2&cdp_id=10'):
            context = get_dashboard_context('admin-uuid', is_supervisor=False)
            self.assertEqual(context['red_id'], 2)
            self.assertEqual(context['cdp_id'], 20)

    @patch('services.leader_service.get_db_connection')
    @patch('services.leader_service.insertar_usuario', return_value='new-uuid-123')
    @patch('services.leader_service.asignar_supervisor_a_red')
    def test_crear_nuevo_usuario_supervisor_with_red(self, mock_asignar, mock_insertar, mock_conn):
        """Crear usuario supervisor asigna opcionalmente la red indicada."""
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        fake_cursor.fetchone.return_value = None  # username libre
        fake_conn.cursor.return_value.__enter__.return_value = fake_cursor
        mock_conn.return_value = fake_conn

        form_data = {
            'nombre': 'Carlos',
            'apellido': 'Perez',
            'username': 'carlosp',
            'password': 'Password123',
            'tipo_usuario': 'supervisor',
            'red_id': '2'
        }
        success, msg = crear_nuevo_usuario(form_data)
        self.assertTrue(success)
        mock_asignar.assert_called_once_with(fake_cursor, 'new-uuid-123', 2)

    @patch('services.leader_service.get_db_connection')
    @patch('services.leader_service.insertar_usuario', return_value='new-uuid-456')
    @patch('services.leader_service.asignar_usuario_a_cdp')
    def test_crear_nuevo_usuario_lider_with_cdp(self, mock_asignar, mock_insertar, mock_conn):
        """Crear usuario lider_cdp asigna opcionalmente el CDP indicado."""
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        fake_cursor.fetchone.return_value = None  # username libre
        fake_conn.cursor.return_value.__enter__.return_value = fake_cursor
        mock_conn.return_value = fake_conn

        form_data = {
            'nombre': 'Maria',
            'apellido': 'Gomez',
            'username': 'mariag',
            'password': 'Password123',
            'tipo_usuario': 'lider_cdp',
            'cdp_id': '5'
        }
        success, msg = crear_nuevo_usuario(form_data)
        self.assertTrue(success)
        mock_asignar.assert_called_once_with(fake_cursor, 'new-uuid-456', 5)

    @patch('services.user_service.get_db_connection')
    @patch('services.user_service.asignar_supervisor_a_red')
    def test_actualizar_usuario_supervisor_with_red(self, mock_asignar, mock_conn):
        """Actualizar usuario a supervisor asigna la red y libera posibles CDPs."""
        from services.user_service import actualizar_usuario_admin
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        fake_cursor.fetchone.return_value = None  # username único
        fake_conn.cursor.return_value.__enter__.return_value = fake_cursor
        mock_conn.return_value = fake_conn

        form_data = {
            'nombre': 'Carlos',
            'apellido': 'Perez',
            'username': 'carlosp',
            'password': '',
            'tipo_usuario': 'supervisor',
            'red_id': '3'
        }
        success, msg = actualizar_usuario_admin('user-uuid-1', form_data)
        self.assertTrue(success)
        mock_asignar.assert_called_once_with(fake_cursor, 'user-uuid-1', 3)

    @patch('services.user_service.get_db_connection')
    @patch('services.user_service.asignar_usuario_a_cdp')
    def test_actualizar_usuario_lider_with_cdp(self, mock_asignar, mock_conn):
        """Actualizar usuario a lider_cdp asigna el CDP y libera posibles redes."""
        from services.user_service import actualizar_usuario_admin
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        fake_cursor.fetchone.return_value = None  # username único
        fake_conn.cursor.return_value.__enter__.return_value = fake_cursor
        mock_conn.return_value = fake_conn

        form_data = {
            'nombre': 'Maria',
            'apellido': 'Gomez',
            'username': 'mariag',
            'password': '',
            'tipo_usuario': 'lider_cdp',
            'cdp_id': '7'
        }
        success, msg = actualizar_usuario_admin('user-uuid-2', form_data)
        self.assertTrue(success)
        mock_asignar.assert_called_once_with(fake_cursor, 'user-uuid-2', 7)

    @patch('services.user_service.get_db_connection')
    def test_actualizar_usuario_admin_clears_assignments(self, mock_conn):
        """Actualizar usuario a admin desvincula red y CDP."""
        from services.user_service import actualizar_usuario_admin
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        fake_cursor.fetchone.return_value = None  # username único
        fake_conn.cursor.return_value.__enter__.return_value = fake_cursor
        mock_conn.return_value = fake_conn

        form_data = {
            'nombre': 'Admin',
            'apellido': 'General',
            'username': 'admingen',
            'password': '',
            'tipo_usuario': 'admin',
        }
        success, msg = actualizar_usuario_admin('user-uuid-3', form_data)
        self.assertTrue(success)
        # Verificar que se ejecutaron queries de limpieza
        executed_sqls = [call[0][0] for call in fake_cursor.execute.call_args_list]
        self.assertTrue(any('UPDATE red SET supervisor_id = NULL' in sql for sql in executed_sqls))
        self.assertTrue(any('UPDATE cdp SET usuario_id = NULL' in sql for sql in executed_sqls))

    @patch('routes.admin_routes.actualizar_reporte')
    def test_admin_reporte_editar_route(self, mock_update):
        """Admin debe poder editar un reporte vía POST y redirigir con flash."""
        mock_update.return_value = (True, "Reporte actualizado exitosamente.")
        with self.client.session_transaction() as sess:
            sess['usuario'] = 'AdminUser'
            sess['usuario_id'] = 'mock-admin-id'
            sess['rol'] = 'admin'

        form_data = {
            'cdp_id': '1',
            'fecha': '2026-09-12',
            'hr_inicio': '19:00',
            'hr_fin': '20:30',
            'tema': 'Tema editado por admin',
            'nro_regulares': '12',
            'nro_ninos': '4',
            'nro_visitas': '2',
            'nro_comprometidos': '1',
            'reconciliaciones': '1',
            'confesiones': '2',
            'ofrendas_usd': '50.00',
            'ofrendas_bs': '500.00',
            'cesta_amor': '1',
            'observaciones': 'Editado por admin'
        }
        response = self.client.post('/admin/reporte/rep-999/editar', data=form_data)
        self.assertEqual(response.status_code, 302)
        mock_update.assert_called_once()


if __name__ == '__main__':
    unittest.main()

