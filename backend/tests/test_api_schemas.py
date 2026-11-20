"""
Pruebas unitarias e integración para contratos tipados Pydantic v2 en la API REST.
"""
import unittest
from app import app
from domain.exceptions import ValidationError as DomainValidationError
from schemas import (
    parse_payload,
    ReporteCreateDTO,
    UsuarioCreateDTO,
    PerfilUsernameDTO,
    PerfilPasswordDTO,
    RedCreateDTO,
    CdpCreateDTO,
    LiderCreateDTO,
)


class TestPydanticSchemasUnit(unittest.TestCase):
    def test_reporte_create_coercion_and_bounds(self):
        dto = parse_payload(
            ReporteCreateDTO,
            {
                'cdp_id': '3',
                'tema': '  La Gracia  ',
                'nro_regulares': '12',
                'nro_ninos': '',
                'ofrendas_usd': '25.5',
            },
        )
        self.assertEqual(dto.cdp_id, 3)
        self.assertEqual(dto.tema, 'La Gracia')
        self.assertEqual(dto.nro_regulares, 12)
        self.assertIsNone(dto.nro_ninos)
        self.assertEqual(dto.ofrendas_usd, 25.5)

        with self.assertRaises(DomainValidationError) as ctx:
            parse_payload(ReporteCreateDTO, {'nro_regulares': -4})
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertTrue(ctx.exception.details)
        self.assertEqual(ctx.exception.details[0]['field'], 'nro_regulares')

    def test_usuario_and_perfil_schemas(self):
        u_dto = parse_payload(
            UsuarioCreateDTO,
            {'nombre': 'Ana', 'apellido': 'Ruiz', 'username': 'ana_r', 'password': 'Password1', 'rol': 'admin'},
        )
        self.assertEqual(u_dto.tipo_usuario, 'admin')

        p_dto = parse_payload(PerfilUsernameDTO, {'username': ' nuevo_user '})
        self.assertEqual(p_dto.nuevo_username, 'nuevo_user')

        with self.assertRaises(DomainValidationError):
            parse_payload(PerfilPasswordDTO, {'password_actual': '123', 'password_nueva': 'Abc12345', 'password_confirmar': 'Otra1234'})

    def test_estructura_schemas_validation(self):
        red = parse_payload(RedCreateDTO, {'nombre': '  Hebrón  ', 'supervisor_id': ''})
        self.assertEqual(red.nombre, 'Hebrón')
        self.assertIsNone(red.supervisor_id)

        with self.assertRaises(DomainValidationError):
            parse_payload(RedCreateDTO, {'nombre': '   '})

        cdp = parse_payload(
            CdpCreateDTO,
            {'codigo': 'HEB-01', 'anfitrion': 'Pedro', 'direccion': 'Av 1', 'red_id': '2', 'telefono': '0414-1234567'},
        )
        self.assertEqual(cdp.red_id, 2)
        self.assertEqual(cdp.telefono, '+584141234567')

        lider = parse_payload(
            LiderCreateDTO,
            {'nombre': 'Luis', 'apellido': 'Diaz', 'rol': 'Lider', 'cdp_id': 1, 'telefono': '+57 300-1234567'},
        )
        self.assertEqual(lider.telefono, '+573001234567')

        with self.assertRaises(DomainValidationError):
            parse_payload(LiderCreateDTO, {'nombre': 'Luis', 'apellido': 'Diaz', 'rol': 'Lider', 'cdp_id': 1, 'telefono': '123'})

        with self.assertRaises(DomainValidationError):
            parse_payload(LiderCreateDTO, {'nombre': 'Luis', 'apellido': 'Diaz', 'rol': 'Lider', 'cdp_id': 'invalido'})


class TestPydanticSchemasApiIntegration(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_invalid_reporte_payload_returns_400_with_details(self):
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'admin-1'
            sess['rol'] = 'admin'

        res = self.client.post('/api/reportes', json={'cdp_id': 1, 'nro_regulares': -10})
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data['success'])
        self.assertEqual(data['code'], 'validation_error')
        self.assertIn('details', data)
        self.assertEqual(data['details'][0]['field'], 'nro_regulares')

    def test_invalid_red_payload_returns_400_with_details(self):
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'admin-1'
            sess['rol'] = 'admin'

        res = self.client.post('/api/redes', json={'nombre': ''})
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data['success'])
        self.assertIn('details', data)


if __name__ == '__main__':
    unittest.main()
