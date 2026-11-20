"""
routes/api/reportes_api.py - Endpoints REST para consulta y gestión de reportes ministeriales.
"""
from flask import request, jsonify, session
from database import get_db_connection
from services.dashboard_service import get_supervisor_red_id, mock_mode_enabled
from services.cdp_service import (
    process_reporte,
    actualizar_reporte,
    eliminar_reporte,
    get_cdp_datos_usuario,
    get_cdp_detalle,
)
from repositories import get_reporte_repository, unit_of_work
from repositories.mock_repositories import NullReporteRepository
from utils.auth import api_auth_required
from policies.access_policy import AccessPolicy, UserContext
from schemas import parse_payload, ReporteCreateDTO, ReporteUpdateDTO
from .base import api_bp, _serialize_item


def _build_user_context() -> UserContext:
    usuario_id = str(session.get("usuario_id") or "")
    rol = str(session.get("rol") or "")
    sup_red_id = get_supervisor_red_id(usuario_id) if rol == 'supervisor' else None
    cdp_id = None
    if rol in ('lider_cdp', 'cdp'):
        cdp, _ = get_cdp_datos_usuario(usuario_id)
        cdp_id = cdp['id'] if cdp else None
    return UserContext(
        usuario_id=usuario_id,
        rol=rol,
        supervisor_red_id=sup_red_id,
        cdp_id=cdp_id,
    )


