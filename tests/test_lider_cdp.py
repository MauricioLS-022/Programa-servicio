"""
Tests unitarios y de integración para el módulo de Líder de Casa de Paz:
- Métricas y datos del dashboard (cdp_service)
- Generación, edición y eliminación de reportes
- Renderizado de interfaz, tablas y modales
- Control de acceso por roles y autenticación
"""
import unittest
from unittest.mock import patch, MagicMock
from app import app
from services.cdp_service import (
    get_lider_dashboard_data,
    actualizar_reporte,
    eliminar_reporte,
    process_reporte,
    get_cdp_datos_usuario
)


class TestLiderCDPService(unittest.TestCase):
    """Pruebas unitarias de las funciones del servicio CDP."""

    def test_get_lider_dashboard_data_structure(self):
        """Verifica que get_lider_dashboard_data retorne la estructura esperada."""
        with app.app_context():
            data = get_lider_dashboard_data('usuario-no-existente-123')
            self.assertIsInstance(data, dict)
            self.assertIn('cdp', data)
            self.assertIn('lideres', data)
            self.assertIn('metricas', data)
            self.assertIn('reportes', data)
            self.assertIn('tiene_cdp', data)

            metricas = data['metricas']
            self.assertIn('total_reportes', metricas)
            self.assertIn('asistencia_promedio', metricas)
            self.assertIn('ofrendas_totales', metricas)
            self.assertIn('reporte_esta_semana', metricas)
            self.assertIn('dias_cierre_texto', metricas)

    @patch('services.cdp_service.get_db_connection')
    def test_actualizar_reporte_sin_conexion(self, mock_db):
        """Si no hay conexión a la BD, actualizar_reporte debe retornar False con mensaje."""
        mock_db.return_value = None
        form_data = {
            'fecha': '2026-08-20',
            'hr_inicio': '18:00',
            'hr_fin': '19:30',
            'tema': 'Tema Test',
            'nro_regulares': '10',
            'nro_ninos': '2',
            'nro_visitas': '1',
            'nro_comprometidos': '0',
            'ofrendas': '150.00'
        }
        with app.app_context():
            exito, mensaje = actualizar_reporte('rep-1', 1, form_data)
            self.assertFalse(exito)
            self.assertIn('conectar', mensaje.lower())

    @patch('services.cdp_service.get_db_connection')
    def test_eliminar_reporte_sin_conexion(self, mock_db):
        """Si no hay conexión a la BD, eliminar_reporte debe retornar False con mensaje."""
        mock_db.return_value = None
        with app.app_context():
            exito, mensaje = eliminar_reporte('rep-1', 1)
            self.assertFalse(exito)
            self.assertIn('conectar', mensaje.lower())

    @patch('services.cdp_service.get_db_connection')
    @patch('services.cdp_service.db_queries.actualizar_reporte_cdp')
    def test_actualizar_reporte_exito(self, mock_update, mock_db):
        """Verifica que una actualización exitosa llame al commit y retorne True."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db.return_value = mock_conn
        mock_update.return_value = True

        form_data = {
            'fecha': '2026-08-20',
            'hr_inicio': '18:00',
            'hr_fin': '19:30',
            'tema': 'El Poder de la Oración',
            'nro_regulares': '15',
            'nro_ninos': '4',
            'nro_visitas': '2',
            'nro_comprometidos': '1',
            'ofrendas': '250.00'
        }
        with app.app_context():
            exito, mensaje = actualizar_reporte('rep-1', 1, form_data)
            self.assertTrue(exito)
            self.assertIn('exitosamente', mensaje.lower())
            mock_conn.commit.assert_called_once()

    @patch('services.cdp_service.get_db_connection')
    @patch('services.cdp_service.db_queries.insertar_reporte')
    def test_process_reporte_exito(self, mock_insert, mock_db):
        """Verifica que process_reporte inserte correctamente y confirme transacción."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db.return_value = mock_conn

        form_data = {
            'fecha': '2026-08-22',
            'hr_inicio': '18:30',
            'hr_fin': '20:00',
            'tema': 'Comunión y Servicio',
            'nro_regulares': '12',
            'nro_ninos': '3',
            'nro_visitas': '2',
            'nro_comprometidos': '1',
            'ofrendas_bs': '450.00',
            'ofrendas_usd': '25.00',
            'cesta_amor': '1'
        }
        with app.app_context():
            exito = process_reporte(1, form_data)
            self.assertTrue(exito)
            mock_conn.commit.assert_called_once()
            args, _ = mock_insert.call_args
            datos = args[1]
            self.assertEqual(datos['ofrendas_bs'], 450.00)
            self.assertEqual(datos['ofrendas_usd'], 25.00)
            self.assertEqual(datos['cesta_amor'], 1)


