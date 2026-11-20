"""Pruebas unitarias del servicio de exportación binaria PDF, Excel (.xlsx) y CSV."""
import io
import os
import sys
import unittest

from openpyxl import load_workbook

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.export_service import (
    MIME_CSV,
    MIME_PDF,
    MIME_XLSX,
    build_casas_xlsx,
    build_csv,
    build_lideres_xlsx,
    build_reportes_csv,
    build_reportes_pdf,
    build_reportes_xlsx,
    build_usuarios_xlsx,
    export_reportes,
    sanitize_spreadsheet_cell,
)


class TestExportService(unittest.TestCase):
    def setUp(self):
        self.sample_reportes = [
            {
                'fecha': '2026-10-18',
                'red_nombre': 'Red Hebrón',
                'cdp_codigo': 'HEB-01',
                'cdp_nombre': 'Familia Pérez',
                'lider_nombre': 'Carlos Méndez',
                'tema': 'La Fe que Mueve Montañas 👋',
                'nro_regulares': 10,
                'nro_niños': 3,
                'nro_visitas': 2,
                'nro_comprometidos': 5,
                'asistencia': 20,
                'reconciliaciones': 1,
                'confesiones': 2,
                'cesta_amor': 1,
                'ofrendas_usd': 45.50,
                'ofrendas_bs': 1800.00,
                'observaciones': '=CMD|\' /C calc\'!A0',
            },
            {
                'fecha': '2026-10-25',
                'red_nombre': 'Red Hebrón',
                'cdp_codigo': 'HEB-02',
                'cdp_nombre': 'Familia Gómez',
                'lider_nombre': 'Ana Silva',
                'tema': '+SUM(A1:A5)',
                'nro_regulares': 8,
                'nro_niños': 2,
                'nro_visitas': 1,
                'nro_comprometidos': 4,
                'asistencia': 15,
                'reconciliaciones': 0,
                'confesiones': 1,
                'cesta_amor': 0,
                'ofrendas_usd': 30.25,
                'ofrendas_bs': 1200.50,
                'observaciones': '@HYPERLINK("http://evil.example")',
            },
        ]

    def test_sanitize_spreadsheet_cell_blocks_formula_prefixes(self):
        self.assertEqual(sanitize_spreadsheet_cell('=SUM(A1:A2)'), "'=SUM(A1:A2)")
        self.assertEqual(sanitize_spreadsheet_cell('+1+1'), "'+1+1")
        self.assertEqual(sanitize_spreadsheet_cell('-2+3'), "'-2+3")
        self.assertEqual(sanitize_spreadsheet_cell('@SUM(1,2)'), "'@SUM(1,2)")
        self.assertEqual(sanitize_spreadsheet_cell('Texto seguro'), 'Texto seguro')
        self.assertEqual(sanitize_spreadsheet_cell(42), 42)
        self.assertEqual(sanitize_spreadsheet_cell(12.5), 12.5)
        self.assertEqual(sanitize_spreadsheet_cell(None), '')

    def test_sanitize_spreadsheet_cell_preserves_valid_e164_phone_only_on_phone_col(self):
        self.assertEqual(sanitize_spreadsheet_cell('+584121234567', is_phone=True), '+584121234567')
        self.assertEqual(sanitize_spreadsheet_cell('=CMD|calc', is_phone=True), "'=CMD|calc")
        self.assertEqual(sanitize_spreadsheet_cell('+584121234567', is_phone=False), "'+584121234567")

    def test_build_reportes_pdf_valid_header_and_unicode_safe(self):
        pdf_bytes = build_reportes_pdf(self.sample_reportes, filters_summary='Red Hebrón')
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))
        self.assertGreater(len(pdf_bytes), 500)

    def test_build_reportes_pdf_empty_list(self):
        pdf_bytes = build_reportes_pdf([])
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))

    def test_build_reportes_xlsx_totals_and_formula_sanitization(self):
        xlsx_bytes = build_reportes_xlsx(self.sample_reportes)
        self.assertTrue(xlsx_bytes.startswith(b'PK'))

        wb = load_workbook(io.BytesIO(xlsx_bytes))
        ws = wb.active
        self.assertEqual(ws.title, 'Reportes Consolidados')
        # 1 header + 2 data rows + 1 totals row = 4 rows
        self.assertEqual(ws.max_row, 4)
        # Check formula neutralization
        self.assertEqual(ws.cell(row=2, column=16).value, "'=CMD|' /C calc'!A0")
        self.assertEqual(ws.cell(row=3, column=5).value, "'+SUM(A1:A5)")
        self.assertEqual(ws.cell(row=3, column=16).value, '\'@HYPERLINK("http://evil.example")')
        # Check consolidated totals row
        self.assertIn('TOTALES (2 reportes)', ws.cell(row=4, column=1).value)
        self.assertEqual(ws.cell(row=4, column=10).value, 35)  # asistencia total 20 + 15
        self.assertAlmostEqual(ws.cell(row=4, column=14).value, 75.75)  # USD 45.50 + 30.25
        self.assertAlmostEqual(ws.cell(row=4, column=15).value, 3000.50)  # Bs 1800 + 1200.50

    def test_build_reportes_csv_utf8_bom_and_sanitization(self):
        csv_bytes = build_reportes_csv(self.sample_reportes)
        self.assertTrue(csv_bytes.startswith(b'\xef\xbb\xbf'))
        decoded = csv_bytes.decode('utf-8-sig')
        self.assertIn('TOTALES (2 reportes)', decoded)
        self.assertIn("'=CMD|' /C calc'!A0", decoded)
        self.assertIn('75.75', decoded)
        self.assertIn('3000.50', decoded)

    def test_build_usuarios_lideres_casas_xlsx_preserve_phones_and_headers(self):
        usuarios_bytes = build_usuarios_xlsx([
            {
                'nombre': 'María',
                'apellido': 'López',
                'username': 'mlopez',
                'tipo_usuario': 'supervisor',
                'is_active': 1,
                'red_nombre': 'Red Hebrón',
                'cdp_codigo': '',
            }
        ])
        wb_u = load_workbook(io.BytesIO(usuarios_bytes))
        self.assertEqual(wb_u.active.cell(row=2, column=3).value, 'mlopez')

        lideres_bytes = build_lideres_xlsx([
            {
                'nombre': 'Juan',
                'apellido': 'Pérez',
                'rol': 'Lider',
                'red_nombre': 'Red Hebrón',
                'cdp_codigo': 'HEB-01',
                'telefono': '+584121234567',
                'is_active': 1,
            }
        ])
        wb_l = load_workbook(io.BytesIO(lideres_bytes))
        tel_cell = wb_l.active.cell(row=2, column=6)
        self.assertEqual(tel_cell.value, '+584121234567')
        self.assertEqual(tel_cell.number_format, '@')

        casas_bytes = build_casas_xlsx([
            {
                'codigo': 'HEB-01',
                'red_nombre': 'Red Hebrón',
                'anfitrion': 'Familia Pérez',
                'lider_nombre': 'Juan Pérez',
                'telefono': '+584141234567',
                'direccion': 'Av. Principal #10',
                'is_active': 1,
                'sin_reporte_7d': True,
            }
        ])
        wb_c = load_workbook(io.BytesIO(casas_bytes))
        self.assertEqual(wb_c.active.cell(row=2, column=5).value, '+584141234567')
        self.assertEqual(wb_c.active.cell(row=2, column=8).value, 'Pendiente (>7d)')

    def test_export_reportes_dispatcher_and_invalid_format(self):
        data_pdf, mime_pdf, name_pdf = export_reportes(self.sample_reportes, 'pdf')
        self.assertEqual(mime_pdf, MIME_PDF)
        self.assertTrue(name_pdf.endswith('.pdf'))
        self.assertTrue(data_pdf.startswith(b'%PDF'))

        data_xlsx, mime_xlsx, name_xlsx = export_reportes(self.sample_reportes, 'xlsx')
        self.assertEqual(mime_xlsx, MIME_XLSX)
        self.assertTrue(name_xlsx.endswith('.xlsx'))
        self.assertTrue(data_xlsx.startswith(b'PK'))

        data_csv, mime_csv, name_csv = export_reportes(self.sample_reportes, 'csv')
        self.assertEqual(mime_csv, MIME_CSV)
        self.assertTrue(name_csv.endswith('.csv'))
        self.assertTrue(data_csv.startswith(b'\xef\xbb\xbf'))

        with self.assertRaises(ValueError):
            export_reportes(self.sample_reportes, 'docx')


if __name__ == '__main__':
    unittest.main()
