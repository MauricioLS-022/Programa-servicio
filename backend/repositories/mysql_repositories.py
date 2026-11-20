"""
Adaptadores MySQL para los protocolos de repositorio.
Delegan en services.queries.* manteniendo la gestión de cierre seguro de conexión.
"""
import logging
from typing import Any, Optional
import db_queries
from services.queries.estructura_queries import (
    listar_redes_con_supervisor,
    listar_casas_de_paz_filtradas,
)

logger = logging.getLogger(__name__)


class MySQLReporteRepository:
    def __init__(self, conn):
        self._conn = conn

    def list_reportes(
        self,
        *,
        search: str = '',
        red_id: str = '',
        cdp_id: str = '',
        fecha_desde: str = '',
        fecha_hasta: str = '',
        supervisor_red_id: Optional[int] = None,
        page: int = 1,
        per_page: int = 10,
    ) -> tuple[list[dict[str, Any]], int, list[dict[str, Any]], list[dict[str, Any]]]:
        try:
            return db_queries.get_reportes(
                self._conn,
                search=search,
                red_id=red_id,
                cdp_id=cdp_id,
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                supervisor_red_id=supervisor_red_id,
                page=page,
                per_page=per_page,
            )
        finally:
            self._conn.close()


class MySQLEstructuraRepository:
    def __init__(self, conn):
        self._conn = conn

    def list_redes(self, *, supervisor_red_id: Optional[int] = None) -> list[dict[str, Any]]:
        try:
            with self._conn.cursor() as cur:
                return listar_redes_con_supervisor(cur, supervisor_red_id=supervisor_red_id)
        finally:
            self._conn.close()

    def list_all_redes_select(self) -> list[dict[str, Any]]:
        try:
            with self._conn.cursor() as cur:
                return db_queries.get_todas_las_redes(cur)
        finally:
            self._conn.close()

    def list_casas_de_paz(
        self,
        *,
        red_id: str = '',
        search: str = '',
        filtro: str = '',
    ) -> tuple[list[dict[str, Any]], list[int]]:
        from services.cdp_service import get_casas_sin_reporte_7d

        try:
            with self._conn.cursor() as cur:
                casas = listar_casas_de_paz_filtradas(
                    cur,
                    red_id=red_id,
                    search=search,
                    filtro=filtro,
                )
            try:
                raw_sin_rep = get_casas_sin_reporte_7d(int(red_id) if red_id else None) or []
                sin_rep_ids = [
                    int(item['id']) if isinstance(item, dict) and 'id' in item else int(item)
                    for item in raw_sin_rep
                ]
            except Exception as err:
                logger.warning("No se pudo calcular casas sin reporte 7d: %s", err)
                sin_rep_ids = []

            sin_rep_set = set(sin_rep_ids)
            for c in casas:
                c['sin_reporte_7d'] = bool(c.get('is_active')) and int(c['id']) in sin_rep_set

            if filtro == 'pendientes_7d':
                casas = [c for c in casas if c['sin_reporte_7d']]

            return casas, sin_rep_ids
        finally:
            self._conn.close()


class MySQLUsuarioRepository:
    def __init__(self, conn):
        self._conn = conn

    def list_usuarios(
        self,
        *,
        search: str = '',
        rol: str = '',
        page: int = 1,
        per_page: int = 5,
    ) -> tuple[list[dict[str, Any]], int, int]:
        try:
            return db_queries.get_usuarios(self._conn, search, rol, page, per_page)
        except Exception as err:
            logger.error("Error obteniendo usuarios: %s", err)
            return [], 0, 0
        finally:
            self._conn.close()

    def get_by_id(self, usuario_id: str) -> Optional[dict[str, Any]]:
        try:
            with self._conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT u.id, u.username, u.nombre, u.apellido, u.tipo_usuario, u.is_active,
                           r.id AS red_id, r.nombre AS red_nombre,
                           c.id AS cdp_id, c.codigo AS cdp_codigo
                    FROM usuario u
                    LEFT JOIN red r ON r.supervisor_id = u.id
                    LEFT JOIN cdp c ON c.usuario_id = u.id
                    WHERE u.id = %s
                    """,
                    (str(usuario_id),),
                )
                return cursor.fetchone()
        except Exception as err:
            logger.error("Error obteniendo usuario %s: %s", usuario_id, err)
            return None
        finally:
            self._conn.close()


class MySQLLiderRepository:
    def __init__(self, conn):
        self._conn = conn

    def list_lideres(
        self,
        *,
        search: str = '',
        rol: str = '',
        red_id: str = '',
        cdp_id: str = '',
        supervisor_red_id: Optional[int] = None,
        page: int = 1,
        per_page: int = 10,
    ) -> tuple[list[dict[str, Any]], int, list[dict[str, Any]], list[dict[str, Any]]]:
        try:
            return db_queries.get_lideres(
                self._conn,
                search=search,
                rol=rol,
                red_id=red_id,
                cdp_id=cdp_id,
                supervisor_red_id=supervisor_red_id,
                page=page,
                per_page=per_page,
            )
        except Exception as err:
            logger.error("Error obteniendo líderes: %s", err)
            return [], 0, [], []
        finally:
            self._conn.close()
