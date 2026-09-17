"""
Pruebas de prevención de doble envío e idempotencia en formularios.
Verifica que el servicio de reportes impida registros duplicados en la misma fecha,
que las plantillas incluyan form_guard.js y que se mantenga la integridad referencial.
"""
import unittest
from unittest.mock import patch, MagicMock
from app import app
from services.cdp_service import process_reporte


class TestFormIdempotency(unittest.TestCase):
    """Pruebas para candados de unicidad e idempotencia."""

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key-123'
        self.client = app.test_client()

    @patch('services.cdp_service.get_db_connection')
    @patch('services.cdp_service.db_queries.insertar_reporte')
    def test_rechazo_duplicado_mismo_dia(self, mock_insert, mock_db):
        """Verifica que process_reporte rechace la inserción si ya existe un reporte en esa fecha."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            'id': 'uuid-reporte-previo-123',
            'fecha': '2026-09-02'
        }
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db.return_value = mock_conn

        form_data = {
            'fecha': '2026-09-02',
            'hr_inicio': '19:00',
            'hr_fin': '20:30',
            'tema': 'Tema repetido accidental',
            'nro_regulares': '10',
            'nro_ninos': '2',
            'nro_visitas': '1',
            'nro_comprometidos': '0',
            'ofrendas_bs': '100.00',
            'ofrendas_usd': '10.00',
            'cesta_amor': '0'
        }

        with app.app_context():
            res = process_reporte(2, form_data)
            self.assertFalse(res)
            self.assertIn("Ya existe un reporte registrado", res[1])
            # Asegurar que nunca se llame a insertar_reporte ni commit
            mock_insert.assert_not_called()
            mock_conn.commit.assert_not_called()

    def test_form_guard_script_included_in_layouts(self):
        """Verifica que form_guard.js esté enlazado en los layouts administrativos."""
        with app.test_request_context():
            with open('templates/admin_layout.html', 'r', encoding='utf-8') as f:
                admin_html = f.read()
            self.assertIn('scripts/form_guard.js', admin_html)

            with open('templates/admin_form_layout.html', 'r', encoding='utf-8') as f:
                form_layout_html = f.read()
            self.assertIn('scripts/form_guard.js', form_layout_html)

    def test_form_guard_css_classes_present(self):
        """Verifica que form.css contenga las clases de estado .is-submitting y .form-guard-spinner."""
        with open('static/styles/admin/form.css', 'r', encoding='utf-8') as f:
            css_content = f.read()
        self.assertIn('.is-submitting', css_content)
        self.assertIn('.form-guard-spinner', css_content)
        self.assertIn('@keyframes formGuardSpin', css_content)


if __name__ == '__main__':
    unittest.main()

