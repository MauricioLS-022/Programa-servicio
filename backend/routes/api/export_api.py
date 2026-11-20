"""
routes/api/export_api.py - Endpoints REST de exportación binaria (PDF, Excel .xlsx y CSV)
con control de acceso RBAC, aislamiento territorial anti-IDOR y degradación controlada 503.
"""
import io
from flask import jsonify, request, send_file, session

from database import get_db_connection
from policies.access_policy import AccessPolicy, UserContext
from repositories import (
    get_estructura_repository,
    get_lider_repository,
    get_reporte_repository,
)
from repositories.mock_repositories import (
    NullEstructuraRepository,
    NullLiderRepository,
    NullReporteRepository,
)
from services.cdp_service import get_cdp_detalle
from services.dashboard_service import get_supervisor_red_id, mock_mode_enabled
from services.export_service import (
    MAX_EXPORT_ROWS,
    export_casas,
    export_lideres,
    export_reportes,
    export_usuarios,
)
from services.user_service import get_usuarios_context
from utils.auth import api_role_required
from .base import api_bp


def _db_unavailable_response():
    return jsonify({
        "success": False,
        "error": "Base de datos temporalmente no disponible. Intente nuevamente en unos segundos.",
        "code": "db_unavailable",
    }), 503


def _invalid_format_response(allowed: str):
    return jsonify({
        "success": False,
        "error": f"Formato de exportación no soportado. Formatos permitidos: {allowed}.",
        "code": "invalid_format",
    }), 400


def _send_binary_export(content: bytes, mimetype: str, filename: str):
    response = send_file(
        io.BytesIO(content),
        mimetype=mimetype,
        as_attachment=True,
        download_name=filename,
    )
    response.headers['Cache-Control'] = 'no-store'
    return response


def _check_supervisor_cdp_access(user_ctx: UserContext, cdp_id_arg: str):
    """Retorna None si permitido, o tupla (response, 403) si el supervisor solicita una CDP ajena."""
    if not user_ctx.is_supervisor or not cdp_id_arg:
        return None
    try:
        cdp_id_int = int(cdp_id_arg)
    except (ValueError, TypeError):
        return None
    cdp_info = get_cdp_detalle(cdp_id_int)
    if cdp_info is not None and not AccessPolicy.can_access_cdp(
        user_ctx, cdp_id_int, cdp_red_id=cdp_info.get('red_id')
    ):
        return jsonify({
            "success": False,
            "error": "No autorizado para exportar datos de una Casa de Paz fuera de su red asignada.",
            "code": "forbidden",
        }), 403
    return None


@api_bp.route('/export/reportes', methods=['GET'])
@api_role_required('admin', 'supervisor')
def api_export_reportes():
    """Exporta el consolidado completo filtrado de reportes en PDF, XLSX o CSV."""
    fmt = request.args.get('format', 'xlsx').strip().lower()
    if fmt not in ('pdf', 'xlsx', 'csv'):
        return _invalid_format_response('pdf, xlsx, csv')

    search = request.args.get('q', '').strip()
    red_id_arg = request.args.get('red_id', '').strip()
    cdp_id_arg = request.args.get('cdp_id', '').strip()
    fecha_desde = request.args.get('fecha_desde', '').strip()
    fecha_hasta = request.args.get('fecha_hasta', '').strip()

    usuario_id = str(session.get('usuario_id') or '')
    rol = str(session.get('rol') or '')
    sup_red_id = get_supervisor_red_id(usuario_id) if rol == 'supervisor' else None
    user_ctx = UserContext(usuario_id=usuario_id, rol=rol, supervisor_red_id=sup_red_id)

    scope = AccessPolicy.resolve_reportes_scope(
        user_ctx,
        requested_red_id=red_id_arg,
        requested_cdp_id=cdp_id_arg,
    )
    denied = _check_supervisor_cdp_access(user_ctx, cdp_id_arg)
    if denied is not None:
        return denied

    repo = get_reporte_repository()
    if isinstance(repo, NullReporteRepository):
        return _db_unavailable_response()

    if scope['empty']:
        reportes = []
    else:
        reportes, _, _, _ = repo.list_reportes(
            search=search,
            red_id=scope['target_red_id'],
            cdp_id=scope['target_cdp_id'],
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            supervisor_red_id=scope['supervisor_red_id'],
            page=1,
            per_page=MAX_EXPORT_ROWS,
        )

    filter_parts = []
    if search:
        filter_parts.append(f'Búsqueda="{search}"')
    if fecha_desde or fecha_hasta:
        filter_parts.append(f'Rango={fecha_desde or "..."} a {fecha_hasta or "..."}')
    if scope['target_red_id']:
        filter_parts.append(f"Red #{scope['target_red_id']}")
    if scope['target_cdp_id']:
        filter_parts.append(f"CDP #{scope['target_cdp_id']}")
    filters_summary = ', '.join(filter_parts)

    content, mimetype, filename = export_reportes(reportes, fmt, filters_summary=filters_summary)
    return _send_binary_export(content, mimetype, filename)


