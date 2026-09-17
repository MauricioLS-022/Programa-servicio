"""
Tests de integración para los filtros por URL en la vista de Estructura Organizacional:
- /admin/estructura con parámetros red_id, cdp_id, filtro, q
- Deducción automática de red_id a partir de cdp_id
- Renderizado de clases activas y atributos data-initial-* en el HTML
- Presencia de identificadores id="cdp-..." y data-cdp-id="..." en las tarjetas de casas
- /supervisor/estructura con parámetros de consulta
"""
import unittest
from unittest.mock import patch, MagicMock
from app import app


class TestEstructuraUrlFilters(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

        self.mock_context_data = {
            'redes_estructura': [
                {
                    'id': 1,
                    'nombre': 'Red Alfa',
                    'slug': 'red-1',
                    'supervisor': 'Pastor Uno',
                    'supervisor_id': 'sup-1',
                    'total_casas': 1,
                    'is_active': True,
                },
                {
                    'id': 2,
                    'nombre': 'Red Beta',
                    'slug': 'red-2',
                    'supervisor': 'Pastor Dos',
                    'supervisor_id': 'sup-2',
                    'total_casas': 1,
                    'is_active': True,
                }
            ],
            'casas_estructura': [
                {
                    'id': 10,
                    'red_id': 1,
                    'red_slug': 'red-1',
                    'codigo': 'ALFA-01',
                    'nombre': 'Casa Alfa 1',
                    'anfitrion': 'Carlos Pérez',
                    'lider': 'Ana Gómez',
                    'zona': 'Centro',
                    'is_active': True,
                    'tiene_reporte_7d': True,
                    'pendiente_7d': False,
                    'asistencia': 12,
                },
                {
                    'id': 20,
                    'red_id': 2,
                    'red_slug': 'red-2',
                    'codigo': 'BETA-01',
                    'nombre': 'Casa Beta 1',
                    'anfitrion': 'Luis Ruiz',
                    'lider': 'Pedro Soto',
                    'zona': 'Norte',
                    'is_active': True,
                    'tiene_reporte_7d': False,
                    'pendiente_7d': True,
                    'asistencia': 8,
                }
            ],
            'total_casas_estructura': 2,
            'total_asistencia_estructura': 20,
            'casas_activas_estructura': 2,
            'casas_pausadas_estructura': 0,
            'casas_pendientes_estructura': 1,
            'total_sin_reporte_7d': 1,
            'casas_sin_reporte_ids': [20],
            'casas_sin_reporte_codigos': ['BETA-01'],
            'estructura_mock': False,
            'estructura_vacia': False,
        }

    def _login_as(self, rol="admin", usuario_id="usr-1"):
        with self.client.session_transaction() as sess:
            sess['usuario'] = 'test_user'
            sess['rol'] = rol
            sess['usuario_id'] = usuario_id

    @patch('routes.admin_routes.get_estructura_context')
    def test_admin_estructura_default_without_params(self, mock_ctx):
        """Sin parámetros en URL, 'Todas las redes' debe ser la opción activa por defecto."""
        mock_ctx.return_value = dict(self.mock_context_data)
        self._login_as('admin')

        res = self.client.get('/admin/estructura')
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)

        # 'Todas las redes' debe tener clase active
        self.assertIn('red-card red-card-all active', html)
        self.assertIn('data-initial-red=""', html)
        self.assertIn('Mostrando las casas de <strong id="casasFilterLabel">todas las redes</strong>', html)

    @patch('routes.admin_routes.get_estructura_context')
    def test_admin_estructura_with_red_id(self, mock_ctx):
        """Con ?red_id=1, la Red Alfa debe tener la clase active y 'Todas las redes' no debe estar activa."""
        mock_ctx.return_value = dict(self.mock_context_data)
        self._login_as('admin')

        res = self.client.get('/admin/estructura?red_id=1')
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)

        self.assertNotIn('red-card red-card-all active', html)
        self.assertIn('red-card red-card-all ', html)
        self.assertIn('data-initial-red="1"', html)
        self.assertIn('Mostrando las casas de <strong id="casasFilterLabel">Red Alfa</strong>', html)

    @patch('routes.admin_routes.get_estructura_context')
    def test_admin_estructura_with_cdp_id_infers_red(self, mock_ctx):
        """Si se pasa ?cdp_id=20 sin red_id, debe deducir red_id=2 y activar Red Beta."""
        mock_ctx.return_value = dict(self.mock_context_data)
        self._login_as('admin')

        res = self.client.get('/admin/estructura?cdp_id=20')
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)

        self.assertIn('data-initial-red="2"', html)
        self.assertIn('data-initial-cdp="20"', html)
        self.assertIn('Mostrando las casas de <strong id="casasFilterLabel">Red Beta</strong>', html)

    @patch('routes.admin_routes.get_estructura_context')
    def test_admin_estructura_with_filtro_and_search(self, mock_ctx):
        """Parámetros ?filtro=pendientes y ?q=Carlos se propagan a data-initial y al campo de búsqueda."""
        mock_ctx.return_value = dict(self.mock_context_data)
        self._login_as('admin')

        res = self.client.get('/admin/estructura?filtro=pendientes&q=Carlos')
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)

        self.assertIn('data-initial-filtro="pendientes"', html)
        self.assertIn('data-initial-q="Carlos"', html)
        self.assertIn('value="Carlos"', html)

    @patch('routes.admin_routes.get_estructura_context')
    def test_casa_cards_have_id_and_cdp_dataset(self, mock_ctx):
        """Las tarjetas de Casa de Paz deben incluir id='cdp-X' y data-cdp-id='X' para permitir scroll y resalte."""
        mock_ctx.return_value = dict(self.mock_context_data)
        self._login_as('admin')

        res = self.client.get('/admin/estructura')
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)

        self.assertIn('id="cdp-10"', html)
        self.assertIn('data-cdp-id="10"', html)
        self.assertIn('id="cdp-20"', html)
        self.assertIn('data-cdp-id="20"', html)

    @patch('routes.supervisor_routes.get_estructura_context')
    def test_supervisor_estructura_with_cdp_id(self, mock_ctx):
        """La ruta de supervisor también debe capturar y enviar selected_cdp_id al contexto."""
        mock_ctx.return_value = dict(self.mock_context_data)
        self._login_as('supervisor')

        res = self.client.get('/supervisor/estructura?cdp_id=10')
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)

        self.assertIn('data-initial-cdp="10"', html)
        self.assertIn('data-initial-red="1"', html)

    @patch('routes.admin_routes.get_estructura_context')
    def test_admin_estructura_with_mismatched_red_and_cdp_reconciles_red(self, mock_ctx):
        """Si en la URL se pasa un red_id discrepante (ej: red_id=1 pero cdp_id=20 pertenece a red 2), debe reconciliarse a red_id=2."""
        mock_ctx.return_value = dict(self.mock_context_data)
        self._login_as('admin')

        res = self.client.get('/admin/estructura?red_id=1&cdp_id=20')
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)

        self.assertIn('data-initial-red="2"', html)
        self.assertIn('data-initial-cdp="20"', html)
        self.assertIn('Mostrando las casas de <strong id="casasFilterLabel">Red Beta</strong>', html)

    def test_css_highlight_pulse_has_opacity(self):
        """Verifica que el CSS de la tarjeta resaltada tenga opacity: 1 !important y animación con forwards."""
        import os
        css_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'styles', 'admin', 'estructura.css')
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()

        self.assertIn('.casa-card.casa-card-highlighted', css_content)
        self.assertIn('opacity: 1 !important;', css_content)
        self.assertIn('@keyframes cdpTargetPulse', css_content)
        self.assertIn('forwards;', css_content)


if __name__ == '__main__':
    unittest.main()

