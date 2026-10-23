"""
routes/api/auth_api.py - Endpoints REST de autenticación y verificación de sesión HttpOnly.
"""
from flask import request, jsonify, session, current_app
from werkzeug.security import generate_password_hash
from database import get_db_connection
from routes.auth_routes import _check_password
from services.cdp_service import get_perfil_data, cambiar_username, cambiar_password
from utils.validators import validate_password_strength, validate_username
from .base import api_bp, _serialize_item


@api_bp.route('/auth/login', methods=['POST'])
def api_auth_login():
    """Autenticación REST para clientes desacoplados con sesión HttpOnly."""
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    usuario = (data.get('usuario') or data.get('username') or '').strip()
    contrasena = (data.get('contrasena') or data.get('password') or '').strip()

    if not usuario or not contrasena:
        return jsonify({
            "success": False,
            "error": "Usuario y contraseña requeridos"
        }), 400

    is_production = bool(
        current_app.config.get('FLASK_ENV') == 'production'
        or (not current_app.config.get('DEBUG', False) and not current_app.config.get('TESTING', False) and current_app.config.get('FLASK_ENV') != 'development')
    )
    is_dev = not is_production and bool(
        current_app.config.get('DEBUG', False)
        or current_app.config.get('FLASK_ENV') == 'development'
        or current_app.config.get('MOCK_MODE', False)
        or current_app.config.get('TESTING', False)
    )

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, username, password, tipo_usuario, is_active, nombre, apellido FROM usuario WHERE username = %s",
                (usuario,)
            )
            r = cur.fetchone()

            password_valid = bool(r and _check_password(r['password'], contrasena))
            if not password_valid:
                return jsonify({"success": False, "error": "Usuario o contraseña incorrectos"}), 401

            if not bool(r.get('is_active', 1)):
                return jsonify({"success": False, "error": "Esta cuenta se encuentra inactiva o suspendida"}), 403

            # Si la contraseña era texto plano legacy, actualizar hash
            if r['password'] == contrasena:
                cur.execute(
                    "UPDATE usuario SET password = %s WHERE id = %s",
                    (generate_password_hash(contrasena), r['id'])
                )
                conn.commit()

            session.clear()
            session["usuario_id"] = str(r['id'])
            session["usuario"] = r['username']
            rol_final = 'lider_cdp' if r['tipo_usuario'] == 'cdp' else r['tipo_usuario']
            session["rol"] = rol_final
            session["nombre"] = r.get('nombre', '')
            session["apellido"] = r.get('apellido', '')

            user_payload = {
                "id": str(r['id']),
                "username": r['username'],
                "rol": rol_final,
                "nombre": r.get('nombre', ''),
                "apellido": r.get('apellido', '')
            }
            return jsonify({"success": True, "user": user_payload}), 200
        except Exception as e:
            current_app.logger.exception("[API Auth] Error en verificación: %s", e)
            return jsonify({"success": False, "error": "Error interno al verificar credenciales"}), 500
        finally:
            conn.close()
    else:
        # Fallback a modo demo en entornos dev / testing
        if is_dev and not is_production:
            if usuario == "admin" and contrasena == "admin":
                session.clear()
                session["usuario_id"] = "702f2129-7d4e-11f1-bf9e-2016d8516279"
                session["usuario"] = "admin"
                session["rol"] = "admin"
                session["nombre"] = "Administrador"
                session["apellido"] = "Sistema"
                return jsonify({
                    "success": True,
                    "user": {
                        "id": session["usuario_id"],
                        "username": "admin",
                        "rol": "admin",
                        "nombre": "Administrador",
                        "apellido": "Sistema"
                    }
                }), 200
            elif usuario == "supervisor" and contrasena == "supervisor":
                session.clear()
                session["usuario_id"] = "ca58cfc6-8337-11f1-8217-2016d8516279"
                session["usuario"] = "supervisor"
                session["rol"] = "supervisor"
                session["nombre"] = "Supervisor"
                session["apellido"] = "Red"
                return jsonify({
                    "success": True,
                    "user": {
                        "id": session["usuario_id"],
                        "username": "supervisor",
                        "rol": "supervisor",
                        "nombre": "Supervisor",
                        "apellido": "Red"
                    }
                }), 200
            elif usuario == "lider" and contrasena == "lider":
                session.clear()
                session["usuario_id"] = "1d4f7c99-7d51-11f1-bf9e-2016d8516279"
                session["usuario"] = "lider"
                session["rol"] = "lider_cdp"
                session["nombre"] = "Líder"
                session["apellido"] = "CDP"
                return jsonify({
                    "success": True,
                    "user": {
                        "id": session["usuario_id"],
                        "username": "lider",
                        "rol": "lider_cdp",
                        "nombre": "Líder",
                        "apellido": "CDP"
                    }
                }), 200
            elif usuario and contrasena:
                from mock_data import get_mock_usuarios
                m_user = next((u for u in get_mock_usuarios() if u['username'] == usuario), None)
                if m_user:
                    session.clear()
                    session["usuario_id"] = m_user['id']
                    session["usuario"] = m_user['username']
                    session["rol"] = m_user['rol']
                    session["nombre"] = m_user.get('nombre', '')
                    session["apellido"] = m_user.get('apellido', '')
                    return jsonify({
                        "success": True,
                        "user": {
                            "id": m_user['id'],
                            "username": m_user['username'],
                            "rol": m_user['rol'],
                            "nombre": m_user.get('nombre', ''),
                            "apellido": m_user.get('apellido', '')
                        }
                    }), 200
            return jsonify({"success": False, "error": "Credenciales inválidas"}), 401
        else:
            return jsonify({"success": False, "error": "Servicio de base de datos no disponible temporalmente"}), 503


