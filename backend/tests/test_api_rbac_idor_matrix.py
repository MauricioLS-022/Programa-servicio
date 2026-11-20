"""
tests/test_api_rbac_idor_matrix.py - Matriz parametrizada RBAC y Anti-IDOR en toda la API REST.
Verifica el aislamiento territorial y control de roles para:
- Anónimo (401)
- lider_cdp (acceso solo a su CDP, bloqueo 403 en estructura/usuarios/terceros)
- supervisor (acceso solo a su red asignada, bloqueo 403 ante redes/CDPs/líderes/reportes ajenos)
- admin (acceso global)
"""
import unittest
from unittest.mock import patch
from app import app


class TestApiRbacIdorMatrix(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def _login_as(self, rol: str, usuario_id: str = 'user-1'):
        with self.client.session_transaction() as sess:
            sess.clear()
            sess['usuario_id'] = usuario_id
            sess['usuario'] = f'user_{rol}'
            sess['rol'] = rol

    def _clear_session(self):
        with self.client.session_transaction() as sess:
            sess.clear()

    # ------------------------------------------------------------------
    # 1. Matriz de endpoints anónimos (todos deben retornar 401 JSON)
    # ------------------------------------------------------------------
    def test_anonymous_matrix_returns_401_json(self):
        endpoints = [
            ('GET', '/api/redes/1'),
            ('POST', '/api/redes'),
            ('PUT', '/api/redes/1'),
            ('POST', '/api/redes/1/toggle'),
            ('DELETE', '/api/redes/1'),
            ('GET', '/api/casas_de_paz/10'),
            ('POST', '/api/casas_de_paz'),
            ('PUT', '/api/casas_de_paz/10'),
            ('POST', '/api/casas_de_paz/10/toggle'),
            ('DELETE', '/api/casas_de_paz/10'),
            ('GET', '/api/lideres/5'),
            ('POST', '/api/lideres'),
            ('PUT', '/api/lideres/5'),
            ('POST', '/api/lideres/5/toggle'),
            ('DELETE', '/api/lideres/5'),
            ('GET', '/api/estructura/selectores'),
            ('GET', '/api/usuarios'),
            ('GET', '/api/usuarios/u-1'),
            ('POST', '/api/usuarios'),
            ('PUT', '/api/usuarios/u-1'),
            ('POST', '/api/usuarios/u-1/toggle'),
            ('DELETE', '/api/usuarios/u-1'),
            ('PUT', '/api/reportes/rep-1'),
            ('DELETE', '/api/reportes/rep-1'),
        ]
        self._clear_session()
        for method, url in endpoints:
            with self.subTest(method=method, url=url):
                res = self.client.open(url, method=method, json={} if method in ('POST', 'PUT') else None)
                self.assertEqual(res.status_code, 401, f"{method} {url} debería retornar 401")
                self.assertIn('application/json', res.content_type)

    # ------------------------------------------------------------------
    # 2. Matriz de mutaciones exclusivas de admin (lider_cdp y supervisor -> 403)
    # ------------------------------------------------------------------
    def test_admin_only_mutations_forbidden_for_non_admin_roles(self):
        admin_only_routes = [
            ('POST', '/api/redes', {'nombre': 'Red X'}),
            ('PUT', '/api/redes/1', {'nombre': 'Red X'}),
            ('POST', '/api/redes/1/toggle', {}),
            ('DELETE', '/api/redes/1', None),
            ('POST', '/api/casas_de_paz', {'codigo': 'C-1', 'anfitrion': 'A', 'direccion': 'D', 'red_id': 1}),
            ('PUT', '/api/casas_de_paz/1', {'codigo': 'C-1', 'anfitrion': 'A', 'direccion': 'D', 'red_id': 1}),
            ('POST', '/api/casas_de_paz/1/toggle', {}),
            ('DELETE', '/api/casas_de_paz/1', None),
            ('POST', '/api/lideres', {'nombre': 'Ana', 'apellido': 'Gil', 'rol': 'Lider', 'cdp_id': 1}),
            ('PUT', '/api/lideres/1', {'nombre': 'Ana', 'apellido': 'Gil', 'rol': 'Lider', 'cdp_id': 1}),
            ('POST', '/api/lideres/1/toggle', {}),
            ('DELETE', '/api/lideres/1', None),
            ('GET', '/api/usuarios', None),
            ('GET', '/api/usuarios/u-1', None),
            ('POST', '/api/usuarios', {'nombre': 'A', 'apellido': 'B', 'username': 'ab', 'password': 'Password1', 'rol': 'admin'}),
            ('PUT', '/api/usuarios/u-1', {'nombre': 'A', 'apellido': 'B', 'username': 'ab', 'rol': 'admin'}),
            ('POST', '/api/usuarios/u-1/toggle', {}),
            ('DELETE', '/api/usuarios/u-1', None),
            ('GET', '/api/usuarios/opciones_asignacion', None),
        ]
        for rol in ('lider_cdp', 'supervisor'):
            self._login_as(rol, usuario_id=f'{rol}-1')
            for method, url, payload in admin_only_routes:
                with self.subTest(rol=rol, method=method, url=url):
                    res = self.client.open(url, method=method, json=payload)
                    self.assertEqual(res.status_code, 403, f"{rol} en {method} {url} debe recibir 403")
                    self.assertIn('error', res.get_json())

    # ------------------------------------------------------------------
    # 3. Lectura individual de redes, CDPs, líderes y selectores (Anti-IDOR)
    # ------------------------------------------------------------------
    @patch('routes.api.estructura_api.obtener_red_servicio')
    def test_get_red_detalle_rbac_and_idor(self, mock_obtener_red):
        mock_obtener_red.side_effect = lambda rid: {'id': rid, 'nombre': f'Red {rid}', 'is_active': 1}

        # lider_cdp -> 403
        self._login_as('lider_cdp', 'lid-1')
        res_lid = self.client.get('/api/redes/1')
        self.assertEqual(res_lid.status_code, 403)

        # supervisor de red 1 -> red 1 OK, red 2 -> 403
        self._login_as('supervisor', 'sup-1')
        with patch('routes.api.estructura_api.get_supervisor_red_id', return_value=1):
            self.assertEqual(self.client.get('/api/redes/1').status_code, 200)
            self.assertEqual(self.client.get('/api/redes/2').status_code, 403)

        # admin -> cualquier red OK
        self._login_as('admin', 'admin-1')
        self.assertEqual(self.client.get('/api/redes/2').status_code, 200)

    @patch('routes.api.estructura_api.get_cdp_detalle')
    def test_get_cdp_detalle_lider_cdp_and_supervisor_idor(self, mock_cdp):
        mock_cdp.side_effect = lambda cid: {'id': cid, 'codigo': f'CDP-{cid}', 'red_id': 1 if cid == 10 else 2}

        # lider_cdp asignado a CDP 10 -> CDP 10 OK, CDP 20 -> 403
        self._login_as('lider_cdp', 'lid-1')
        with patch('routes.api.estructura_api.get_cdp_datos_usuario', return_value=({'id': 10}, [])):
            self.assertEqual(self.client.get('/api/casas_de_paz/10').status_code, 200)
            self.assertEqual(self.client.get('/api/casas_de_paz/20').status_code, 403)

        # supervisor de red 1 -> CDP 10 (red 1) OK, CDP 20 (red 2) -> 403
        self._login_as('supervisor', 'sup-1')
        with patch('routes.api.estructura_api.get_supervisor_red_id', return_value=1):
            self.assertEqual(self.client.get('/api/casas_de_paz/10').status_code, 200)
            self.assertEqual(self.client.get('/api/casas_de_paz/20').status_code, 403)

    @patch('routes.api.estructura_api.obtener_lider_servicio')
    def test_get_lider_detalle_rbac_and_idor(self, mock_lider):
        mock_lider.side_effect = lambda lid: (
            {'id': lid, 'nombre': 'Pedro', 'cdp_id': 10, 'red_id': 1}
            if lid == 1
            else {'id': lid, 'nombre': 'Lucas', 'cdp_id': 20, 'red_id': 2}
        )

        # lider_cdp -> 403
        self._login_as('lider_cdp', 'lid-1')
        self.assertEqual(self.client.get('/api/lideres/1').status_code, 403)

        # supervisor de red 1 -> líder red 1 OK, líder red 2 -> 403
        self._login_as('supervisor', 'sup-1')
        with patch('routes.api.estructura_api.get_supervisor_red_id', return_value=1):
            self.assertEqual(self.client.get('/api/lideres/1').status_code, 200)
            self.assertEqual(self.client.get('/api/lideres/2').status_code, 403)

        # admin -> ambos OK
        self._login_as('admin', 'admin-1')
        self.assertEqual(self.client.get('/api/lideres/2').status_code, 200)

    def test_get_estructura_selectores_rbac_and_supervisor_scoping(self):
        # lider_cdp -> 403
        self._login_as('lider_cdp', 'lid-1')
        self.assertEqual(self.client.get('/api/estructura/selectores').status_code, 403)

        # supervisor de red 1 -> solo recibe red 1 y casas de red 1, sin supervisores ni lideres_cdp
        self._login_as('supervisor', 'sup-1')
        mock_cdps = [
            {'id': 10, 'codigo': 'HEB-01', 'red_id': 1},
            {'id': 20, 'codigo': 'SUR-01', 'red_id': 2},
        ]
        with patch('routes.api.estructura_api.get_supervisor_red_id', return_value=1), \
             patch('routes.api.estructura_api.obtener_cdps_para_select', return_value=mock_cdps):
            res = self.client.get('/api/estructura/selectores')
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            self.assertEqual(data['supervisores'], [])
            self.assertEqual(data['lideres_cdp'], [])
            self.assertEqual([c['id'] for c in data['casas_de_paz']], [10])
            self.assertTrue(all(r['id'] == 1 for r in data['redes']))

    # ------------------------------------------------------------------
    # 4. Mutaciones de reportes: aislamiento territorial de supervisor y lider_cdp
    # ------------------------------------------------------------------
    @patch('routes.api.reportes_api.actualizar_reporte', return_value=(True, 'Actualizado'))
    @patch('routes.api.reportes_api.eliminar_reporte', return_value=(True, 'Eliminado'))
    @patch('routes.api.reportes_api.get_cdp_detalle')
    def test_reporte_mutations_supervisor_territorial_validation(self, mock_cdp, mock_del, mock_put):
        mock_cdp.side_effect = lambda cid: {'id': cid, 'red_id': 1 if cid == 10 else 2}
        self._login_as('supervisor', 'sup-1')

        with patch('routes.api.reportes_api.get_supervisor_red_id', return_value=1):
            # PUT sin cdp_id -> 400
            res_put_missing = self.client.put('/api/reportes/rep-uuid-1', json={'tema': 'Tema X'})
            self.assertEqual(res_put_missing.status_code, 400)

            # DELETE sin cdp_id -> 400 (sin fallback a cdp_id=1)
            res_del_missing = self.client.delete('/api/reportes/rep-uuid-1')
            self.assertEqual(res_del_missing.status_code, 400)

            # PUT hacia CDP 20 (red 2) -> 403
            res_put_idor = self.client.put('/api/reportes/rep-uuid-1', json={'cdp_id': 20, 'tema': 'Hack'})
            self.assertEqual(res_put_idor.status_code, 403)

            # DELETE hacia CDP 20 (red 2) -> 403
            res_del_idor = self.client.delete('/api/reportes/rep-uuid-1?cdp_id=20')
            self.assertEqual(res_del_idor.status_code, 403)
            mock_put.assert_not_called()
            mock_del.assert_not_called()

            # PUT y DELETE hacia CDP 10 (red 1 propia) -> 200
            res_put_ok = self.client.put('/api/reportes/rep-uuid-1', json={'cdp_id': 10, 'tema': 'OK'})
            self.assertEqual(res_put_ok.status_code, 200)
            res_del_ok = self.client.delete('/api/reportes/rep-uuid-1?cdp_id=10')
            self.assertEqual(res_del_ok.status_code, 200)

    def test_reporte_mutations_lider_cdp_blocks_foreign_cdp(self):
        self._login_as('lider_cdp', 'lid-1')
        with patch('routes.api.reportes_api.get_cdp_datos_usuario', return_value=({'id': 10}, [])):
            res_post = self.client.post('/api/reportes', json={'cdp_id': 99, 'tema': 'Ajeno'})
            self.assertEqual(res_post.status_code, 403)
            res_put = self.client.put('/api/reportes/rep-1', json={'cdp_id': 99, 'tema': 'Ajeno'})
            self.assertEqual(res_put.status_code, 403)
            res_del = self.client.delete('/api/reportes/rep-1?cdp_id=99')
            self.assertEqual(res_del.status_code, 403)

    # ------------------------------------------------------------------
    # 5. Aislamiento territorial de listados para lider_cdp
    # ------------------------------------------------------------------
    def test_lider_cdp_list_endpoints_isolation(self):
        """lider_cdp recibe 403 en /api/redes y solo ve su propia CDP/líderes en listados."""
        self._login_as('lider_cdp', 'lid-1')

        # GET /api/redes -> 403
        self.assertEqual(self.client.get('/api/redes').status_code, 403)

        fake_estructura_repo = unittest.mock.MagicMock()
        fake_estructura_repo.list_casas_de_paz.return_value = (
            [
                {'id': 10, 'codigo': 'CDP-10', 'red_id': 1},
                {'id': 20, 'codigo': 'CDP-20', 'red_id': 1},
            ],
            [10, 20],
        )
        fake_lider_repo = unittest.mock.MagicMock()
        fake_lider_repo.list_lideres.return_value = (
            [{'id': 1, 'nombre': 'Pedro', 'cdp_id': 10}],
            1,
            [],
            [],
        )

        with patch('routes.api.estructura_api.get_cdp_datos_usuario', return_value=({'id': 10, 'red_id': 1}, [])), \
             patch('routes.api.estructura_api.get_estructura_repository', return_value=fake_estructura_repo), \
             patch('routes.api.estructura_api.get_lider_repository', return_value=fake_lider_repo):
            # GET /api/casas_de_paz -> solo retorna CDP 10
            res_cdps = self.client.get('/api/casas_de_paz')
            self.assertEqual(res_cdps.status_code, 200)
            body_cdps = res_cdps.get_json()
            self.assertEqual([c['id'] for c in body_cdps['casas']], [10])
            self.assertEqual(body_cdps['sin_reporte_7d_ids'], [10])

            # GET /api/casas_de_paz?red_id=2 (red ajena) -> 403
            self.assertEqual(self.client.get('/api/casas_de_paz?red_id=2').status_code, 403)

            # GET /api/lideres -> fuerza cdp_id='10'
            res_lids = self.client.get('/api/lideres')
            self.assertEqual(res_lids.status_code, 200)
            _, kwargs = fake_lider_repo.list_lideres.call_args
            self.assertEqual(kwargs.get('cdp_id'), '10')

            # GET /api/lideres?cdp_id=20 o ?red_id=2 (ajenos) -> 403
            self.assertEqual(self.client.get('/api/lideres?cdp_id=20').status_code, 403)
            self.assertEqual(self.client.get('/api/lideres?red_id=2').status_code, 403)

    # ------------------------------------------------------------------
    # 6. Protección CSRF por cabecera X-CSRFToken en mutaciones /api/*
    # ------------------------------------------------------------------
    def test_api_csrf_header_enforcement_on_mutations(self):
        """Con FORCE_CSRF_IN_TESTING=True, las mutaciones /api/* exigen X-CSRFToken válido."""
        orig_force = app.config.get('FORCE_CSRF_IN_TESTING', False)
        orig_wtf = app.config.get('WTF_CSRF_ENABLED', False)
        app.config['FORCE_CSRF_IN_TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = True
        try:
            self._login_as('admin', 'admin-1')

            # Sin cabecera X-CSRFToken -> 400 csrf_error
            res_missing = self.client.post('/api/redes', json={'nombre': 'Red Sin CSRF'})
            self.assertEqual(res_missing.status_code, 400)
            self.assertEqual(res_missing.get_json().get('code'), 'csrf_error')

            # Con cabecera inválida -> 400 csrf_error
            res_invalid = self.client.post(
                '/api/redes',
                json={'nombre': 'Red Token Malo'},
                headers={'X-CSRFToken': 'token-invalido'},
            )
            self.assertEqual(res_invalid.status_code, 400)
            self.assertEqual(res_invalid.get_json().get('code'), 'csrf_error')

            # GET /api/auth/csrf-token, /api/auth/config y /api/auth/me entregan token válido
            res_tok = self.client.get('/api/auth/csrf-token')
            self.assertEqual(res_tok.status_code, 200)
            csrf_token = res_tok.get_json().get('csrf_token')
            self.assertTrue(csrf_token)

            self.assertTrue(self.client.get('/api/auth/config').get_json().get('csrf_token'))
            self.assertTrue(self.client.get('/api/auth/me').get_json().get('csrf_token'))

            # Con X-CSRFToken válido -> pasa el middleware CSRF
            with patch('routes.api.estructura_api.crear_red_servicio', return_value=(True, 'Red creada')):
                res_ok = self.client.post(
                    '/api/redes',
                    json={'nombre': 'Red Con CSRF'},
                    headers={'X-CSRFToken': csrf_token},
                )
                self.assertEqual(res_ok.status_code, 201)
        finally:
            app.config['FORCE_CSRF_IN_TESTING'] = orig_force
            app.config['WTF_CSRF_ENABLED'] = orig_wtf


if __name__ == '__main__':
    unittest.main()
