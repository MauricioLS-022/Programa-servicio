"""
tests/test_sql_integration_and_concurrency.py - Pruebas de concurrencia del pool LifoQueue,
atomicidad/rollback de unit_of_work y suite opt-in de integración SQL real contra MySQL.
"""
import os
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock, patch
from app import app
import database
from repositories import unit_of_work
from services.report_service import process_reporte


class _FakeThreadSafeConn:
    """Conexión simulada thread-safe para probar concurrencia del pool LifoQueue."""
    def __init__(self, conn_id: int, fail_rollback: bool = False):
        self.conn_id = conn_id
        self.open = True
        self.pings = 0
        self.rollbacks = 0
        self.closed = False
        self.fail_rollback = fail_rollback

    def ping(self, reconnect=True):
        self.pings += 1
        if not self.open:
            raise RuntimeError("Conexión cerrada")

    def rollback(self):
        self.rollbacks += 1
        if self.fail_rollback:
            raise RuntimeError("Rollback failed")

    def close(self):
        self.open = False
        self.closed = True


class TestPoolAndUowConcurrency(unittest.TestCase):
    """Pruebas siempre activas de concurrencia en database._pool y rollback en unit_of_work."""

    def setUp(self):
        self._orig_mock = app.config.get('MOCK_MODE', False)
        app.config['TESTING'] = True
        app.config['MOCK_MODE'] = False
        database.reset_circuit_breaker()

    def tearDown(self):
        database.reset_circuit_breaker()
        app.config['MOCK_MODE'] = self._orig_mock

    def test_pool_concurrent_borrow_and_return_without_race_or_leaks(self):
        """Múltiples hilos tomando y devolviendo conexiones al pool LifoQueue no pierden conexiones ni fallan."""
        counter_lock = threading.Lock()
        created = []

        def fake_create():
            with counter_lock:
                c = _FakeThreadSafeConn(len(created) + 1)
                created.append(c)
                return c

        errors = []

        def worker():
            try:
                with app.test_request_context('/api/health'):
                    conn = database.get_db_connection()
                    self.assertIsNotNone(conn)
                    # Misma petición debe reutilizar el mismo wrapper scoped
                    conn2 = database.get_db_connection()
                    self.assertIs(conn, conn2)
            except Exception as exc:
                errors.append(exc)

        with patch('database._create_raw_connection', side_effect=fake_create):
            with ThreadPoolExecutor(max_workers=10) as pool:
                futures = [pool.submit(worker) for _ in range(30)]
                for f in futures:
                    f.result()

        self.assertEqual(errors, [])
        self.assertGreater(len(created), 0)
        self.assertTrue(any(c.rollbacks > 0 for c in created))
        # El pool nunca excede _MAX_POOL_SIZE y todas las conexiones devueltas ejecutaron rollback()
        self.assertLessEqual(database._pool.qsize(), database._MAX_POOL_SIZE)
        self.assertTrue(all(c.rollbacks >= 1 for c in created))
        database.reset_circuit_breaker()
        self.assertEqual(database._pool.qsize(), 0)
        self.assertTrue(all(c.closed for c in created))

    def test_close_db_connection_rolls_back_and_discards_on_error(self):
        """close_db_connection() ejecuta rollback() antes de devolver al pool y descarta si falla."""
        healthy = _FakeThreadSafeConn(1, fail_rollback=False)
        broken = _FakeThreadSafeConn(2, fail_rollback=True)

        with patch('database._create_raw_connection', return_value=healthy):
            with app.test_request_context('/api/health'):
                _ = database.get_db_connection()
        self.assertEqual(healthy.rollbacks, 1)
        self.assertFalse(healthy.closed)
        self.assertEqual(database._pool.qsize(), 1)

        database.reset_circuit_breaker()

        with patch('database._create_raw_connection', return_value=broken):
            with app.test_request_context('/api/health'):
                _ = database.get_db_connection()
        self.assertEqual(broken.rollbacks, 1)
        self.assertTrue(broken.closed)
        self.assertEqual(database._pool.qsize(), 0)

    def test_unit_of_work_rolls_back_on_duplicate_or_sql_exception(self):
        """process_reporte ejecuta rollback y cierra conexión ante duplicado uq_cdp_fecha o fallo SQL."""
        valid_form = {
            'fecha': '2026-10-21',
            'hr_inicio': '18:00',
            'hr_fin': '19:30',
            'tema': 'La Fe',
            'nro_regulares': '10',
            'nro_ninos': '2',
            'nro_visitas': '1',
            'nro_comprometidos': '2',
            'ofrendas_usd': '15.0',
            'ofrendas_bs': '500.0',
            'cesta_amor': '1',
        }

        # Caso 1: Reporte ya existente para (cdp_id, fecha) -> rollback sin insertar
        dup_conn = MagicMock()
        dup_cur = MagicMock()
        dup_cur.fetchone.return_value = {'id': 'existing-uuid'}
        dup_conn.cursor.return_value.__enter__.return_value = dup_cur
        mock_queries = MagicMock()

        ok, msg = process_reporte(1, valid_form, _conn_provider=lambda: dup_conn, _db_queries=mock_queries)
        self.assertFalse(ok)
        self.assertIn('Ya existe un reporte', msg)
        mock_queries.insertar_reporte.assert_not_called()
        dup_conn.rollback.assert_called()
        dup_conn.close.assert_called_once()

        # Caso 2: Error SQL durante insertar_reporte -> rollback automático vía unit_of_work
        err_conn = MagicMock()
        err_cur = MagicMock()
        err_cur.fetchone.return_value = None
        err_conn.cursor.return_value.__enter__.return_value = err_cur
        mock_queries_err = MagicMock()
        mock_queries_err.insertar_reporte.side_effect = RuntimeError("Duplicate entry for key 'uq_cdp_fecha'")

        ok2, msg2 = process_reporte(1, valid_form, _conn_provider=lambda: err_conn, _db_queries=mock_queries_err)
        self.assertFalse(ok2)
        self.assertIn('Error al guardar', msg2)
        err_conn.commit.assert_not_called()
        err_conn.rollback.assert_called_once()
        err_conn.close.assert_called_once()

    def test_unit_of_work_concurrent_transactions_isolated(self):
        """Múltiples transacciones unit_of_work concurrentes hacen commit/rollback de forma aislada."""
        def run_tx(should_fail: bool):
            conn = MagicMock()
            if should_fail:
                try:
                    with unit_of_work(conn_provider=lambda: conn, transactional=True) as uow:
                        uow.cursor()
                        raise ValueError("fail")
                except ValueError:
                    pass
                return (conn.commit.call_count, conn.rollback.call_count, conn.close.call_count)
            with unit_of_work(conn_provider=lambda: conn, transactional=True) as uow:
                uow.cursor()
            return (conn.commit.call_count, conn.rollback.call_count, conn.close.call_count)

        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(run_tx, [i % 2 == 0 for i in range(20)]))

        for i, (commits, rollbacks, closes) in enumerate(results):
            self.assertEqual(closes, 1)
            if i % 2 == 0:
                self.assertEqual((commits, rollbacks), (0, 1))
            else:
                self.assertEqual((commits, rollbacks), (1, 0))


