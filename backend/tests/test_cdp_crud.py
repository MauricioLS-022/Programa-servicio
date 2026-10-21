"""
Tests unitarios y de integración para el CRUD de Casas de Paz (CDP):
1. crear_cdp_servicio: validaciones, duplicados y persistencia transaccional.
2. actualizar_cdp_servicio: validaciones, unicidad de código/usuario y actualización de credenciales.
3. eliminar_cdp_servicio y db_queries.eliminar_pausar_cdp:
   - Bloqueo por líderes asignados.
   - Pausa (soft-delete) por reportes históricos existentes.
   - Eliminación física completa si no tiene dependencias.
4. Rutas administrativas (/admin/casa_de_paz/...):
   - GET / POST crear
   - GET / POST editar
   - POST eliminar
"""
import unittest
from unittest.mock import patch, MagicMock
from app import app
import db_queries
from services.cdp_service import (
    crear_cdp_servicio,
    actualizar_cdp_servicio,
    eliminar_cdp_servicio,
)


class TestCdpCrudService(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    # -------------------------------------------------------------
    # Tests de crear_cdp_servicio
    # -------------------------------------------------------------
    def test_crear_cdp_validaciones_basicas(self):
        """Valida que los campos obligatorios y formatos se verifiquen defensivamente."""
        # Código inválido
        ok, msg = crear_cdp_servicio({'codigo': 'A'})
        self.assertFalse(ok)
        self.assertIn('código', msg.lower())

        # Dirección corta
        ok, msg = crear_cdp_servicio({'codigo': 'SUR-10', 'direccion': 'Av'})
        self.assertFalse(ok)
        self.assertIn('dirección', msg.lower())

        # Anfitrión inválido
        ok, msg = crear_cdp_servicio({
            'codigo': 'SUR-10',
            'direccion': 'Calle Principal 123',
            'anfitrion': '123'
        })
        self.assertFalse(ok)

        # Teléfono inválido
        ok, msg = crear_cdp_servicio({
            'codigo': 'SUR-10',
            'direccion': 'Calle Principal 123',
            'anfitrion': 'Familia Pérez',
            'telefono': 'invalido'
        })
        self.assertFalse(ok)

        # Red inválida
        ok, msg = crear_cdp_servicio({
            'codigo': 'SUR-10',
            'direccion': 'Calle Principal 123',
            'anfitrion': 'Familia Pérez',
            'telefono': '+58 412 1112233',
            'red_id': 'no-un-numero'
        })
        self.assertFalse(ok)
        self.assertIn('red', msg.lower())

    @patch('services.cdp_service.get_db_connection')
    def test_crear_cdp_duplicados_codigo(self, mock_get_conn):
        """Verifica que rechace códigos de CDP duplicados."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        # Cursor retorna un registro existente al buscar código
        mock_cursor.fetchone.return_value = {'id': 1}

        form_data = {
            'codigo': 'SUR-001',
            'anfitrion': 'Familia Gómez',
            'telefono': '+58 412 9998877',
            'direccion': 'Urbanización Los Cedros',
            'red_id': '1',
            'nombre': 'Carlos',
            'apellido': 'Gómez',
            'username': 'carlos_cdp',
            'password': 'Password123'
        }

        with self.app.app_context():
            ok, msg = crear_cdp_servicio(form_data)
            self.assertFalse(ok)
            self.assertIn("Ya existe una Casa de Paz con el código", msg)

    @patch('services.cdp_service.invalidate_dashboard_cache')
    @patch('services.cdp_service.db_queries.insertar_cdp')
    @patch('services.cdp_service.get_db_connection')
    def test_crear_cdp_exitoso(self, mock_get_conn, mock_insertar_cdp, mock_invalidate):
        """Verifica la creación exitosa pasando res_anfitrion correctamente a db_queries.insertar_cdp."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        # fetchone retorna None para código único y username único
        mock_cursor.fetchone.return_value = None

        form_data = {
            'codigo': 'SUR-001',
            'anfitrion': 'Familia Gómez',
            'telefono': '+58 412 9998877',
            'direccion': 'Urbanización Los Cedros',
            'red_id': '1',
            'nombre': 'Carlos',
            'apellido': 'Gómez',
            'username': 'carlos_cdp',
            'password': 'Password123'
        }

        with self.app.app_context():
            ok, msg = crear_cdp_servicio(form_data)
            self.assertTrue(ok)
            self.assertIn("creados exitosamente", msg)

            # Verificar que insertar_cdp recibió el anfitrión, no el apellido
            mock_insertar_cdp.assert_called_once()
            args = mock_insertar_cdp.call_args[0]
            # args: (cursor, codigo, anfitrion, direccion, telefono, red_id, nuevo_user_id)
            self.assertEqual(args[1], 'SUR-001')
            self.assertEqual(args[2], 'Familia Gómez')
            self.assertEqual(args[3], 'Urbanización Los Cedros')
            mock_conn.commit.assert_called_once()
            mock_invalidate.assert_called_once()

    @patch('services.cdp_service.invalidate_dashboard_cache')
    @patch('services.cdp_service.db_queries.insertar_cdp')
    @patch('services.cdp_service.get_db_connection')
    def test_crear_cdp_con_lider_existente_exitoso(self, mock_get_conn, mock_insertar_cdp, mock_invalidate):
        """Verifica la asignación exitosa de un líder_cdp ya existente al crear la Casa de Paz."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        # 1er fetchone: código CDP no duplicado (None)
        # 2do fetchone: datos del usuario existente válido
        # 3er fetchone: usuario no asignado a otra CDP (None)
        mock_cursor.fetchone.side_effect = [
            None,
            {'id': 'uuid-1234', 'username': 'lider_existente', 'tipo_usuario': 'lider_cdp', 'is_active': 1},
            None
        ]

        form_data = {
            'codigo': 'SUR-002',
            'anfitrion': 'Familia Martínez',
            'telefono': '+58 412 1112233',
            'direccion': 'Calle Las Flores 123',
            'red_id': '1',
            'modo_usuario': 'existente',
            'usuario_existente_id': 'uuid-1234'
        }

        with self.app.app_context():
            ok, msg = crear_cdp_servicio(form_data)
            self.assertTrue(ok)
            self.assertIn("asignada exitosamente al líder '@lider_existente'", msg)

            mock_insertar_cdp.assert_called_once()
            args = mock_insertar_cdp.call_args[0]
            # args: (cursor, codigo, anfitrion, direccion, telefono, red_id, usuario_existente_id)
            self.assertEqual(args[1], 'SUR-002')
            self.assertEqual(args[6], 'uuid-1234')
            mock_conn.commit.assert_called_once()
            mock_invalidate.assert_called_once()

    def test_crear_cdp_con_lider_existente_sin_id(self):
        """Rechaza la creación si se eligió modo existente pero no se seleccionó ningún usuario."""
        form_data = {
            'codigo': 'SUR-002',
            'anfitrion': 'Familia Martínez',
            'telefono': '+58 412 1112233',
            'direccion': 'Calle Las Flores 123',
            'red_id': '1',
            'modo_usuario': 'existente',
            'usuario_existente_id': ''
        }
        with self.app.app_context():
            ok, msg = crear_cdp_servicio(form_data)
            self.assertFalse(ok)
            self.assertIn("Debe seleccionar un usuario líder", msg)

    @patch('services.cdp_service.get_db_connection')
    def test_crear_cdp_con_lider_existente_ya_ocupado(self, mock_get_conn):
        """Rechaza la creación si el usuario ya está asignado a otra Casa de Paz."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        # 1er fetchone: código CDP no duplicado (None)
        # 2do fetchone: usuario existe
        # 3er fetchone: usuario YA está en otra CDP
        mock_cursor.fetchone.side_effect = [
            None,
            {'id': 'uuid-1234', 'username': 'lider_ocupado', 'tipo_usuario': 'lider_cdp', 'is_active': 1},
            {'id': 2, 'codigo': 'NORTE-001'}
        ]

        form_data = {
            'codigo': 'SUR-003',
            'anfitrion': 'Familia Martínez',
            'telefono': '+58 412 1112233',
            'direccion': 'Calle Las Flores 123',
            'red_id': '1',
            'modo_usuario': 'existente',
            'usuario_existente_id': 'uuid-1234'
        }

        with self.app.app_context():
            ok, msg = crear_cdp_servicio(form_data)
            self.assertFalse(ok)
            self.assertIn("ya está asignado a la Casa de Paz 'NORTE-001'", msg)

    # -------------------------------------------------------------
    # Tests de actualizar_cdp_servicio
    # -------------------------------------------------------------
    def test_actualizar_cdp_id_invalido(self):
        """Rechaza identificadores no numéricos."""
        ok, msg = actualizar_cdp_servicio('abc', {})
        self.assertFalse(ok)
        self.assertIn('identificador', msg.lower())

    @patch('services.cdp_service.invalidate_dashboard_cache')
    @patch('services.cdp_service.db_queries.actualizar_cdp_admin')
    @patch('services.cdp_service.get_db_connection')
    def test_actualizar_cdp_exitoso_con_usuario(self, mock_get_conn, mock_actualizar_admin, mock_invalidate):
        """Actualiza Casa de Paz y datos de usuario correctamente."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        # 1er fetchone: cdp existe con usuario_id
        # 2do fetchone: no hay duplicado de código
        # 3er fetchone: no hay duplicado de username
        mock_cursor.fetchone.side_effect = [
            {'id': 5, 'usuario_id': 'user-uuid-123'},
            None,
            None
        ]

        form_data = {
            'codigo': 'SUR-002',
            'anfitrion': 'Hnos Rodríguez',
            'telefono': '+58 414 1234567',
            'direccion': 'Sector Sur Calle 4',
            'red_id': '2',
            'nombre': 'Pedro',
            'apellido': 'Rodríguez',
            'username': 'pedro_cdp',
            'password': ''  # Sin cambiar contraseña
        }

        with self.app.app_context():
            ok, msg = actualizar_cdp_servicio(5, form_data)
            self.assertTrue(ok)
            self.assertIn("actualizada exitosamente", msg)
            mock_actualizar_admin.assert_called_once_with(
                mock_cursor, 5, 'SUR-002', 'Hnos Rodríguez', '+58 414 1234567', 'Sector Sur Calle 4', 2
            )
            mock_conn.commit.assert_called_once()

    # -------------------------------------------------------------
    # Tests de eliminar_pausar_cdp / eliminar_cdp_servicio
    # -------------------------------------------------------------
    def test_eliminar_cdp_bloqueada_por_lideres(self):
        """Bloquea la baja si la Casa de Paz tiene líderes asignados."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [
            {'usuario_id': 'uid-1', 'codigo': 'CDP-01'},  # CDP info
            {'total': 2}  # Total de líderes asignados
        ]

        exito, accion, mensaje = db_queries.eliminar_pausar_cdp(mock_cursor, 1)
        self.assertFalse(exito)
        self.assertEqual(accion, 'bloqueada')
        self.assertIn('líder(es) asignado(s)', mensaje)

    def test_eliminar_cdp_pausada_por_reportes_historicos(self):
        """Pone en pausa (is_active = 0) si tiene historial de reportes."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [
            {'usuario_id': 'uid-1', 'codigo': 'CDP-01'},  # CDP info
            {'total': 0},  # Líderes asignados = 0
            {'total': 12}  # Reportes históricos = 12
        ]

        exito, accion, mensaje = db_queries.eliminar_pausar_cdp(mock_cursor, 1)
        self.assertTrue(exito)
        self.assertEqual(accion, 'pausada')
        self.assertIn('pausada y su acceso desactivado', mensaje)

    def test_eliminar_cdp_eliminacion_limpia(self):
        """Elimina físicamente si no tiene reportes ni líderes asignados."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [
            {'usuario_id': 'uid-1', 'codigo': 'CDP-01'},  # CDP info
            {'total': 0},  # Líderes asignados = 0
            {'total': 0}   # Reportes históricos = 0
        ]

        exito, accion, mensaje = db_queries.eliminar_pausar_cdp(mock_cursor, 1)
        self.assertTrue(exito)
        self.assertEqual(accion, 'eliminada')
        self.assertIn('eliminadas permanentemente', mensaje)