@api_bp.route('/export/usuarios', methods=['GET'])
@api_role_required('admin')
def api_export_usuarios():
    """Exporta el directorio completo filtrado de usuarios en XLSX o CSV (solo admin)."""
    fmt = request.args.get('format', 'xlsx').strip().lower()
    if fmt not in ('xlsx', 'csv'):
        return _invalid_format_response('xlsx, csv')

    if not mock_mode_enabled() and get_db_connection() is None:
        return _db_unavailable_response()

    search = request.args.get('q', '').strip()
    rol_filtro = request.args.get('rol', '').strip().lower()

    ctx = get_usuarios_context(search=search, rol=rol_filtro, page=1, per_page=MAX_EXPORT_ROWS)
    usuarios = ctx.get('usuarios', [])

    content, mimetype, filename = export_usuarios(usuarios, fmt)
    return _send_binary_export(content, mimetype, filename)


@api_bp.route('/export/lideres', methods=['GET'])
@api_role_required('admin', 'supervisor')
def api_export_lideres():
    """Exporta el directorio completo filtrado de líderes en XLSX o CSV."""
    fmt = request.args.get('format', 'xlsx').strip().lower()
    if fmt not in ('xlsx', 'csv'):
        return _invalid_format_response('xlsx, csv')

    search = request.args.get('q', '').strip()
    rol_filtro = request.args.get('rol', '').strip()
    red_id_arg = request.args.get('red_id', '').strip()
    cdp_id_arg = request.args.get('cdp_id', '').strip()

    usuario_id = str(session.get('usuario_id') or '')
    rol = str(session.get('rol') or '')
    supervisor_red_id = None
    target_red_id = red_id_arg

    if rol == 'supervisor':
        sup_red = get_supervisor_red_id(usuario_id)
        user_ctx = UserContext(usuario_id=usuario_id, rol=rol, supervisor_red_id=sup_red)
        if red_id_arg and not AccessPolicy.can_access_red(user_ctx, red_id_arg):
            return jsonify({
                "success": False,
                "error": "No autorizado para exportar líderes fuera de su red asignada.",
                "code": "forbidden",
            }), 403
        denied = _check_supervisor_cdp_access(user_ctx, cdp_id_arg)
        if denied is not None:
            return denied
        supervisor_red_id = sup_red
        target_red_id = str(sup_red) if sup_red else ''

    repo = get_lider_repository()
    if isinstance(repo, NullLiderRepository):
        return _db_unavailable_response()

    if rol == 'supervisor' and not supervisor_red_id:
        lideres = []
    else:
        lideres, _, _, _ = repo.list_lideres(
            search=search,
            rol=rol_filtro,
            red_id=target_red_id,
            cdp_id=cdp_id_arg,
            supervisor_red_id=supervisor_red_id,
            page=1,
            per_page=MAX_EXPORT_ROWS,
        )

    content, mimetype, filename = export_lideres(lideres, fmt)
    return _send_binary_export(content, mimetype, filename)


@api_bp.route('/export/casas_de_paz', methods=['GET'])
@api_role_required('admin', 'supervisor')
def api_export_casas_de_paz():
    """Exporta el listado completo filtrado de Casas de Paz en XLSX o CSV."""
    fmt = request.args.get('format', 'xlsx').strip().lower()
    if fmt not in ('xlsx', 'csv'):
        return _invalid_format_response('xlsx, csv')

    red_id_arg = request.args.get('red_id', '').strip()
    search = request.args.get('q', '').strip()
    filtro = request.args.get('filtro', '').strip().lower()

    usuario_id = str(session.get('usuario_id') or '')
    rol = str(session.get('rol') or '')
    target_red_id = red_id_arg

    if rol == 'supervisor':
        sup_red = get_supervisor_red_id(usuario_id)
        user_ctx = UserContext(usuario_id=usuario_id, rol=rol, supervisor_red_id=sup_red)
        if red_id_arg and not AccessPolicy.can_access_red(user_ctx, red_id_arg):
            return jsonify({
                "success": False,
                "error": "No autorizado para exportar Casas de Paz fuera de su red asignada.",
                "code": "forbidden",
            }), 403
        target_red_id = str(sup_red) if sup_red else ''

    repo = get_estructura_repository()
    if isinstance(repo, NullEstructuraRepository):
        return _db_unavailable_response()

    if rol == 'supervisor' and not target_red_id:
        casas = []
    else:
        casas, sin_rep_ids = repo.list_casas_de_paz(
            red_id=target_red_id,
            search=search,
            filtro=filtro,
        )
        sin_rep_set = {str(cid) for cid in (sin_rep_ids or [])}
        for c in casas:
            if 'sin_reporte_7d' not in c:
                c['sin_reporte_7d'] = str(c.get('id')) in sin_rep_set

    content, mimetype, filename = export_casas(casas, fmt)
    return _send_binary_export(content, mimetype, filename)
