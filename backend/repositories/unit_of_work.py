"""
Unit of Work transaccional para PyMySQL.
Encapsula la obtención de conexión (compatible con el Circuit Breaker y pool),
commit automático al concluir sin errores, rollback ante excepciones y cierre garantizado.
"""
import logging
from contextlib import contextmanager
from typing import Callable, Iterator, Optional
from database import get_db_connection

logger = logging.getLogger(__name__)


class UnitOfWork:
    """Wrapper transaccional sobre una conexión activa de PyMySQL."""

    def __init__(self, conn, *, transactional: bool = True):
        self.conn = conn
        self.transactional = transactional
        self._committed = False
        self._rolled_back = False

    def cursor(self):
        return self.conn.cursor()

    def commit(self):
        if self.conn:
            self.conn.commit()
            self._committed = True

    def rollback(self):
        if self.conn and not self._rolled_back:
            try:
                self.conn.rollback()
            except Exception as rb_err:
                logger.warning("Error durante rollback de transacción: %s", rb_err)
            finally:
                self._rolled_back = True


@contextmanager
def unit_of_work(
    *,
    conn_provider: Callable[[], Optional[object]] = get_db_connection,
    transactional: bool = True,
) -> Iterator[Optional[UnitOfWork]]:
    """
    Context manager para operaciones de base de datos.
    Si no hay conexión disponible (p. ej. Circuit Breaker OPEN o MOCK_MODE), entrega None.
    Si hay conexión y `transactional=True`, confirma al finalizar sin errores y revierte en excepción.
    Siempre libera la conexión al pool mediante `conn.close()`.
    """
    conn = conn_provider()
    if conn is None:
        yield None
        return

    uow = UnitOfWork(conn, transactional=transactional)
    try:
        yield uow
        if transactional and not uow._committed and not uow._rolled_back:
            uow.commit()
    except Exception:
        if transactional:
            uow.rollback()
        raise
    finally:
        try:
            conn.close()
        except Exception as close_err:
            logger.warning("Error liberando conexión de BD: %s", close_err)
