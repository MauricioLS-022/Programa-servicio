"""
routes/api/auth_api.py - Endpoints REST de autenticación y verificación de sesión HttpOnly.
"""
from flask import request, jsonify, session, current_app
from werkzeug.security import generate_password_hash
from database import get_db_connection
from routes.auth_routes import _check_password
from .base import api_bp


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
