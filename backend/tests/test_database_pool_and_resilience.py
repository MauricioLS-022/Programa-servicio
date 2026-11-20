"""
tests/test_database_pool_and_resilience.py - Pruebas unitarias e integración para:
1. Higiene del pool LifoQueue en database.py (rollback defensivo y descarte de conexiones rotas).
2. Eliminación de fallbacks silenciosos a mock con MOCK_MODE=False (HTTP 503 JSON en API).
"""
import unittest
from unittest.mock import MagicMock, patch
from flask import g
from app import app
import database


class TestDatabasePoolHygiene(unittest.TestCase):
    def setUp(self):
        self._orig_mock = app.config.get('MOCK_MODE', False)
        app.config['TESTING'] = True
        app.config['MOCK_MODE'] = False
        database.reset_circuit_breaker()

    def tearDown(self):
        database.reset_circuit_breaker()
        app.config['MOCK_MODE'] = self._orig_mock

    def test_close_db_connection_runs_rollback_before_returning_to_pool(self):
        """close_db_connection() debe ejecutar rollback() antes de devolver la conexión viva al pool."""
        fake_conn = MagicMock()
        fake_conn.open = True

        with app.app_context():
            g._db_conn = database._RequestScopedConnection(fake_conn)
            database.close_db_connection()

        fake_conn.rollback.assert_called_once()
        fake_conn.close.assert_not_called()
        self.assertEqual(database._pool.qsize(), 1)
        pooled = database._pool.get_nowait()
        self.assertIs(pooled, fake_conn)

    def test_close_db_connection_discards_and_closes_when_rollback_fails(self):
        """Si rollback() falla, close_db_connection() debe cerrar la conexión y NO devolverla al pool."""
        broken_conn = MagicMock()
        broken_conn.open = True
        broken_conn.rollback.side_effect = RuntimeError("MySQL server has gone away")

        with app.app_context():
            g._db_conn = database._RequestScopedConnection(broken_conn)
            database.close_db_connection()

        broken_conn.rollback.assert_called_once()
        broken_conn.close.assert_called_once()
        self.assertEqual(database._pool.qsize(), 0)


class TestApiNoSilentMockFallbackWhenDbDown(unittest.TestCase):
    """Cuando MOCK_MODE=False y la BD no responde, la API retorna 503 en lugar de datos ficticios."""

    def setUp(self):
        self._orig_mock = app.config.get('MOCK_MODE', False)
        app.config['TESTING'] = True
        app.config['MOCK_MODE'] = False
        app.config['WTF_CSRF_ENABLED'] = False
        database.reset_circuit_breaker()
        self.client = app.test_client()
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'admin-uuid'
            sess['usuario'] = 'admin'
            sess['rol'] = 'admin'

    def tearDown(self):
        app.config['MOCK_MODE'] = self._orig_mock
        database.reset_circuit_breaker()

    def test_api_endpoints_return_503_when_db_unavailable_and_mock_false(self):
        endpoints = [
            '/api/redes',
            '/api/casas_de_paz',
            '/api/casas_de_paz/1',
            '/api/lideres',
            '/api/reportes',
        ]
        with patch('database._create_raw_connection', side_effect=RuntimeError("DB down")):
            for url in endpoints:
                with self.subTest(url=url):
                    res = self.client.get(url)
                    self.assertEqual(res.status_code, 503, f"{url} debe responder 503 sin BD y MOCK_MODE=False")
                    data = res.get_json()
                    self.assertFalse(data.get('success', True))
                    self.assertIn('error', data)


if __name__ == '__main__':
    unittest.main()
