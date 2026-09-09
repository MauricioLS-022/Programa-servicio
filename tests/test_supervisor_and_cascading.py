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


if __name__ == '__main__':
    unittest.main()
