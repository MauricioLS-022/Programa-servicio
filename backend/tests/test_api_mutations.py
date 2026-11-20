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
    @patch('routes.api.reportes_api._resolve_reporte_cdp_id', return_value=10)
    @patch('routes.api.reportes_api.actualizar_reporte')
    def test_api_reportes_put_uuid_supported(self, mock_act, _mock_resolve):
        """PUT /api/reportes/<uuid> no debe dar 404 por incompatibilidad de tipo y resuelve cdp_id real."""
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
        self.assertEqual(mock_act.call_args[0][1], 10)

    @patch('routes.api.reportes_api._resolve_reporte_cdp_id', return_value=10)
    @patch('routes.api.reportes_api.eliminar_reporte')
    def test_api_reportes_delete_uuid_supported(self, mock_elim, _mock_resolve):
        """DELETE /api/reportes/<uuid> debe recibir la cadena UUID correctamente y resolver cdp_id real."""
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
        self.assertEqual(mock_elim.call_args[0][1], 10)

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

    # -------------------------------------------------------------------------
    # 5. Mutaciones REST completas: Redes
    # -------------------------------------------------------------------------
    def _set_admin_session(self):
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'admin-uuid'
            sess['usuario'] = 'admin'
            sess['rol'] = 'admin'

    @patch('routes.api.estructura_api.crear_red_servicio')
    @patch('routes.api.estructura_api.actualizar_red_servicio')
    @patch('routes.api.estructura_api.toggle_red_servicio')
    @patch('routes.api.estructura_api.eliminar_red_servicio')
    @patch('routes.api.estructura_api.obtener_red_servicio')
    def test_api_redes_full_crud_mutations(self, mock_get, mock_del, mock_toggle, mock_upd, mock_create):
        self._set_admin_session()

        # GET 404 cuando no existe
        mock_get.return_value = None
        res_404 = self.client.get('/api/redes/999')
        self.assertEqual(res_404.status_code, 404)

        # POST inválido (nombre vacío -> Pydantic 400 con details)
        res_bad = self.client.post('/api/redes', json={'nombre': '   '})
        self.assertEqual(res_bad.status_code, 400)
        self.assertIn('details', res_bad.get_json())

        # POST válido -> 201
        mock_create.return_value = (True, 'Red creada exitosamente.')
        res_create = self.client.post('/api/redes', json={'nombre': 'Red Betel', 'supervisor_id': ''})
        self.assertEqual(res_create.status_code, 201)
        self.assertTrue(res_create.get_json()['success'])

        # PUT válido -> 200 y error de negocio -> 400
        mock_upd.return_value = (True, 'Red actualizada.')
        res_upd = self.client.put('/api/redes/1', json={'nombre': 'Red Betel Norte'})
        self.assertEqual(res_upd.status_code, 200)
        mock_upd.return_value = (False, 'Nombre duplicado.')
        res_upd_err = self.client.put('/api/redes/1', json={'nombre': 'Red Duplicada'})
        self.assertEqual(res_upd_err.status_code, 400)

        # POST toggle -> 200 y fallo -> 400
        mock_toggle.return_value = (True, 'Red pausada.')
        self.assertEqual(self.client.post('/api/redes/1/toggle').status_code, 200)
        mock_toggle.return_value = (False, 'Red no encontrada.')
        self.assertEqual(self.client.post('/api/redes/1/toggle').status_code, 400)

        # DELETE -> 200 y bloqueo -> 400
        mock_del.return_value = (True, 'Red eliminada.')
        self.assertEqual(self.client.delete('/api/redes/1').status_code, 200)
        mock_del.return_value = (False, 'Tiene Casas de Paz activas.')
        res_del_guard = self.client.delete('/api/redes/1')
        self.assertEqual(res_del_guard.status_code, 400)
        self.assertFalse(res_del_guard.get_json()['success'])

    # -------------------------------------------------------------------------
    # 6. Mutaciones REST completas: Casas de Paz
    # -------------------------------------------------------------------------
    @patch('routes.api.estructura_api.crear_cdp_servicio')
    @patch('routes.api.estructura_api.actualizar_cdp_servicio')
    @patch('routes.api.estructura_api.toggle_cdp_servicio')
    @patch('routes.api.estructura_api.eliminar_cdp_servicio')
    @patch('routes.api.estructura_api.get_cdp_detalle')
    def test_api_casas_de_paz_full_crud_mutations(self, mock_get, mock_del, mock_toggle, mock_upd, mock_create):
        self._set_admin_session()

        # GET 404
        mock_get.return_value = None
        self.assertEqual(self.client.get('/api/casas_de_paz/999').status_code, 404)

        # POST inválido (sin red_id) -> 400 Pydantic
        res_bad = self.client.post('/api/casas_de_paz', json={'codigo': 'CDP-1'})
        self.assertEqual(res_bad.status_code, 400)
        self.assertIn('details', res_bad.get_json())

        # POST válido -> 201
        mock_create.return_value = (True, 'Casa creada.')
        res_ok = self.client.post('/api/casas_de_paz', json={
            'codigo': 'HEB-05',
            'anfitrion': 'Familia Ruiz',
            'direccion': 'Av Principal 12',
            'red_id': '1',
        })
        self.assertEqual(res_ok.status_code, 201)
        self.assertTrue(res_ok.get_json()['success'])

        # PUT válido -> 200 y error -> 400
        mock_upd.return_value = (True, 'Casa actualizada.')
        self.assertEqual(self.client.put('/api/casas_de_paz/5', json={'anfitrion': 'Familia Nueva'}).status_code, 200)
        mock_upd.return_value = (False, 'Código ya existe.')
        self.assertEqual(self.client.put('/api/casas_de_paz/5', json={'codigo': 'DUP-1'}).status_code, 400)

        # POST toggle -> 200 y bloqueo jerárquico -> 400
        mock_toggle.return_value = (True, 'active', 'Casa reactivada.')
        res_tog = self.client.post('/api/casas_de_paz/5/toggle')
        self.assertEqual(res_tog.status_code, 200)
        self.assertEqual(res_tog.get_json()['status'], 'active')
        mock_toggle.return_value = (False, 'error', 'La red padre está pausada.')
        self.assertEqual(self.client.post('/api/casas_de_paz/5/toggle').status_code, 400)

        # DELETE -> 200 y bloqueo -> 400
        mock_del.return_value = (True, 'success', 'Casa eliminada.')
        self.assertEqual(self.client.delete('/api/casas_de_paz/5').status_code, 200)
        mock_del.return_value = (False, 'danger', 'Tiene líderes asignados.')
        self.assertEqual(self.client.delete('/api/casas_de_paz/5').status_code, 400)

    # -------------------------------------------------------------------------
    # 7. Mutaciones REST completas: Líderes
    # -------------------------------------------------------------------------
    @patch('routes.api.estructura_api.crear_lider_servicio')
    @patch('routes.api.estructura_api.actualizar_lider_servicio')
    @patch('routes.api.estructura_api.toggle_lider_servicio')
    @patch('routes.api.estructura_api.eliminar_lider_servicio')
    @patch('routes.api.estructura_api.obtener_lider_servicio')
    def test_api_lideres_full_crud_mutations(self, mock_get, mock_del, mock_toggle, mock_upd, mock_create):
        self._set_admin_session()

        # GET 404
        mock_get.return_value = None
        self.assertEqual(self.client.get('/api/lideres/999').status_code, 404)

        # POST inválido (cdp_id no numérico) -> 400
        res_bad = self.client.post('/api/lideres', json={'nombre': 'Ana', 'apellido': 'Gil', 'rol': 'Lider', 'cdp_id': 'abc'})
        self.assertEqual(res_bad.status_code, 400)
        self.assertIn('details', res_bad.get_json())

        # POST válido -> 201
        mock_create.return_value = (True, 'Líder registrado.')
        res_ok = self.client.post('/api/lideres', json={
            'nombre': 'Ana',
            'apellido': 'Gil',
            'rol': 'Lider',
            'telefono': '+584121234567',
            'cdp_id': 1,
        })
        self.assertEqual(res_ok.status_code, 201)

        # PUT válido -> 200 y error -> 400
        mock_upd.return_value = (True, 'Líder actualizado.')
        self.assertEqual(self.client.put('/api/lideres/3', json={'rol': 'Sublider'}).status_code, 200)
        mock_upd.return_value = (False, 'Casa inactiva.')
        self.assertEqual(self.client.put('/api/lideres/3', json={'cdp_id': 99}).status_code, 400)

        # POST toggle -> 200 y error -> 400
        mock_toggle.return_value = (True, 'paused', 'Líder pausado.')
        self.assertEqual(self.client.post('/api/lideres/3/toggle').status_code, 200)
        mock_toggle.return_value = (False, 'error', 'No se pudo reactivar.')
        self.assertEqual(self.client.post('/api/lideres/3/toggle').status_code, 400)

        # DELETE -> 200 y candado de historial -> 400
        mock_del.return_value = (True, 'success', 'Líder eliminado.')
        self.assertEqual(self.client.delete('/api/lideres/3').status_code, 200)
        mock_del.return_value = (False, 'danger', 'Tiene reportes históricos.')
        self.assertEqual(self.client.delete('/api/lideres/3').status_code, 400)

    # -------------------------------------------------------------------------
    # 8. Mutaciones REST completas: Usuarios
    # -------------------------------------------------------------------------
    @patch('routes.api.usuarios_api.obtener_usuario_por_id')
    @patch('routes.api.usuarios_api.crear_nuevo_usuario')
    @patch('routes.api.usuarios_api.actualizar_usuario_admin')
    @patch('routes.api.usuarios_api.toggle_usuario_servicio')
    @patch('routes.api.usuarios_api.get_opciones_asignacion')
    def test_api_usuarios_full_crud_mutations(self, mock_opts, mock_toggle, mock_upd, mock_create, mock_get):
        self._set_admin_session()

        # GET detalle 200 y 404
        mock_get.return_value = {'id': 'u-1', 'username': 'juan', 'tipo_usuario': 'supervisor'}
        self.assertEqual(self.client.get('/api/usuarios/u-1').status_code, 200)
        mock_get.return_value = None
        self.assertEqual(self.client.get('/api/usuarios/missing').status_code, 404)

        # POST inválido -> 400 con details
        res_bad = self.client.post('/api/usuarios', json={'username': 'solo_user'})
        self.assertEqual(res_bad.status_code, 400)
        self.assertIn('details', res_bad.get_json())

        # POST válido -> 201 y error de negocio -> 400
        mock_create.return_value = (True, 'Usuario creado.')
        res_ok = self.client.post('/api/usuarios', json={
            'nombre': 'Carlos',
            'apellido': 'Pérez',
            'username': 'cperez',
            'password': 'Password1',
            'rol': 'supervisor',
        })
        self.assertEqual(res_ok.status_code, 201)
        mock_create.return_value = (False, 'Nombre de usuario duplicado.')
        self.assertEqual(self.client.post('/api/usuarios', json={
            'nombre': 'Carlos',
            'apellido': 'Pérez',
            'username': 'cperez',
            'password': 'Password1',
            'rol': 'supervisor',
        }).status_code, 400)

        # PUT válido -> 200 y error -> 400
        mock_upd.return_value = (True, 'Usuario actualizado.')
        self.assertEqual(self.client.put('/api/usuarios/u-1', json={'nombre': 'Carlos Alberto'}).status_code, 200)
        mock_upd.return_value = (False, 'Error de validación.')
        self.assertEqual(self.client.put('/api/usuarios/u-1', json={'nombre': 'Carlos'}).status_code, 400)

        # POST toggle -> 200 y error -> 400
        mock_toggle.return_value = (True, 'paused', 'Usuario pausado.')
        self.assertEqual(self.client.post('/api/usuarios/u-1/toggle').status_code, 200)
        mock_toggle.return_value = (False, 'error', 'No se puede pausar el único admin.')
        self.assertEqual(self.client.post('/api/usuarios/u-1/toggle').status_code, 400)

        # GET opciones de asignación -> 200
        mock_opts.return_value = ([{'id': 1, 'nombre': 'Hebrón'}], [{'id': 10, 'codigo': 'HEB-01'}])
        res_opts = self.client.get('/api/usuarios/opciones_asignacion?usuario_id=u-1')
        self.assertEqual(res_opts.status_code, 200)
        opts_data = res_opts.get_json()
        self.assertEqual(len(opts_data['redes']), 1)
        self.assertEqual(len(opts_data['casas_de_paz']), 1)

    # -------------------------------------------------------------------------
    # 9. Payloads reales de modales React (int IDs, edición parcial, self-toggle, 503)
    # -------------------------------------------------------------------------
    def test_modal_payloads_with_int_ids_do_not_crash_services(self):
        """Los servicios CRUD aceptan IDs enteros provenientes de DTOs Pydantic/modales React."""
        from services.cdp_service import crear_cdp_servicio, actualizar_cdp_servicio
        from services.leader_service import crear_lider_servicio, actualizar_lider_servicio
        from services.user_service import actualizar_usuario_admin, toggle_usuario_servicio

        # 1. CasaDePazModal: crear con red_id=int y actualizar solo campos CDP (sin res_user crash)
        fake_conn = MagicMock()
        fake_cur = MagicMock()
        fake_conn.cursor.return_value.__enter__.return_value = fake_cur
        # crear_cdp_servicio: check codigo dup -> check usuario existente -> check cdp ocupada
        fake_cur.fetchone.side_effect = [
            None,
            {'id': 'u-existing-1', 'username': 'lider1', 'tipo_usuario': 'lider_cdp', 'is_active': 1},
            None,
        ]
        with patch('services.cdp_service.get_db_connection', return_value=fake_conn), \
             patch('services.cdp_service.invalidate_dashboard_cache'):
            ok_c, msg_c = crear_cdp_servicio({
                'codigo': 'CA-9.9',
                'anfitrion': 'Familia Prueba',
                'direccion': 'Calle 1',
                'red_id': 1,
                'usuario_existente_id': 'u-existing-1',
            })
            self.assertTrue(ok_c, msg_c)

        fake_conn2 = MagicMock()
        fake_cur2 = MagicMock()
        fake_cur2.rowcount = 1
        fake_conn2.cursor.return_value.__enter__.return_value = fake_cur2
        # actualizar_cdp_servicio sin campos de usuario: check cdp actual -> check codigo dup -> None
        fake_cur2.fetchone.side_effect = [{'id': 5, 'usuario_id': None, 'is_active': 1}, None]
        with app.app_context(), \
             patch('services.cdp_service.get_db_connection', return_value=fake_conn2), \
             patch('services.cdp_service.invalidate_dashboard_cache'):
            ok_u, msg_u = actualizar_cdp_servicio(5, {
                'codigo': 'CA-9.9',
                'anfitrion': 'Familia Editada',
                'direccion': 'Calle 2',
                'red_id': 1,
            })
            self.assertTrue(ok_u, msg_u)

        # 2. LiderFormModal: crear y actualizar con cdp_id=int
        fake_conn_l = MagicMock()
        fake_cur_l = MagicMock()
        fake_cur_l.rowcount = 1
        fake_conn_l.cursor.return_value.__enter__.return_value = fake_cur_l
        fake_cur_l.fetchone.side_effect = [
            {'id': 1, 'codigo': 'HEB-01', 'is_active': 1},
            None,
            {'id': 3, 'is_active': 1, 'cdp_id': 1},
            {'id': 1, 'codigo': 'HEB-01', 'is_active': 1},
            None,
        ]
        with app.app_context(), \
             patch('services.leader_service.get_db_connection', return_value=fake_conn_l), \
             patch('services.leader_service.invalidate_dashboard_cache'):
            ok_lc, msg_lc = crear_lider_servicio({
                'nombre': 'Juan',
                'apellido': 'Pérez',
                'rol': 'Lider',
                'telefono': '04121234567',
                'cdp_id': 1,
            })
            self.assertTrue(ok_lc, msg_lc)
            ok_lu, msg_lu = actualizar_lider_servicio(3, {
                'nombre': 'Juan',
                'apellido': 'Pérez',
                'rol': 'Sublider',
                'telefono': '04121234567',
                'cdp_id': 1,
            })
            self.assertTrue(ok_lu, msg_lu)

        # 3. UsuarioModal: actualizar con red_id=int y bloqueo anti-autodesactivación
        fake_conn_u = MagicMock()
        fake_cur_u = MagicMock()
        fake_cur_u.rowcount = 1
        fake_conn_u.cursor.return_value.__enter__.return_value = fake_cur_u
        fake_cur_u.fetchone.return_value = None  # check username dup -> libre
        with app.app_context(), \
             patch('services.user_service.get_db_connection', return_value=fake_conn_u), \
             patch('services.user_service.invalidate_dashboard_cache'):
            ok_uu, msg_uu = actualizar_usuario_admin('u-2', {
                'nombre': 'Pedro',
                'apellido': 'Gómez',
                'username': 'sup2',
                'tipo_usuario': 'supervisor',
                'red_id': 1,
                'cdp_id': None,
            })
            self.assertTrue(ok_uu, msg_uu)

        ok_self, status_self, msg_self = toggle_usuario_servicio('admin-self-id', usuario_session_id='admin-self-id')
        self.assertFalse(ok_self)
        self.assertEqual(status_self, 'error')
        self.assertIn('propia cuenta', msg_self)

    def test_api_returns_503_when_db_unavailable_and_mock_mode_false(self):
        """Con MOCK_MODE=False y BD caída, /api/redes, /api/casas_de_paz, /api/lideres y /api/reportes devuelven 503."""
        import database
        self._set_admin_session()
        orig_mock = app.config.get('MOCK_MODE', False)
        app.config['MOCK_MODE'] = False
        database.reset_circuit_breaker()
        try:
            with patch('database._create_raw_connection', side_effect=RuntimeError("DB down")):
                for ep in ('/api/redes', '/api/casas_de_paz', '/api/lideres', '/api/reportes', '/api/casas_de_paz/1'):
                    res = self.client.get(ep)
                    self.assertEqual(res.status_code, 503, f"Esperado 503 en {ep}, recibido {res.status_code}")
                    self.assertEqual(res.get_json().get('code'), 'db_unavailable')
        finally:
            database.reset_circuit_breaker()
            app.config['MOCK_MODE'] = orig_mock


if __name__ == '__main__':
    unittest.main()