class TestCdpAdminRoutes(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def _login_admin(self):
        with self.client.session_transaction() as sess:
            sess['usuario'] = 'admin'
            sess['rol'] = 'admin'
            sess['usuario_id'] = 'admin-id'

    @patch('routes.admin_routes.get_todas_las_redes', return_value=[{'id': 1, 'nombre': 'Red Central'}])
    @patch('routes.admin_routes.get_db_connection')
    def test_get_crear_cdp(self, mock_conn, mock_redes):
        """Ruta GET para crear CDP debe responder 200 y renderizar el formulario."""
        self._login_admin()
        mock_conn.return_value = MagicMock()
        resp = self.client.get('/admin/casa_de_paz/crear')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Datos del Centro', resp.data)

    @patch('routes.admin_routes.crear_cdp_servicio', return_value=(True, "Casa de Paz creada exitosamente."))
    def test_post_crear_cdp_redirects(self, mock_crear):
        """Ruta POST para crear CDP debe redirigir a /admin/estructura en caso de éxito."""
        self._login_admin()
        resp = self.client.post('/admin/casa_de_paz/crear', data={
            'codigo': 'SUR-001',
            'anfitrion': 'Familia Pérez',
            'telefono': '+58 412 1234567',
            'direccion': 'Calle Los Olivos',
            'red_id': '1',
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'username': 'juan_cdp',
            'password': 'Password123'
        }, follow_redirects=False)

        self.assertEqual(resp.status_code, 302)
        self.assertIn('/admin/estructura', resp.headers['Location'])

    @patch('routes.admin_routes.obtener_cdp_admin')
    @patch('routes.admin_routes.get_todas_las_redes', return_value=[{'id': 1, 'nombre': 'Red Central'}])
    @patch('routes.admin_routes.get_db_connection')
    def test_get_editar_cdp(self, mock_conn, mock_redes, mock_obtener_cdp):
        """Ruta GET para editar CDP debe responder 200 con los datos de la Casa."""
        self._login_admin()
        mock_conn.return_value = MagicMock()
        mock_obtener_cdp.return_value = {
            'id': 1,
            'codigo': 'SUR-001',
            'anfitrion': 'Familia Pérez',
            'telefono': '+58 412 1234567',
            'direccion': 'Calle Los Olivos',
            'red_id': 1,
            'username': 'juan_cdp',
            'usuario_nombre': 'Juan',
            'usuario_apellido': 'Pérez'
        }

        resp = self.client.get('/admin/casa_de_paz/1/editar')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'SUR-001', resp.data)
        self.assertIn(b'juan_cdp', resp.data)
        # Verificar que el breadcrumb enlaza a los detalles de esa Casa de Paz específica
        self.assertIn(b'/admin/casa_de_paz/1', resp.data)

    @patch('routes.admin_routes.actualizar_cdp_servicio', return_value=(True, "Actualizado"))
    @patch('routes.admin_routes.obtener_cdp_admin', return_value={'id': 1, 'codigo': 'SUR-001'})
    @patch('routes.admin_routes.get_todas_las_redes', return_value=[])
    @patch('routes.admin_routes.get_db_connection')
    def test_post_editar_cdp_redirects(self, mock_conn, mock_redes, mock_obtener, mock_actualizar):
        """Ruta POST para editar CDP debe redirigir a /admin/estructura en caso de éxito."""
        self._login_admin()
        mock_conn.return_value = MagicMock()
        resp = self.client.post('/admin/casa_de_paz/1/editar', data={
            'codigo': 'SUR-001',
            'anfitrion': 'Familia Gómez',
            'telefono': '+58 412 1234567',
            'direccion': 'Calle Actualizada 456',
            'red_id': '1',
            'nombre': 'Juan',
            'apellido': 'Gómez',
            'username': 'juan_cdp',
            'password': ''
        }, follow_redirects=False)

        self.assertEqual(resp.status_code, 302)
        self.assertIn('/admin/estructura', resp.headers['Location'])

    @patch('routes.admin_routes.eliminar_cdp_servicio', return_value=(True, 'success', "Eliminada"))
    def test_post_eliminar_cdp(self, mock_eliminar):
        """Ruta POST para eliminar CDP debe redirigir a /admin/estructura."""
        self._login_admin()
        resp = self.client.post('/admin/casa_de_paz/1/eliminar', follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/admin/estructura', resp.headers['Location'])

    def test_detalle_cdp_datos_reales_y_usuario(self):
        """Verifica que la vista de detalle de CDP renderice el usuario del sistema, estado y teléfono propio."""
        self._login_admin()
        resp = self.client.get('/admin/casa_de_paz/1')
        self.assertEqual(resp.status_code, 200)
        # Debe mostrar el usuario asignado
        self.assertIn(b'Usuario del Sistema', resp.data)
        self.assertIn(b'@', resp.data)
        # Debe mostrar el teléfono de la casa
        self.assertIn(b'Tel\xc3\xa9fono de la Casa', resp.data)
        # Debe reflejar el estado Activa
        self.assertIn(b'Activa', resp.data)
        # Debe mostrar el badge de reporte semanal
        self.assertIn(b'Reporte Semanal (7', resp.data)

    def test_check_cdp_reporte_7d_demo_fallback(self):
        """Verifica que check_cdp_reporte_7d funcione correctamente con el fallback demo."""
        from services.cdp_service import check_cdp_reporte_7d
        res = check_cdp_reporte_7d(1)
        self.assertIn('tiene_reporte', res)
        self.assertIn('estado', res)
        self.assertIn('is_active', res)

    @patch('services.dashboard_service.mock_mode_enabled', return_value=True)
    def test_estructura_admin_renderiza_cumplimiento_y_banner(self, mock_mode):
        """Verifica que la vista /admin/estructura renderice las pastillas y el banner de cumplimiento."""
        self._login_admin()
        resp = self.client.get('/admin/estructura')
        self.assertEqual(resp.status_code, 200)
        # Debe renderizar el contenedor de cuadrícula
        self.assertIn(b'casas-grid', resp.data)
        # Debe incluir los atributos data-reporte-reciente y data-is-active
        self.assertIn(b'data-reporte-reciente', resp.data)
        self.assertIn(b'data-is-active', resp.data)


if __name__ == '__main__':
    unittest.main()
