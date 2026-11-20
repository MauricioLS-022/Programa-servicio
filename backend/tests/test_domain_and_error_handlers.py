"""
Pruebas unitarias e integración para excepciones de dominio y Content Negotiation
en manejadores globales de error de Flask (JSON para /api/* vs HTML para SSR).
"""
import unittest
from app import app
from domain.exceptions import (
    DomainError,
    ValidationError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    ConflictError,
    ServiceUnavailableError,
)


class TestDomainExceptions(unittest.TestCase):
    def test_exception_status_codes_and_serialization(self):
        cases = [
            (ValidationError("Campo inválido", details=[{"field": "tema", "message": "requerido"}]), 400, "validation_error"),
            (UnauthorizedError("No autenticado"), 401, "unauthorized"),
            (ForbiddenError("Acceso denegado"), 403, "forbidden"),
            (NotFoundError("No encontrado"), 404, "not_found"),
            (ConflictError("Duplicado"), 409, "conflict"),
            (ServiceUnavailableError("BD no disponible"), 503, "service_unavailable"),
        ]
        for exc, expected_status, expected_code in cases:
            self.assertEqual(exc.status_code, expected_status)
            self.assertEqual(exc.code, expected_code)
            payload = exc.to_dict()
            self.assertFalse(payload["success"])
            self.assertEqual(payload["error"], exc.message)
            self.assertEqual(payload["code"], expected_code)

        val_dict = cases[0][0].to_dict()
        self.assertIn("details", val_dict)
        self.assertEqual(val_dict["details"][0]["field"], "tema")

    def test_custom_domain_error_override(self):
        err = DomainError("Custom", status_code=422, code="unprocessable")
        self.assertEqual(err.status_code, 422)
        self.assertEqual(err.to_dict(), {"success": False, "error": "Custom", "code": "unprocessable"})


class TestContentNegotiationErrorHandlers(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_api_404_returns_json(self):
        res = self.client.get('/api/ruta-inexistente-de-prueba')
        self.assertEqual(res.status_code, 404)
        self.assertIn('application/json', res.content_type)
        data = res.get_json()
        self.assertFalse(data['success'])
        self.assertEqual(data['code'], 'not_found')
        self.assertIn('error', data)

    def test_ssr_404_returns_html(self):
        res = self.client.get('/pagina-ssr-inexistente-de-prueba', headers={'Accept': 'text/html'})
        self.assertEqual(res.status_code, 404)
        self.assertIn('text/html', res.content_type)

    def test_accept_json_on_non_api_404_returns_json(self):
        res = self.client.get('/pagina-inexistente', headers={'Accept': 'application/json'})
        self.assertEqual(res.status_code, 404)
        self.assertIn('application/json', res.content_type)

    def test_domain_error_handler_returns_json_on_api_context(self):
        with app.test_request_context('/api/test-domain-err', headers={'Accept': 'application/json'}):
            resp, status = app.error_handler_spec[None][None][DomainError](NotFoundError("Entidad X no existe"))
            self.assertEqual(status, 404)
            data = resp.get_json()
            self.assertEqual(data['error'], 'Entidad X no existe')
            self.assertEqual(data['code'], 'not_found')


if __name__ == '__main__':
    unittest.main()