@api_bp.route('/auth/logout', methods=['POST'])
def api_auth_logout():
    """Invalida la sesión actual del usuario."""
    session.clear()
    return jsonify({
        "success": True,
        "message": "Sesión cerrada correctamente"
    }), 200


@api_bp.route('/auth/me', methods=['GET'])
def api_auth_me():
    """Retorna la identidad y rol del usuario autenticado vía sesión HttpOnly."""
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return jsonify({
            "authenticated": False,
            "error": "No autenticado"
        }), 401

    return jsonify({
        "authenticated": True,
        "user": {
            "id": usuario_id,
            "username": session.get("usuario"),
            "rol": session.get("rol"),
            "nombre": session.get("nombre", ""),
            "apellido": session.get("apellido", "")
        }
    }), 200


@api_bp.route('/perfil', methods=['GET'])
def api_get_perfil():
    """Retorna los datos de perfil del usuario autenticado con sus asignaciones."""
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return jsonify({"error": "No autenticado"}), 401

    perfil = get_perfil_data(str(usuario_id))
    return jsonify({
        "perfil": _serialize_item(perfil),
        "usuario": session.get("usuario"),
        "rol": session.get("rol")
    }), 200


@api_bp.route('/perfil/username', methods=['POST'])
def api_cambiar_perfil_username():
    """Actualiza el nombre de usuario verificando formato y unicidad."""
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return jsonify({"error": "No autenticado"}), 401

    data = request.get_json(silent=True) or request.form.to_dict() or {}
    nuevo_username = (data.get('nuevo_username') or data.get('username') or '').strip()

    ok_user, res_user = validate_username(nuevo_username)
    if not ok_user:
        return jsonify({"success": False, "error": res_user}), 400

    exito, mensaje = cambiar_username(usuario_id, res_user)
    if exito:
        session['usuario'] = res_user
        return jsonify({"success": True, "message": mensaje, "username": res_user}), 200
    return jsonify({"success": False, "error": mensaje}), 400


@api_bp.route('/perfil/password', methods=['POST'])
def api_cambiar_perfil_password():
    """Cambia la contraseña validando la contraseña actual y políticas de complejidad."""
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return jsonify({"error": "No autenticado"}), 401

    data = request.get_json(silent=True) or request.form.to_dict() or {}
    password_actual = data.get('password_actual', '')
    password_nueva = data.get('password_nueva', '')
    password_confirmar = data.get('password_confirmar', '')

    if not password_actual:
        return jsonify({"success": False, "error": "Debe ingresar su contraseña actual"}), 400

    if not password_nueva:
        return jsonify({"success": False, "error": "Debe ingresar una nueva contraseña"}), 400

    if password_confirmar and password_nueva != password_confirmar:
        return jsonify({"success": False, "error": "Las contraseñas nuevas no coinciden"}), 400

    ok_pass, msg_pass = validate_password_strength(password_nueva)
    if not ok_pass:
        return jsonify({"success": False, "error": msg_pass}), 400

    exito, mensaje = cambiar_password(usuario_id, password_actual, password_nueva)
    if exito:
        return jsonify({"success": True, "message": mensaje}), 200
    return jsonify({"success": False, "error": mensaje}), 400
