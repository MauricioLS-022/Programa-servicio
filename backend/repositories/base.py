"""
Protocolos (interfaces) de repositorio y fábrica de adaptadores (MySQL vs Mock vs Null).
Desacopla los servicios y endpoints de las ramificaciones condicionales `if conn: ... elif mock_mode`.
"""
from typing import Any, Callable, Optional, Protocol
from database import get_db_connection
from services.dashboard_service import mock_mode_enabled


class ReporteRepository(Protocol):
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
    ) -> tuple[list[dict[str, Any]], int, list[dict[str, Any]], list[dict[str, Any]]]: ...


class EstructuraRepository(Protocol):
    def list_redes(self, *, supervisor_red_id: Optional[int] = None) -> list[dict[str, Any]]: ...
    def list_all_redes_select(self) -> list[dict[str, Any]]: ...
    def list_casas_de_paz(
        self,
        *,
        red_id: str = '',
        search: str = '',
        filtro: str = '',
    ) -> tuple[list[dict[str, Any]], list[int]]: ...


class UsuarioRepository(Protocol):
    def list_usuarios(
        self,
        *,
        search: str = '',
        rol: str = '',
        page: int = 1,
        per_page: int = 5,
    ) -> tuple[list[dict[str, Any]], int, int]: ...

    def get_by_id(self, usuario_id: str) -> Optional[dict[str, Any]]: ...


class LiderRepository(Protocol):
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
    ) -> tuple[list[dict[str, Any]], int, list[dict[str, Any]], list[dict[str, Any]]]: ...


def _resolve_adapter(
    mysql_cls,
    mock_cls,
    null_cls,
    *,
    conn_provider: Callable[[], Optional[object]] = get_db_connection,
    mock_checker: Callable[[], bool] = mock_mode_enabled,
    allow_mock_fallback_without_flag: bool = False,
):
    conn = conn_provider()
    if conn is not None:
        return mysql_cls(conn)
    if mock_checker() or allow_mock_fallback_without_flag:
        return mock_cls()
    return null_cls()


def get_reporte_repository(
    *,
    conn_provider: Callable[[], Optional[object]] = get_db_connection,
    mock_checker: Callable[[], bool] = mock_mode_enabled,
    allow_mock_fallback_without_flag: bool = False,
) -> ReporteRepository:
    from .mysql_repositories import MySQLReporteRepository
    from .mock_repositories import MockReporteRepository, NullReporteRepository
    return _resolve_adapter(
        MySQLReporteRepository,
        MockReporteRepository,
        NullReporteRepository,
        conn_provider=conn_provider,
        mock_checker=mock_checker,
        allow_mock_fallback_without_flag=allow_mock_fallback_without_flag,
    )


def get_estructura_repository(
    *,
    conn_provider: Callable[[], Optional[object]] = get_db_connection,
    mock_checker: Callable[[], bool] = mock_mode_enabled,
    allow_mock_fallback_without_flag: bool = False,
) -> EstructuraRepository:
    from .mysql_repositories import MySQLEstructuraRepository
    from .mock_repositories import MockEstructuraRepository, NullEstructuraRepository
    return _resolve_adapter(
        MySQLEstructuraRepository,
        MockEstructuraRepository,
        NullEstructuraRepository,
        conn_provider=conn_provider,
        mock_checker=mock_checker,
        allow_mock_fallback_without_flag=allow_mock_fallback_without_flag,
    )


def get_usuario_repository(
    *,
    conn_provider: Callable[[], Optional[object]] = get_db_connection,
    mock_checker: Callable[[], bool] = mock_mode_enabled,
) -> UsuarioRepository:
    from .mysql_repositories import MySQLUsuarioRepository
    from .mock_repositories import MockUsuarioRepository, NullUsuarioRepository
    return _resolve_adapter(
        MySQLUsuarioRepository,
        MockUsuarioRepository,
        NullUsuarioRepository,
        conn_provider=conn_provider,
        mock_checker=mock_checker,
    )


def get_lider_repository(
    *,
    conn_provider: Callable[[], Optional[object]] = get_db_connection,
    mock_checker: Callable[[], bool] = mock_mode_enabled,
    allow_mock_fallback_without_flag: bool = False,
) -> LiderRepository:
    from .mysql_repositories import MySQLLiderRepository
    from .mock_repositories import MockLiderRepository, NullLiderRepository
    return _resolve_adapter(
        MySQLLiderRepository,
        MockLiderRepository,
        NullLiderRepository,
        conn_provider=conn_provider,
        mock_checker=mock_checker,
        allow_mock_fallback_without_flag=allow_mock_fallback_without_flag,
    )
