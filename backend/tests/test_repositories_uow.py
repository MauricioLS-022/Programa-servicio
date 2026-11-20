"""
Pruebas unitarias para UnitOfWork y adaptadores de repositorio (MySQL, Mock y Null).
"""
import unittest
from unittest.mock import MagicMock
from repositories import (
    unit_of_work,
    get_reporte_repository,
    get_estructura_repository,
    get_usuario_repository,
    get_lider_repository,
)
from repositories.mysql_repositories import (
    MySQLReporteRepository,
    MySQLEstructuraRepository,
    MySQLUsuarioRepository,
    MySQLLiderRepository,
)
from repositories.mock_repositories import (
    MockReporteRepository,
    NullReporteRepository,
    MockEstructuraRepository,
    NullEstructuraRepository,
    MockUsuarioRepository,
    NullUsuarioRepository,
    MockLiderRepository,
    NullLiderRepository,
)


class TestUnitOfWork(unittest.TestCase):
    def test_uow_commits_and_closes_on_success(self):
        mock_conn = MagicMock()
        with unit_of_work(conn_provider=lambda: mock_conn, transactional=True) as uow:
            self.assertIsNotNone(uow)
            uow.cursor()
        mock_conn.commit.assert_called_once()
        mock_conn.rollback.assert_not_called()
        mock_conn.close.assert_called_once()

    def test_uow_rolls_back_and_closes_on_exception(self):
        mock_conn = MagicMock()
        with self.assertRaises(RuntimeError):
            with unit_of_work(conn_provider=lambda: mock_conn, transactional=True) as uow:
                self.assertIsNotNone(uow)
                raise RuntimeError("Fallo simulado de SQL")
        mock_conn.commit.assert_not_called()
        mock_conn.rollback.assert_called_once()
        mock_conn.close.assert_called_once()

    def test_uow_yields_none_when_no_connection(self):
        with unit_of_work(conn_provider=lambda: None, transactional=True) as uow:
            self.assertIsNone(uow)


class TestRepositorySelectionAndAdapters(unittest.TestCase):
    def test_selects_mysql_adapter_when_connection_available(self):
        mock_conn = MagicMock()
        self.assertIsInstance(get_reporte_repository(conn_provider=lambda: mock_conn), MySQLReporteRepository)
        self.assertIsInstance(get_estructura_repository(conn_provider=lambda: mock_conn), MySQLEstructuraRepository)
        self.assertIsInstance(get_usuario_repository(conn_provider=lambda: mock_conn), MySQLUsuarioRepository)
        self.assertIsInstance(get_lider_repository(conn_provider=lambda: mock_conn), MySQLLiderRepository)

    def test_selects_mock_adapter_when_mock_mode_enabled(self):
        self.assertIsInstance(
            get_reporte_repository(conn_provider=lambda: None, mock_checker=lambda: True),
            MockReporteRepository,
        )
        self.assertIsInstance(
            get_estructura_repository(conn_provider=lambda: None, mock_checker=lambda: True),
            MockEstructuraRepository,
        )
        self.assertIsInstance(
            get_usuario_repository(conn_provider=lambda: None, mock_checker=lambda: True),
            MockUsuarioRepository,
        )
        self.assertIsInstance(
            get_lider_repository(conn_provider=lambda: None, mock_checker=lambda: True),
            MockLiderRepository,
        )

    def test_selects_null_adapter_when_no_db_and_mock_disabled(self):
        rep_repo = get_reporte_repository(conn_provider=lambda: None, mock_checker=lambda: False)
        est_repo = get_estructura_repository(conn_provider=lambda: None, mock_checker=lambda: False)
        usr_repo = get_usuario_repository(conn_provider=lambda: None, mock_checker=lambda: False)
        lid_repo = get_lider_repository(conn_provider=lambda: None, mock_checker=lambda: False)

        self.assertIsInstance(rep_repo, NullReporteRepository)
        self.assertIsInstance(est_repo, NullEstructuraRepository)
        self.assertIsInstance(usr_repo, NullUsuarioRepository)
        self.assertIsInstance(lid_repo, NullLiderRepository)

        self.assertEqual(rep_repo.list_reportes(), ([], 0, [], []))
        self.assertEqual(est_repo.list_redes(), [])
        self.assertEqual(est_repo.list_casas_de_paz(), ([], []))
        self.assertEqual(usr_repo.list_usuarios(), ([], 0, 0))
        self.assertIsNone(usr_repo.get_by_id('missing'))
        self.assertEqual(lid_repo.list_lideres(), ([], 0, [], []))

    def test_mock_adapters_filter_data_correctly(self):
        est_repo = MockEstructuraRepository()
        redes = est_repo.list_redes()
        self.assertGreater(len(redes), 0)
        redes_scoped = est_repo.list_redes(supervisor_red_id=redes[0]['id'])
        self.assertEqual(len(redes_scoped), 1)

        usr_repo = MockUsuarioRepository()
        usuarios, total, _ = usr_repo.list_usuarios(rol='admin', page=1, per_page=5)
        self.assertGreater(total, 0)
        self.assertTrue(all(u['rol'] == 'admin' for u in usuarios))


if __name__ == '__main__':
    unittest.main()
