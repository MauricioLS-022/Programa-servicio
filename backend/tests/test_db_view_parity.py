"""
Pruebas de regresión de paridad BD <-> API REST para asegurar que los contratos
JSON devuelvan todos los campos requeridos por las vistas y modales React.
"""
import unittest
from unittest.mock import MagicMock, patch
from repositories.mysql_repositories import MySQLEstructuraRepository


class TestDbViewContractParity(unittest.TestCase):
    def test_mysql_estructura_repo_extracts_integer_sin_reporte_7d_ids(self):
        """sin_reporte_7d_ids debe contener IDs enteros y marcar sin_reporte_7d=True en casas activas."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_casas = [
            {'id': 1, 'codigo': 'CA-3.3', 'is_active': 1, 'asistencia': 31, 'lider': 'Pedro García'},
            {'id': 2, 'codigo': 'CA-3.2', 'is_active': 1, 'asistencia': 18, 'lider': 'Mateo Rodríguez'},
            {'id': 3, 'codigo': 'SUR-001', 'is_active': 0, 'asistencia': 14, 'lider': 'Luis'},
        ]
        # get_casas_sin_reporte_7d retorna lista de dicts como en MySQL real
        mock_sin_rep_dicts = [
            {'id': 1, 'codigo': 'CA-3.3'},
            {'id': 2, 'codigo': 'CA-3.2'},
        ]

        with patch('repositories.mysql_repositories.listar_casas_de_paz_filtradas', return_value=mock_casas), \
             patch('services.cdp_service.get_casas_sin_reporte_7d', return_value=mock_sin_rep_dicts):
            repo = MySQLEstructuraRepository(mock_conn)
            casas, sin_rep_ids = repo.list_casas_de_paz()

        self.assertEqual(sin_rep_ids, [1, 2])
        self.assertTrue(casas[0]['sin_reporte_7d'])
        self.assertTrue(casas[1]['sin_reporte_7d'])
        self.assertFalse(casas[2]['sin_reporte_7d'])


if __name__ == '__main__':
    unittest.main()
