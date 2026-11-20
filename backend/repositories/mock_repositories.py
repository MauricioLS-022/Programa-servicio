"""
Adaptadores Mock y Null para los protocolos de repositorio.
Encapsulan el filtrado en memoria sobre mock_data.py eliminando duplicación en servicios y rutas.
"""
from typing import Any, Optional
from mock_data import (
    get_mock_reportes,
    get_redes_demo,
    get_casas_demo,
    get_mock_usuarios,
    get_mock_lideres,
)


class MockReporteRepository:
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
        reportes = list(get_mock_reportes())
        if supervisor_red_id is not None:
            reportes = [r for r in reportes if str(r.get('red_id', '')) == str(supervisor_red_id)]
        if red_id:
            reportes = [r for r in reportes if str(r.get('red_id', '')) == str(red_id)]
        if cdp_id:
            reportes = [r for r in reportes if str(r.get('cdp_id', '')) == str(cdp_id)]
        if search:
            q = search.lower()
            reportes = [
                r for r in reportes
                if q in f"{r.get('tema', '')} {r.get('cdp_codigo', '')} {r.get('lider_nombre', '')}".lower()
            ]
        total = len(reportes)
        redes = get_redes_demo()
        casas = get_casas_demo()
        return reportes, total, redes, casas


class NullReporteRepository:
    def list_reportes(self, **kwargs):
        return [], 0, [], []


class MockEstructuraRepository:
    def list_redes(self, *, supervisor_red_id: Optional[int] = None) -> list[dict[str, Any]]:
        redes = list(get_redes_demo())
        if supervisor_red_id is not None:
            redes = [r for r in redes if str(r.get('id')) == str(supervisor_red_id)]
        return redes

    def list_all_redes_select(self) -> list[dict[str, Any]]:
        return list(get_redes_demo())

    def list_casas_de_paz(
        self,
        *,
        red_id: str = '',
        search: str = '',
        filtro: str = '',
    ) -> tuple[list[dict[str, Any]], list[int]]:
        casas = [dict(c) for c in get_casas_demo()]
        if red_id:
            casas = [c for c in casas if str(c.get('red_id', '')) == str(red_id)]
        if search:
            q = search.lower()
            casas = [
                c for c in casas
                if q in f"{c.get('codigo', '')} {c.get('anfitrion', '')} {c.get('direccion', '')}".lower()
            ]
        if filtro == 'activas':
            casas = [c for c in casas if bool(c.get('is_active', 1))]
        elif filtro == 'pausadas':
            casas = [c for c in casas if not bool(c.get('is_active', 1))]

        sin_rep_ids = [c['id'] for c in casas if not c.get('tiene_reporte_7d', True)]
        for c in casas:
            c['sin_reporte_7d'] = c['id'] in sin_rep_ids

        if filtro == 'pendientes_7d':
            casas = [c for c in casas if c['id'] in sin_rep_ids]

        return casas, sin_rep_ids


class NullEstructuraRepository:
    def list_redes(self, *, supervisor_red_id: Optional[int] = None) -> list[dict[str, Any]]:
        return []

    def list_all_redes_select(self) -> list[dict[str, Any]]:
        return []

    def list_casas_de_paz(self, **kwargs) -> tuple[list[dict[str, Any]], list[int]]:
        return [], []


class MockUsuarioRepository:
    def list_usuarios(
        self,
        *,
        search: str = '',
        rol: str = '',
        page: int = 1,
        per_page: int = 5,
    ) -> tuple[list[dict[str, Any]], int, int]:
        usuarios = [dict(u) for u in get_mock_usuarios()]
        redes = get_redes_demo()
        casas = get_casas_demo()
        for u in usuarios:
            red_asig = next((r for r in redes if str(r.get('supervisor_id')) == str(u.get('id'))), None)
            u['red_nombre'] = red_asig['nombre'] if red_asig else None
            cdp_asig = next(
                (
                    c for c in casas
                    if str(c.get('lider_id')) == str(u.get('id')) or str(c.get('usuario_id')) == str(u.get('id'))
                ),
                None,
            )
            u['cdp_codigo'] = cdp_asig['codigo'] if cdp_asig else None
        if search:
            q = search.lower()
            usuarios = [
                u for u in usuarios
                if q in f"{u['nombre']} {u['apellido']} {u['username']}".lower()
            ]
        if rol:
            usuarios = [u for u in usuarios if u['rol'] == rol]
        total = len(usuarios)
        total_activos = sum(u['is_active'] for u in usuarios)
        start = (page - 1) * per_page
        return usuarios[start:start + per_page], total, total_activos

    def get_by_id(self, usuario_id: str) -> Optional[dict[str, Any]]:
        usuarios = get_mock_usuarios()
        u = next((item for item in usuarios if str(item.get('id')) == str(usuario_id)), None)
        if not u:
            return None
        u_data = dict(u)
        u_data['tipo_usuario'] = u_data.get('rol', u_data.get('tipo_usuario', 'admin'))
        redes = get_redes_demo()
        red_asig = next((r for r in redes if str(r.get('supervisor_id')) == str(usuario_id)), None)
        u_data['red_id'] = red_asig['id'] if red_asig else None
        u_data['red_nombre'] = red_asig['nombre'] if red_asig else None
        casas = get_casas_demo()
        cdp_asig = next((c for c in casas if str(c.get('lider_id')) == str(usuario_id)), None)
        u_data['cdp_id'] = cdp_asig['id'] if cdp_asig else None
        u_data['cdp_codigo'] = cdp_asig['codigo'] if cdp_asig else None
        return u_data


class NullUsuarioRepository:
    def list_usuarios(self, **kwargs):
        return [], 0, 0

    def get_by_id(self, usuario_id: str):
        return None


class MockLiderRepository:
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
        lideres = list(get_mock_lideres())
        if supervisor_red_id is not None:
            lideres = [l for l in lideres if str(l.get('red_id')) == str(supervisor_red_id)]
        if search:
            q = search.lower()
            lideres = [
                l for l in lideres
                if q in f"{l.get('nombre', '')} {l.get('apellido', '')} {l.get('telefono', '')}".lower()
            ]
        if rol:
            lideres = [l for l in lideres if l.get('rol') == rol]
        if red_id:
            lideres = [l for l in lideres if str(l.get('red_id', '')) == str(red_id)]
        if cdp_id:
            lideres = [l for l in lideres if str(l.get('cdp_id', '')) == str(cdp_id)]
        total = len(lideres)
        redes = get_redes_demo()
        casas = get_casas_demo()
        start = (page - 1) * per_page
        return lideres[start:start + per_page], total, redes, casas


class NullLiderRepository:
    def list_lideres(self, **kwargs):
        return [], 0, [], []
