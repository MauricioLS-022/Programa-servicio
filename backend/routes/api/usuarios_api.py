"""
routes/api/usuarios_api.py - Endpoints REST para gestión administrativa de usuarios y candados de seguridad.
"""
from flask import request, jsonify, session
from services.user_service import (
    get_usuarios_context,
    obtener_usuario_por_id,
    actualizar_usuario_admin,
    toggle_usuario_servicio,
    eliminar_usuario_servicio
)
from services.leader_service import (
    crear_nuevo_usuario,
    get_opciones_asignacion
)
from .base import api_bp, _serialize_item


@api_bp.route('/usuarios', methods=['GET'])
def api_get_usuarios():
    """Listado paginado de usuarios con estadísticas y filtros."""
    usuario_id = session.get("usuario_id")
    rol = session.get("rol")
    if not usuario_id:
        return jsonify({"error": "No autenticado"}), 401
    if rol != 'admin':
        return jsonify({"error": "Acceso restringido a administradores"}), 403

    search = request.args.get('q', '').strip()
    rol_filtro = request.args.get('rol', '').strip().lower()
    page = max(request.args.get('page', 1, type=int), 1)
    per_page = min(max(request.args.get('per_page', 10, type=int), 1), 100)

    context = get_usuarios_context(search=search, rol=rol_filtro, page=page, per_page=per_page)

    return jsonify({
        "usuarios": _serialize_item(context.get('usuarios', [])),
        "total": context.get('total_usuarios', 0),
        "total_activos": context.get('total_activos', 0),
        "page": context.get('page', 1),
        "pages": context.get('pages', 1),
        "per_page": per_page
    }), 200


@api_bp.route('/usuarios/<string:usuario_id>', methods=['GET'])
def api_get_usuario_detalle(usuario_id):
    """Consulta los datos de un usuario por su UUID."""
    if not session.get("usuario_id"):
        return jsonify({"error": "No autenticado"}), 401
    if session.get("rol") != 'admin':
        return jsonify({"error": "Acceso restringido a administradores"}), 403

    usuario = obtener_usuario_por_id(usuario_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({"usuario": _serialize_item(usuario)}), 200


@api_bp.route('/usuarios', methods=['POST'])
def api_crear_usuario():
    """Creación de un nuevo usuario con validaciones de seguridad."""
    if not session.get("usuario_id"):
        return jsonify({"error": "No autenticado"}), 401
    if session.get("rol") != 'admin':
        return jsonify({"error": "Acceso restringido a administradores"}), 403

    data = request.get_json(silent=True) or request.form.to_dict() or {}
    ok, mensaje = crear_nuevo_usuario(data)
    if ok:
        return jsonify({"success": True, "message": mensaje}), 201
    return jsonify({"success": False, "error": mensaje}), 400


@api_bp.route('/usuarios/<string:usuario_id>', methods=['PUT', 'POST'])
def api_editar_usuario(usuario_id):
    """Edición de datos y asignaciones de un usuario existente."""
    if not session.get("usuario_id"):
        return jsonify({"error": "No autenticado"}), 401
    if session.get("rol") != 'admin':
        return jsonify({"error": "Acceso restringido a administradores"}), 403

    data = request.get_json(silent=True) or request.form.to_dict() or {}
    ok, mensaje = actualizar_usuario_admin(usuario_id, data)
    if ok:
        return jsonify({"success": True, "message": mensaje}), 200
    return jsonify({"success": False, "error": mensaje}), 400


@api_bp.route('/usuarios/<string:usuario_id>/toggle', methods=['POST'])
def api_toggle_usuario(usuario_id):
    """Alterna el estado activo / pausado de un usuario."""
    if not session.get("usuario_id"):
        return jsonify({"error": "No autenticado"}), 401
    if session.get("rol") != 'admin':
        return jsonify({"error": "Acceso restringido a administradores"}), 403

    ok, status, mensaje = toggle_usuario_servicio(usuario_id)
    if ok:
        return jsonify({"success": True, "status": status, "message": mensaje}), 200
    return jsonify({"success": False, "status": status, "error": mensaje}), 400


@api_bp.route('/usuarios/<string:usuario_id>', methods=['DELETE'])
def api_eliminar_usuario(usuario_id):
    """Eliminación defensiva de usuario con candados de integridad."""
    session_user_id = session.get("usuario_id")
    if not session_user_id:
        return jsonify({"error": "No autenticado"}), 401
    if session.get("rol") != 'admin':
        return jsonify({"error": "Acceso restringido a administradores"}), 403

    ok, categoria, mensaje = eliminar_usuario_servicio(usuario_id, session_user_id)
    if ok:
        return jsonify({"success": True, "message": mensaje}), 200
    return jsonify({"success": False, "error": mensaje}), 400


@api_bp.route('/usuarios/opciones_asignacion', methods=['GET'])
def api_get_opciones_asignacion():
    """Retorna redes y Casas de Paz disponibles para asignaciones ministeriales."""
    if not session.get("usuario_id"):
        return jsonify({"error": "No autenticado"}), 401
    if session.get("rol") != 'admin':
        return jsonify({"error": "Acceso restringido a administradores"}), 403

    usuario_id = request.args.get('usuario_id')
    redes, cdps = get_opciones_asignacion(usuario_id)
    return jsonify({
        "redes": _serialize_item(redes or []),
        "casas_de_paz": _serialize_item(cdps or [])
    }), 200

