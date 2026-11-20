"""
routes/api/auth_api.py - Endpoints REST de autenticación y verificación de sesión HttpOnly.
"""
import hmac
import requests
from flask import request, jsonify, session, current_app
from flask_wtf.csrf import generate_csrf
from werkzeug.security import generate_password_hash
from database import get_db_connection
from extensions import limiter
from repositories import unit_of_work
from routes.auth_routes import _check_password
from services.queries.usuarios_queries import (
    obtener_usuario_por_username,
    actualizar_password_usuario,
)
from services.cdp_service import get_perfil_data, cambiar_username, cambiar_password
from utils.auth import api_auth_required
from utils.validators import validate_password_strength, validate_username
from schemas import parse_payload, PerfilUsernameDTO, PerfilPasswordDTO
from .base import api_bp, _serialize_item


@api_bp.route('/auth/csrf-token', methods=['GET'])
def api_auth_csrf_token():
    """Retorna un token CSRF vinculado a la sesión actual para mutaciones REST."""
    return jsonify({"csrf_token": generate_csrf()}), 200


@api_bp.route('/auth/config', methods=['GET'])
def api_auth_config():
    """Retorna la configuración pública necesaria para la autenticación en el frontend."""
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
    site_key = current_app.config.get("RECAPTCHA_SITE_KEY", "")
    return jsonify({
        "siteKey": site_key,
        "isDev": is_dev,
        "csrf_token": generate_csrf(),
    }), 200