@api_bp.route('/reportes', methods=['GET'])
@api_auth_required
def api_get_reportes():
    """Listado paginado y filtrado de reportes con aislamiento defensivo por rol."""
    search = request.args.get('q', '').strip()
    fecha_desde = request.args.get('fecha_desde', '').strip()
    fecha_hasta = request.args.get('fecha_hasta', '').strip()
    page = max(request.args.get('page', 1, type=int), 1)
    per_page = min(max(request.args.get('per_page', 10, type=int), 1), 100)

    red_id_arg = request.args.get('red_id', '').strip()
    cdp_id_arg = request.args.get('cdp_id', '').strip()

    user_ctx = _build_user_context()
    scope = AccessPolicy.resolve_reportes_scope(
        user_ctx,
        requested_red_id=red_id_arg,
        requested_cdp_id=cdp_id_arg,
    )
    if scope['empty']:
        return jsonify({"reportes": [], "total": 0, "page": page, "pages": 1, "per_page": per_page}), 200

    supervisor_red_id = scope['supervisor_red_id']
    target_red_id = scope['target_red_id']
    target_cdp_id = scope['target_cdp_id']

    repo = get_reporte_repository()
    if isinstance(repo, NullReporteRepository):
        return jsonify({
            "success": False,
            "error": "Base de datos temporalmente no disponible. Intente nuevamente en unos segundos.",
            "code": "db_unavailable",
        }), 503
    reportes, total, _, _ = repo.list_reportes(
        search=search,
        red_id=target_red_id,
        cdp_id=target_cdp_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        supervisor_red_id=supervisor_red_id,
        page=page,
        per_page=per_page,
    )
    total_pages = max((total + per_page - 1) // per_page, 1) if total else 1
    return jsonify({
        "reportes": _serialize_item(reportes),
        "total": total,
        "page": page,
        "pages": total_pages,
        "per_page": per_page,
    }), 200


@api_bp.route('/reportes', methods=['POST'])
@api_auth_required
def api_crear_reporte():
    """Registro de reporte con cálculo automático y validación ministerial."""
    raw_data = request.get_json(silent=True) or request.form.to_dict() or {}
    dto = parse_payload(ReporteCreateDTO, raw_data)
    data = dto.to_service_dict()
    user_ctx = _build_user_context()
    cdp_id = AccessPolicy.resolve_reporte_mutation_cdp_id(
        user_ctx,
        requested_cdp_id=dto.cdp_id,
        allow_supervisor=False,
    )

    res = process_reporte(cdp_id=cdp_id, form_data=data)
    exito = res[0] if isinstance(res, (tuple, list)) else bool(res)
    mensaje = res[1] if isinstance(res, (tuple, list)) and len(res) > 1 else (
        'Reporte guardado exitosamente.' if exito else 'Error al procesar el reporte.'
    )

    if exito:
        return jsonify({"success": True, "message": mensaje, "cdp_id": cdp_id}), 201
    return jsonify({"success": False, "error": mensaje}), 400


def _resolve_target_cdp_red_id(user_ctx: UserContext, requested_cdp_id):
    """Resuelve la red a la que pertenece la CDP objetivo cuando un supervisor realiza una mutación."""
    if not user_ctx.is_supervisor or requested_cdp_id is None or str(requested_cdp_id).strip() == '':
        return None
    try:
        cdp_id_int = int(requested_cdp_id)
    except (ValueError, TypeError):
        return None
    cdp_info = get_cdp_detalle(cdp_id_int)
    return cdp_info.get('red_id') if cdp_info else None


def _resolve_reporte_cdp_id(reporte_id):
    """Consulta en BD el cdp_id real del reporte cuando un administrador omite cdp_id."""
    if not reporte_id:
        return None
    try:
        with unit_of_work(conn_provider=get_db_connection, transactional=False) as uow:
            if uow is None:
                return None
            with uow.cursor() as cur:
                cur.execute("SELECT cdp_id FROM reporte WHERE id = %s LIMIT 1", (reporte_id,))
                row = cur.fetchone()
                return row['cdp_id'] if row and row.get('cdp_id') is not None else None
    except Exception:
        return None


@api_bp.route('/reportes/<string:reporte_id>', methods=['PUT', 'POST'])
@api_auth_required
def api_actualizar_reporte(reporte_id):
    """Actualización de un reporte existente perteneciente a la Casa de Paz."""
    raw_data = request.get_json(silent=True) or request.form.to_dict() or {}
    dto = parse_payload(ReporteUpdateDTO, raw_data)
    data = dto.to_service_dict()
    user_ctx = _build_user_context()
    req_cdp_id = dto.cdp_id
    if user_ctx.is_admin and (req_cdp_id is None or str(req_cdp_id).strip() == ''):
        req_cdp_id = _resolve_reporte_cdp_id(reporte_id)
    target_cdp_red_id = _resolve_target_cdp_red_id(user_ctx, req_cdp_id)
    cdp_id = AccessPolicy.resolve_reporte_mutation_cdp_id(
        user_ctx,
        requested_cdp_id=req_cdp_id,
        allow_supervisor=True,
        default_admin_cdp_id=1 if mock_mode_enabled() else None,
        target_cdp_red_id=target_cdp_red_id,
    )

    exito, mensaje = actualizar_reporte(reporte_id, cdp_id, data)
    if exito:
        return jsonify({"success": True, "message": mensaje}), 200
    return jsonify({"success": False, "error": mensaje}), 400


@api_bp.route('/reportes/<string:reporte_id>', methods=['DELETE'])
@api_auth_required
def api_eliminar_reporte(reporte_id):
    """Eliminación segura de reporte con control de permisos."""
    user_ctx = _build_user_context()
    req_cdp_id = request.args.get('cdp_id', type=int)
    if user_ctx.is_admin and req_cdp_id is None:
        req_cdp_id = _resolve_reporte_cdp_id(reporte_id)
    target_cdp_red_id = _resolve_target_cdp_red_id(user_ctx, req_cdp_id)
    cdp_id = AccessPolicy.resolve_reporte_mutation_cdp_id(
        user_ctx,
        requested_cdp_id=req_cdp_id,
        allow_supervisor=True,
        default_admin_cdp_id=1 if mock_mode_enabled() else None,
        target_cdp_red_id=target_cdp_red_id,
    )

    exito, mensaje = eliminar_reporte(reporte_id, cdp_id)
    if exito:
        return jsonify({"success": True, "message": mensaje}), 200
    return jsonify({"success": False, "error": mensaje}), 400
