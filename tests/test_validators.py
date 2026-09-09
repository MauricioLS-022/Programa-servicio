"""
tests/test_validators.py - Pruebas unitarias para el módulo defensivo utils/validators.py
"""

import unittest
from datetime import date, timedelta
from utils.validators import (
    validate_username,
    validate_password_strength,
    validate_person_name,
    validate_phone,
    validate_uuid,
    validate_positive_int,
    validate_currency,
    validate_date,
    validate_time_range,
    sanitize_text,
    validate_report_form
)


class TestValidators(unittest.TestCase):

    def test_validate_username(self):
        # Válidos
        ok, user = validate_username("carlos.mendez")
        self.assertTrue(ok)
        self.assertEqual(user, "carlos.mendez")

        ok, user = validate_username("lider_cdp-01")
        self.assertTrue(ok)

        # Inválidos
        ok, msg = validate_username("ab")  # Menor a 3
        self.assertFalse(ok)
        self.assertIn("al menos 3", msg)

        ok, msg = validate_username("a" * 31)  # Mayor a 30
        self.assertFalse(ok)
        self.assertIn("no puede exceder 30", msg)

        ok, msg = validate_username("user name")  # Con espacios
        self.assertFalse(ok)

        ok, msg = validate_username("user<script>")  # Caracteres peligrosos
        self.assertFalse(ok)

        ok, msg = validate_username("...")  # Solo puntuación
        self.assertFalse(ok)

    def test_validate_password_strength(self):
        # Válida (>=8 chars, lower, upper, digit)
        ok, msg = validate_password_strength("VinoNuevo2026")
        self.assertTrue(ok)

        # Muy corta
        ok, msg = validate_password_strength("Pass1")
        self.assertFalse(ok)
        self.assertIn("al menos 8", msg)

        # Sin mayúscula
        ok, msg = validate_password_strength("vinonuevo2026")
        self.assertFalse(ok)
        self.assertIn("mayúscula", msg)

        # Sin número
        ok, msg = validate_password_strength("VinoNuevoSeguro")
        self.assertFalse(ok)
        self.assertIn("número", msg)

    def test_validate_person_name(self):
        # Válidos con acentos y ñ
        ok, val = validate_person_name("María José", "Nombre")
        self.assertTrue(ok)
        self.assertEqual(val, "María José")

        ok, val = validate_person_name("Peña-Rivera", "Apellido")
        self.assertTrue(ok)

        # Inválidos
        ok, msg = validate_person_name("A", "Nombre")
        self.assertFalse(ok)

        ok, msg = validate_person_name("Nombre123", "Nombre")
        self.assertFalse(ok)

        ok, msg = validate_person_name("<script>", "Nombre")
        self.assertFalse(ok)

    def test_validate_phone(self):
        # Válidos
        ok, phone, msg = validate_phone("+58 412-1234567")
        self.assertTrue(ok)
        self.assertEqual(phone, "+58 412-1234567")

        ok, phone, msg = validate_phone("04141234567")
        self.assertTrue(ok)

        # Inválidos
        ok, phone, msg = validate_phone("123")  # Muy corto
        self.assertFalse(ok)

        ok, phone, msg = validate_phone("telefono-invalido")
        self.assertFalse(ok)

    def test_validate_uuid(self):
        self.assertTrue(validate_uuid("702f2129-7d4e-11f1-bf9e-2016d8516279"))
        self.assertTrue(validate_uuid("ca58cfc6-8337-11f1-8217-2016d8516279"))
        self.assertFalse(validate_uuid("no-es-uuid"))
        self.assertFalse(validate_uuid("12345"))
        self.assertFalse(validate_uuid(""))
        self.assertFalse(validate_uuid(None))

    def test_validate_positive_int(self):
        ok, val, msg = validate_positive_int("15", default=0, min_val=0, max_val=100)
        self.assertTrue(ok)
        self.assertEqual(val, 15)

        # Negativo
        ok, val, msg = validate_positive_int("-5", default=0, min_val=0, max_val=100)
        self.assertFalse(ok)

        # Desbordamiento
        ok, val, msg = validate_positive_int("9999", default=0, min_val=0, max_val=100)
        self.assertFalse(ok)

        # No numérico
        ok, val, msg = validate_positive_int("diez", default=0, min_val=0, max_val=100)
        self.assertFalse(ok)

    def test_validate_currency(self):
        ok, val, msg = validate_currency("25.50", default=0.0)
        self.assertTrue(ok)
        self.assertEqual(val, 25.50)

        # Coma como separador
        ok, val, msg = validate_currency("100,50", default=0.0)
        self.assertTrue(ok)
        self.assertEqual(val, 100.50)

        # Negativo
        ok, val, msg = validate_currency("-10.00", default=0.0)
        self.assertFalse(ok)

        # NaN / Infinity
        ok, val, msg = validate_currency("nan", default=0.0)
        self.assertFalse(ok)

        ok, val, msg = validate_currency("inf", default=0.0)
        self.assertFalse(ok)

    def test_validate_date(self):
        ayer = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        ok, val, msg = validate_date(ayer)
        self.assertTrue(ok)

        # Fecha futura no permitida
        manana = (date.today() + timedelta(days=2)).strftime('%Y-%m-%d')
        ok, val, msg = validate_date(manana, allow_future=False)
        self.assertFalse(ok)
        self.assertIn("futura", msg.lower())

        # Formato inválido
        ok, val, msg = validate_date("22/08/2026")
        self.assertFalse(ok)

    def test_validate_time_range(self):
        ok, msg = validate_time_range("18:00", "19:30")
        self.assertTrue(ok)

        # Fin antes que inicio
        ok, msg = validate_time_range("20:00", "18:00")
        self.assertFalse(ok)
        self.assertIn("posterior", msg.lower())

        # Horas iguales
        ok, msg = validate_time_range("18:00", "18:00")
        self.assertFalse(ok)

    def test_sanitize_text(self):
        # Neutraliza caracteres HTML XSS
        malicious = "<script>alert('xss')</script>"
        sanitized = sanitize_text(malicious)
        self.assertNotIn("<script>", sanitized)
        self.assertIn("&lt;script&gt;", sanitized)

        # Truncamiento
        long_text = "a" * 300
        self.assertEqual(len(sanitize_text(long_text, max_length=50)), 50)

    def test_validate_report_form(self):
        hoy = date.today().strftime('%Y-%m-%d')
        form_data = {
            'fecha': hoy,
            'hr_inicio': '18:00',
            'hr_fin': '19:30',
            'tema': 'El Buen Samaritano',
            'nro_regulares': '10',
            'nro_ninos': '5',
            'nro_visitas': '2',
            'nro_comprometidos': '1',
            'reconciliaciones': '0',
            'confesiones': '1',
            'ofrendas_usd': '20.00',
            'ofrendas_bs': '200.00',
            'cesta_amor': '1',
            'observaciones': 'Excelente asistencia'
        }
        ok, msg, clean_data = validate_report_form(form_data, cdp_id=1)
        self.assertTrue(ok)
        self.assertEqual(clean_data['cdp_id'], 1)
        self.assertEqual(clean_data['nro_regulares'], 10)
        self.assertEqual(clean_data['ofrendas_usd'], 20.00)

        # Formulario con hora invertida
        bad_form = form_data.copy()
        bad_form['hr_inicio'] = '21:00'
        bad_form['hr_fin'] = '19:00'
        ok, msg, clean_data = validate_report_form(bad_form, cdp_id=1)
        self.assertFalse(ok)


if __name__ == '__main__':
    unittest.main()