@api_bp.route('/auth/login', methods=['POST'])
@limiter.limit("5 per minute", methods=["POST"])
def api_auth_login():
    """Autenticación REST para clientes desacoplados con sesión HttpOnly y protección anti-bot reCAPTCHA."""
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    usuario = (data.get('usuario') or data.get('username') or '').strip()
    contrasena = (data.get('contrasena') or data.get('password') or '').strip()
    recaptcha_token = (data.get('recaptcha_token') or data.get('g-recaptcha-response') or '').strip()

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

    # Verificación de reCAPTCHA
    secret = current_app.config.get("RECAPTCHA_SECRET_KEY", "")
    captcha_valido = False
    puntaje = 0.0
    accion = ""

    if is_dev and not recaptcha_token:
        captcha_valido = True
        puntaje = 1.0
        accion = "login"
    else:
        try:
            respuesta = requests.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data={"secret": secret, "response": recaptcha_token},
                timeout=5
            )
            resultado = respuesta.json()
            captcha_valido = resultado.get("success", False)
            puntaje = resultado.get("score", 0.0)
            accion = resultado.get("action", "")
            error_codes = resultado.get("error-codes", [])
            current_app.logger.info(
                f"[API reCAPTCHA] Éxito: {captcha_valido} | Puntuación: {puntaje} | Acción: {accion} | Errores: {error_codes}"
            )
        except Exception as e:
            current_app.logger.error(f"[API reCAPTCHA] Error de conexión: {e}")
            captcha_valido = False

    if not captcha_valido or puntaje < 0.7 or (accion != "login" and not is_dev):
        return jsonify({
            "success": False,
            "error": "Tráfico sospechoso o verificación de seguridad fallida. Inténtalo de nuevo."
        }), 400

    try:
        with unit_of_work(conn_provider=get_db_connection, transactional=False) as uow:
            if uow is not None:
                cur = uow.cursor()
                r = obtener_usuario_por_username(cur, usuario)

                password_valid = bool(r and _check_password(r['password'], contrasena))
                if not password_valid:
                    return jsonify({"success": False, "error": "Usuario o contraseña incorrectos"}), 401

                if not bool(r.get('is_active', 1)):
                    return jsonify({"success": False, "error": "Esta cuenta se encuentra inactiva o suspendida"}), 403

                # Si la contraseña era texto plano legacy, actualizar hash
                if hmac.compare_digest(r['password'], contrasena):
                    actualizar_password_usuario(cur, r['id'], generate_password_hash(contrasena))
                    uow.commit()

                session.clear()
                session.permanent = True
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
                return jsonify({"success": True, "user": user_payload, "csrf_token": generate_csrf()}), 200
    except Exception as e:
        current_app.logger.exception("[API Auth] Error en verificación: %s", e)
        return jsonify({"success": False, "error": "Error interno al verificar credenciales"}), 500

    # Fallback a modo demo en entornos dev / testing
    if True:
        if is_dev and not is_production:
            if usuario == "admin" and contrasena == "admin":
                session.clear()
                session.permanent = True
                session["usuario_id"] = "702f2129-7d4e-11f1-bf9e-2016d8516279"
                session["usuario"] = "admin"
                session["rol"] = "admin"
                session["nombre"] = "Administrador"
                session["apellido"] = "Sistema"
                return jsonify({
                    "success": True,
                    "csrf_token": generate_csrf(),
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
                session.permanent = True
                session["usuario_id"] = "ca58cfc6-8337-11f1-8217-2016d8516279"
                session["usuario"] = "supervisor"
                session["rol"] = "supervisor"
                session["nombre"] = "Supervisor"
                session["apellido"] = "Red"
                return jsonify({
                    "success": True,
                    "csrf_token": generate_csrf(),
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
                session.permanent = True
                session["usuario_id"] = "1d4f7c99-7d51-11f1-bf9e-2016d8516279"
                session["usuario"] = "lider"
                session["rol"] = "lider_cdp"
                session["nombre"] = "Líder"
                session["apellido"] = "CDP"
                return jsonify({
                    "success": True,
                    "csrf_token": generate_csrf(),
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
                    session.permanent = True
                    session["usuario_id"] = m_user['id']
                    session["usuario"] = m_user['username']
                    session["rol"] = m_user['rol']
                    session["nombre"] = m_user.get('nombre', '')
                    session["apellido"] = m_user.get('apellido', '')
                    return jsonify({
                        "success": True,
                        "csrf_token": generate_csrf(),
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
        "csrf_token": generate_csrf(),
        "user": {
            "id": usuario_id,
            "username": session.get("usuario"),
            "rol": session.get("rol"),
            "nombre": session.get("nombre", ""),
            "apellido": session.get("apellido", "")
        }
    }), 200


@api_bp.route('/perfil', methods=['GET'])
@api_auth_required
def api_get_perfil():
    """Retorna los datos de perfil del usuario autenticado con sus asignaciones."""
    usuario_id = session.get("usuario_id")

    perfil = get_perfil_data(str(usuario_id))
    return jsonify({
        "perfil": _serialize_item(perfil),
        "usuario": session.get("usuario"),
        "rol": session.get("rol")
    }), 200


@api_bp.route('/perfil/username', methods=['POST'])
@api_auth_required
def api_cambiar_perfil_username():
    """Actualiza el nombre de usuario verificando formato y unicidad."""
    usuario_id = session.get("usuario_id")

    raw_data = request.get_json(silent=True) or request.form.to_dict() or {}
    dto = parse_payload(PerfilUsernameDTO, raw_data)
    nuevo_username = dto.nuevo_username or ''

    ok_user, res_user = validate_username(nuevo_username)
    if not ok_user:
        return jsonify({"success": False, "error": res_user}), 400

    exito, mensaje = cambiar_username(usuario_id, res_user)
    if exito:
        session['usuario'] = res_user
        return jsonify({"success": True, "message": mensaje, "username": res_user}), 200
    return jsonify({"success": False, "error": mensaje}), 400


@api_bp.route('/perfil/password', methods=['POST'])
@api_auth_required
def api_cambiar_perfil_password():
    """Cambia la contraseña validando la contraseña actual y políticas de complejidad."""
    usuario_id = session.get("usuario_id")

    raw_data = request.get_json(silent=True) or request.form.to_dict() or {}
    dto = parse_payload(PerfilPasswordDTO, raw_data)
    password_actual = dto.password_actual
    password_nueva = dto.password_nueva

    ok_pass, msg_pass = validate_password_strength(password_nueva)
    if not ok_pass:
        return jsonify({"success": False, "error": msg_pass}), 400

    exito, mensaje = cambiar_password(usuario_id, password_actual, password_nueva)
    if exito:
        return jsonify({"success": True, "message": mensaje}), 200
    return jsonify({"success": False, "error": mensaje}), 400
