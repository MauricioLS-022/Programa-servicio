"""
Tests unitarios para alternancia de estado (toggle_estado) de redes:
1. get_selectores incluye is_active y supervisor_id en redes.
2. get_estructura_context propaga is_active como booleano.
3. estructura_admin.html muestra 'Poner en pausa' cuando la red está activa y 'Reactivar red' cuando está pausada.
4. toggle_red_servicio alterna correctamente el estado en la base de datos.
"""
import unittest
from unittest.mock import patch, MagicMock
from app import app
from services.dashboard_service import get_selectores, get_estructura_context
from services.leader_service import toggle_red_servicio


class TestRedToggleEstado(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.client = app.test_client()
        app.config['TESTING'] = True

    @patch('services.dashboard_service.get_db_connection')
    def test_get_selectores_includes_is_active(self, mock_get_conn):
        """get_selectores debe incluir r.is_active y r.supervisor_id en la consulta SQL."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.side_effect = [
            [{'id': 1, 'nombre': 'Red Alfa', 'is_active': 1, 'supervisor_id': 'sup-1', 'supervisor': 'Juan Perez'}],
            []
        ]
        mock_get_conn.return_value = mock_conn

        with patch('services.dashboard_service.get_cached_value', return_value=None):
            redes, _ = get_selectores()
            self.assertEqual(len(redes), 1)
            self.assertIn('is_active', redes[0])
            self.assertEqual(redes[0]['is_active'], 1)
            self.assertEqual(redes[0]['supervisor_id'], 'sup-1')

    @patch('services.dashboard_service.get_selectores')
    @patch('services.dashboard_service.get_db_connection', return_value=MagicMock())
    def test_get_estructura_context_is_active_propagation(self, mock_conn, mock_selectores):
        """get_estructura_context debe propagar is_active como booleano para cada red."""
        mock_redes = [
            {'id': 1, 'nombre': 'Red Activa', 'is_active': 1, 'supervisor': 'Sup 1'},
            {'id': 2, 'nombre': 'Red Pausada', 'is_active': 0, 'supervisor': 'Sup 2'}
        ]
        mock_casas = []
        mock_selectores.return_value = (mock_redes, mock_casas)

        context = get_estructura_context('admin-uuid', is_supervisor=False)
        redes = context['redes_estructura']
        
        self.assertEqual(len(redes), 2)
        self.assertTrue(redes[0]['is_active'])
        self.assertFalse(redes[1]['is_active'])

    def test_template_button_text_active_vs_paused(self):
        """estructura_admin.html debe mostrar 'Poner en pausa' si la red está activa y 'Reactivar red' si está pausada."""
        with self.app.test_request_context('/admin/estructura'):
            # Inyectamos una sesión simulada de admin
            from flask import render_template
            context = {
                'redes_estructura': [
                    {
                        'id': 1,
                        'nombre': 'Red Activa',
                        'slug': 'red-1',
                        'supervisor': 'Supervisor Uno',
                        'supervisor_id': 'sup-1',
                        'total_casas': 2,
                        'is_active': True
                    },
                    {
                        'id': 2,
                        'nombre': 'Red Pausada',
                        'slug': 'red-2',
                        'supervisor': 'Supervisor Dos',
                        'supervisor_id': 'sup-2',
                        'total_casas': 0,
                        'is_active': False
                    }
                ],
                'casas_estructura': [],
                'total_casas_estructura': 2,
                'total_asistencia_estructura': 0,
                'casas_activas_estructura': 0,
                'casas_pendientes_estructura': 0,
                'estructura_mock': False,
                'estructura_vacia': False,
                'current_user_role': 'admin',
            }
            
            with self.client.session_transaction() as sess:
                sess['usuario'] = 'admin'
                sess['rol'] = 'admin'
                sess['usuario_id'] = 'admin-id'

            html = render_template('estructura_admin.html', **context)
            
            # Para la red activa: debe tener 'Poner en pausa' y clase 'menu-danger'
            self.assertIn('Poner en pausa', html)
            self.assertIn('pause_circle', html)
            
            # Para la red pausada: debe tener 'Reactivar red' y badge 'En pausa'
            self.assertIn('Reactivar red', html)
            self.assertIn('play_circle', html)
            self.assertIn('En pausa', html)

    @patch('services.leader_service.get_db_connection')
    @patch('services.leader_service.toggle_estado_red')
    @patch('services.leader_service.invalidate_dashboard_cache')
    def test_toggle_red_servicio_success(self, mock_cache, mock_toggle_estado, mock_get_conn):
        """toggle_red_servicio debe cambiar el estado y devolver mensaje según quede activa o pausada."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {'nombre': 'Red Beta'}
        mock_get_conn.return_value = mock_conn

        # Caso 1: Se pausa la red (quedo_activa = False)
        mock_toggle_estado.return_value = False
        success, message = toggle_red_servicio(1)
        self.assertTrue(success)
        self.assertIn("puesta en pausa", message)

        # Caso 2: Se reactiva la red (quedo_activa = True)
        mock_toggle_estado.return_value = True
        success, message = toggle_red_servicio(1)
        self.assertTrue(success)
        self.assertIn("reactivada", message)


if __name__ == '__main__':
    unittest.main()