@unittest.skipUnless(
    os.getenv('RUN_DB_INTEGRATION_TESTS') == '1',
    "Suite SQL real desactivada por defecto. Defina RUN_DB_INTEGRATION_TESTS=1 con una BD MySQL de pruebas.",
)
class TestMySQLRealIntegration(unittest.TestCase):
    """
    Suite opt-in contra MySQL real para validar sintaxis SQL, ONLY_FULL_GROUP_BY,
    restricción uq_cdp_fecha y consultas reales en services/queries/.
    """

    def setUp(self):
        self._orig_mock = app.config.get('MOCK_MODE', False)
        app.config['MOCK_MODE'] = False
        database.reset_circuit_breaker()
        with app.app_context():
            self.conn = database.get_db_connection()
        if not self.conn:
            self.skipTest("No se pudo conectar a MySQL de pruebas.")

    def tearDown(self):
        if getattr(self, 'conn', None):
            try:
                self.conn.rollback()
                self.conn.close()
            except Exception:
                pass
        app.config['MOCK_MODE'] = self._orig_mock
        database.reset_circuit_breaker()

    def test_real_mysql_queries_compatible_with_only_full_group_by(self):
        """Valida consultas críticas de estructura y métricas bajo ONLY_FULL_GROUP_BY real."""
        from services.queries.estructura_queries import listar_redes_con_supervisor, listar_casas_de_paz_filtradas

        with self.conn.cursor() as cur:
            cur.execute("SELECT @@sql_mode AS mode")
            _ = cur.fetchone()
            redes = listar_redes_con_supervisor(cur)
            casas = listar_casas_de_paz_filtradas(cur)
            self.assertIsInstance(redes, list)
            self.assertIsInstance(casas, list)

    def test_real_mysql_schema_has_uq_cdp_fecha_constraint(self):
        """Verifica que la BD cumple todas las restricciones canónicas (uq_cdp_fecha, FKs y cdp.usuario_id NULL)."""
        with self.conn.cursor() as cur:
            cur.execute("SHOW INDEX FROM reporte WHERE Key_name = 'uq_cdp_fecha'")
            indexes = cur.fetchall()
            self.assertGreaterEqual(len(indexes), 2)

            cur.execute(
                """
                SELECT IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'cdp' AND COLUMN_NAME = 'usuario_id'
                """
            )
            col = cur.fetchone()
            self.assertIsNotNone(col)
            self.assertEqual(col['IS_NULLABLE'], 'YES')

            cur.execute(
                """
                SELECT CONSTRAINT_NAME, DELETE_RULE
                FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS
                WHERE CONSTRAINT_SCHEMA = DATABASE()
                  AND CONSTRAINT_NAME IN ('fk_cdp_usuario', 'fk_reporte_cdp')
                """
            )
            rules = {r['CONSTRAINT_NAME']: r['DELETE_RULE'] for r in cur.fetchall()}
            self.assertEqual(rules.get('fk_cdp_usuario'), 'SET NULL')
            self.assertEqual(rules.get('fk_reporte_cdp'), 'RESTRICT')

    def test_real_mysql_crud_roundtrip_and_immediate_visibility_across_pool_connections(self):
        """Valida ciclo CRUD real (crear -> leer -> actualizar -> verificar desde otra conexión -> limpiar)."""
        import uuid
        from services.red_service import crear_red_servicio, actualizar_red_servicio, eliminar_red_servicio

        nombre_inicial = f"Red Test Integracion {uuid.uuid4().hex[:8]}"
        nombre_editado = f"{nombre_inicial} Editada"
        red_id = None

        try:
            with app.test_request_context('/api/redes'):
                ok_create, msg_create = crear_red_servicio({'nombre': nombre_inicial, 'supervisor_id': ''})
                self.assertTrue(ok_create, msg_create)

            # Leer desde una nueva conexión del pool (verifica rollback() limpio sin snapshot viejo)
            with app.test_request_context('/api/redes'):
                conn_read = database.get_db_connection()
                self.assertIsNotNone(conn_read)
                with conn_read.cursor() as cur:
                    cur.execute("SELECT id, nombre FROM red WHERE nombre = %s", (nombre_inicial,))
                    row = cur.fetchone()
                    self.assertIsNotNone(row)
                    red_id = row['id']

            with app.test_request_context(f'/api/redes/{red_id}'):
                ok_upd, msg_upd = actualizar_red_servicio(red_id, {'nombre': nombre_editado, 'supervisor_id': ''})
                self.assertTrue(ok_upd, msg_upd)

            # Verificar visibilidad inmediata del cambio desde otra petición/conexión
            with app.test_request_context('/api/redes'):
                conn_verify = database.get_db_connection()
                self.assertIsNotNone(conn_verify)
                with conn_verify.cursor() as cur:
                    cur.execute("SELECT nombre FROM red WHERE id = %s", (red_id,))
                    row2 = cur.fetchone()
                    self.assertIsNotNone(row2)
                    self.assertEqual(row2['nombre'], nombre_editado)
        finally:
            if red_id is not None:
                with app.test_request_context(f'/api/redes/{red_id}'):
                    eliminar_red_servicio(red_id)


if __name__ == '__main__':
    unittest.main()
