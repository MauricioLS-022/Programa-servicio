"""
Pruebas unitarias para decoradores REST (@api_auth_required, @api_role_required)
y política centralizada de acceso territorial (AccessPolicy).
"""
import unittest
from app import app
from domain.exceptions import ForbiddenError, ValidationError
from policies.access_policy import AccessPolicy, UserContext


class TestAccessPolicy(unittest.TestCase):
    def test_admin_permissions(self):
        admin = UserContext(usuario_id='admin-1', rol='admin')
        self.assertTrue(AccessPolicy.can_manage_usuarios(admin))
        self.assertTrue(AccessPolicy.can_access_red(admin, 99))
        self.assertTrue(AccessPolicy.can_access_cdp(admin, 12, cdp_red_id=5))

        scope = AccessPolicy.resolve_reportes_scope(admin, requested_red_id='2', requested_cdp_id='7')
        self.assertFalse(scope['empty'])
        self.assertEqual(scope['target_red_id'], '2')
        self.assertEqual(scope['target_cdp_id'], '7')

        self.assertEqual(AccessPolicy.resolve_reporte_mutation_cdp_id(admin, '5'), 5)
        with self.assertRaises(ValidationError):
            AccessPolicy.resolve_reporte_mutation_cdp_id(admin, '')

    def test_supervisor_territorial_isolation(self):
        sup = UserContext(usuario_id='sup-1', rol='supervisor', supervisor_red_id=3)
        self.assertFalse(AccessPolicy.can_manage_usuarios(sup))
        self.assertTrue(AccessPolicy.can_access_red(sup, 3))
        self.assertFalse(AccessPolicy.can_access_red(sup, 4))
        self.assertTrue(AccessPolicy.can_access_cdp(sup, 10, cdp_red_id=3))
        self.assertFalse(AccessPolicy.can_access_cdp(sup, 10, cdp_red_id=4))

        scope_ok = AccessPolicy.resolve_reportes_scope(sup, requested_red_id='3')
        self.assertEqual(scope_ok['supervisor_red_id'], 3)
        self.assertEqual(scope_ok['target_red_id'], '3')

        with self.assertRaises(ForbiddenError):
            AccessPolicy.resolve_reportes_scope(sup, requested_red_id='9')

        sup_sin_red = UserContext(usuario_id='sup-2', rol='supervisor', supervisor_red_id=None)
        self.assertTrue(AccessPolicy.resolve_reportes_scope(sup_sin_red)['empty'])
        self.assertFalse(AccessPolicy.can_access_red(sup_sin_red, 1))

        # Mutaciones de reporte de supervisor exigen cdp_id explícito y pertenencia a su red
        self.assertEqual(
            AccessPolicy.resolve_reporte_mutation_cdp_id(sup, 10, allow_supervisor=True, target_cdp_red_id=3),
            10,
        )
        with self.assertRaises(ValidationError):
            AccessPolicy.resolve_reporte_mutation_cdp_id(sup, None, allow_supervisor=True, target_cdp_red_id=3)
        with self.assertRaises(ForbiddenError):
            AccessPolicy.resolve_reporte_mutation_cdp_id(sup, 10, allow_supervisor=True, target_cdp_red_id=4)
        with self.assertRaises(ForbiddenError):
            AccessPolicy.resolve_reporte_mutation_cdp_id(sup, 10, allow_supervisor=True, target_cdp_red_id=None)

    def test_lider_cdp_isolation(self):
        lider = UserContext(usuario_id='lid-1', rol='lider_cdp', cdp_id=7)
        self.assertFalse(AccessPolicy.can_manage_usuarios(lider))
        self.assertTrue(AccessPolicy.can_access_cdp(lider, 7))
        self.assertFalse(AccessPolicy.can_access_cdp(lider, 8))

        scope_ok = AccessPolicy.resolve_reportes_scope(lider, requested_cdp_id='7')
        self.assertEqual(scope_ok['target_cdp_id'], '7')

        with self.assertRaises(ForbiddenError):
            AccessPolicy.resolve_reportes_scope(lider, requested_cdp_id='8')

        self.assertEqual(AccessPolicy.resolve_reporte_mutation_cdp_id(lider, None), 7)
        with self.assertRaises(ForbiddenError):
            AccessPolicy.resolve_reporte_mutation_cdp_id(lider, 99)


class TestApiAuthDecorators(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_api_dashboard_legacy_redirect_without_json_accept(self):
        res = self.client.get('/api/dashboard/datos')
        self.assertEqual(res.status_code, 302)
        self.assertIn('/iniciar_sesion', res.headers.get('Location', ''))

    def test_api_dashboard_returns_401_json_with_json_accept(self):
        res = self.client.get('/api/dashboard/datos', headers={'Accept': 'application/json'})
        self.assertEqual(res.status_code, 401)
        self.assertIn('application/json', res.content_type)
        self.assertIn('error', res.get_json())

    def test_api_usuarios_returns_401_and_403_json(self):
        res_anon = self.client.get('/api/usuarios')
        self.assertEqual(res_anon.status_code, 401)
        self.assertEqual(res_anon.get_json().get('error'), 'No autenticado')

        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'sup-1'
            sess['rol'] = 'supervisor'
        res_forb = self.client.get('/api/usuarios')
        self.assertEqual(res_forb.status_code, 403)
        self.assertIn('error', res_forb.get_json())


if __name__ == '__main__':
    unittest.main()