class TestLiderCDPRoutes(unittest.TestCase):
    """Pruebas de integración de las rutas /lider_cdp."""

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key-123'
        self.client = app.test_client()

    def test_dashboard_requiere_login(self):
        """El acceso sin sesión debe redirigir al login (/iniciar_sesion)."""
        response = self.client.get('/lider_cdp/dashboard')
        self.assertEqual(response.status_code, 302)
        location = response.headers.get('Location', '')
        self.assertTrue('/iniciar_sesion' in location or '/login' in location)

    def test_dashboard_acceso_lider_cdp(self):
        """Un usuario con rol lider_cdp debe poder ver el dashboard y sus componentes."""
        with self.client.session_transaction() as sess:
            sess['usuario'] = 'LiderTest'
            sess['usuario_id'] = 'mock-lider-id'
            sess['rol'] = 'lider_cdp'

        response = self.client.get('/lider_cdp/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Panel de Casa de Paz', response.data)
        self.assertIn(b'LiderTest', response.data)
        self.assertIn(b'modalDetalleReporte', response.data)
        self.assertIn(b'modalEditarReporte', response.data)
        self.assertIn(b'modalEliminarReporte', response.data)

    def test_dashboard_rol_no_autorizado(self):
        """Un rol supervisor no debe tener acceso al panel exclusivo de lider_cdp."""
        with self.client.session_transaction() as sess:
            sess['usuario'] = 'SupervisorTest'
            sess['usuario_id'] = 'mock-sup-id'
            sess['rol'] = 'supervisor'

        response = self.client.get('/lider_cdp/dashboard')
        self.assertIn(response.status_code, [403, 302])

    @patch('routes.lider_cdp_routes.get_lider_dashboard_data')
    def test_dashboard_render_with_reports(self, mock_dash):
        """Verifica que los reportes y botones de acción se rendericen en la tabla."""
        mock_dash.return_value = {
            'cdp': {'id': 1, 'codigo': 'BET-001', 'anfitrion': 'Familia Pérez'},
            'lideres': [{'id': 1, 'nombre': 'Juan', 'apellido': 'Pérez', 'rol': 'Lider'}],
            'metricas': {
                'total_reportes': 1,
                'asistencia_promedio': 25,
                'ofrendas_totales': 500.0,
                'reporte_esta_semana': True,
                'dias_cierre_texto': 'Próximo cierre: 3 días'
            },
            'reportes': [{
                'id': 'rep-abc-123',
                'fecha': '2026-08-20',
                'fecha_formateada': '20 Ago 2026',
                'hr_inicio': '19:00',
                'hr_fin': '20:30',
                'lider_nombre': 'Juan Pérez',
                'iniciales': 'JP',
                'tema': 'El Poder de la Fe',
                'asistencia': 25,
                'nro_regulares': 15,
                'nro_niños': 5,
                'nro_visitas': 3,
                'nro_comprometidos': 2,
                'reconciliaciones': 1,
                'confesiones': 1,
                'ofrendas': 500.0,
                'cesta_amor': 0,
                'observaciones': 'Gran reunión'
            }],
            'tiene_cdp': True,
            'page': 1,
            'pages': 1,
            'total_reportes': 1,
        }

        with self.client.session_transaction() as sess:
            sess['usuario'] = 'Juan'
            sess['usuario_id'] = 'lider-1'
            sess['rol'] = 'lider_cdp'

        response = self.client.get('/lider_cdp/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'BET-001', response.data)
        self.assertIn(b'El Poder de la Fe', response.data)
        self.assertIn(b'btn-action-view', response.data)
        self.assertIn(b'btn-action-edit', response.data)
        self.assertIn(b'btn-action-delete', response.data)

    @patch('routes.lider_cdp_routes.get_cdp_datos_usuario')
    @patch('routes.lider_cdp_routes.actualizar_reporte')
    def test_editar_reporte_route_post(self, mock_update, mock_cdp):
        """La ruta POST de editar reporte debe llamar al servicio y redirigir con flash."""
        mock_cdp.return_value = ({'id': 1, 'codigo': 'BET-001'}, [])
        mock_update.return_value = (True, 'Reporte actualizado exitosamente.')

        with self.client.session_transaction() as sess:
            sess['usuario'] = 'LiderTest'
            sess['usuario_id'] = 'mock-lider-id'
            sess['rol'] = 'lider_cdp'

        form_data = {
            'fecha': '2026-08-20',
            'hr_inicio': '19:00',
            'hr_fin': '20:30',
            'tema': 'Tema Actualizado',
            'nro_regulares': '20',
            'nro_ninos': '5',
            'nro_visitas': '3',
            'nro_comprometidos': '1',
            'reconciliaciones': '0',
            'confesiones': '1',
            'ofrendas': '300.00',
            'cesta_amor': '0',
            'observaciones': 'Todo excelente'
        }

        response = self.client.post('/lider_cdp/reporte/rep-123/editar', data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/lider_cdp/dashboard', response.headers.get('Location', ''))

    @patch('routes.lider_cdp_routes.get_cdp_datos_usuario')
    def test_editar_reporte_sin_cdp(self, mock_cdp):
        """Si el usuario no tiene CDP asignada, no debe permitir editar y debe redirigir."""
        mock_cdp.return_value = (None, [])

        with self.client.session_transaction() as sess:
            sess['usuario'] = 'LiderSinCDP'
            sess['usuario_id'] = 'sin-cdp-id'
            sess['rol'] = 'lider_cdp'

        response = self.client.post('/lider_cdp/reporte/rep-123/editar', data={'tema': 'Test'})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/lider_cdp/dashboard', response.headers.get('Location', ''))

    @patch('routes.lider_cdp_routes.get_cdp_datos_usuario')
    @patch('routes.lider_cdp_routes.eliminar_reporte')
    def test_eliminar_reporte_route_post(self, mock_delete, mock_cdp):
        """La ruta POST de eliminar reporte debe llamar al servicio y redirigir."""
        mock_cdp.return_value = ({'id': 1, 'codigo': 'BET-001'}, [])
        mock_delete.return_value = (True, 'Reporte eliminado exitosamente.')

        with self.client.session_transaction() as sess:
            sess['usuario'] = 'LiderTest'
            sess['usuario_id'] = 'mock-lider-id'
            sess['rol'] = 'lider_cdp'

        response = self.client.post('/lider_cdp/reporte/rep-123/eliminar')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/lider_cdp/dashboard', response.headers.get('Location', ''))

    @patch('routes.lider_cdp_routes.get_cdp_datos_usuario')
    def test_eliminar_reporte_sin_cdp(self, mock_cdp):
        """Si el usuario no tiene CDP asignada, no debe permitir eliminar y debe redirigir."""
        mock_cdp.return_value = (None, [])

        with self.client.session_transaction() as sess:
            sess['usuario'] = 'LiderSinCDP'
            sess['usuario_id'] = 'sin-cdp-id'
            sess['rol'] = 'lider_cdp'

        response = self.client.post('/lider_cdp/reporte/rep-123/eliminar')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/lider_cdp/dashboard', response.headers.get('Location', ''))

    @patch('routes.lider_cdp_routes.get_cdp_datos_usuario')
    def test_generar_reporte_get(self, mock_cdp):
        """Ruta GET generar_reporte debe renderizar la plantilla cuando hay CDP asignada."""
        mock_cdp.return_value = ({'id': 1, 'codigo': 'BET-001'}, [{'id': 1, 'nombre': 'Juan', 'apellido': 'Pérez'}])

        with self.client.session_transaction() as sess:
            sess['usuario'] = 'LiderTest'
            sess['usuario_id'] = 'mock-lider-id'
            sess['rol'] = 'lider_cdp'

        response = self.client.get('/lider_cdp/generar_reporte')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Generar Reporte', response.data)

    def test_admin_casa_de_paz_detalles(self):
        """Ruta GET /admin/casa_de_paz/<id> debe renderizar detalles de la Casa de Paz."""
        with self.client.session_transaction() as sess:
            sess['usuario'] = 'AdminTest'
            sess['usuario_id'] = 'admin-id'
            sess['rol'] = 'admin'

        response = self.client.get('/admin/casa_de_paz/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Detalle de Casa de Paz', response.data)

    def test_supervisor_casa_de_paz_detalles(self):
        """Ruta GET /supervisor/casa_de_paz/<id> debe renderizar detalles de la Casa de Paz para supervisor."""
        with self.client.session_transaction() as sess:
            sess['usuario'] = 'SupervisorTest'
            sess['usuario_id'] = 'sup-id'
            sess['rol'] = 'supervisor'

        response = self.client.get('/supervisor/casa_de_paz/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Detalle de Casa de Paz', response.data)


if __name__ == '__main__':
    unittest.main()
