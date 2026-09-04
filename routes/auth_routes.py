"""
Rutas de autenticación: /iniciar_sesion, /logout
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database import get_db_connection
from werkzeug.security import check_password_hash, generate_password_hash

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/iniciar_sesion', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión."""
    from flask import current_app
    p = ""
    is_dev = bool(
        current_app.config.get('DEBUG', False)
        or current_app.config.get('FLASK_ENV') == 'development'
        or current_app.config.get('MOCK_MODE', False)
    )

    # Helper para redirigir según el rol
    def _redirect_by_role(role):
        if role == "admin":
            return redirect(url_for('admin.dashboard'))
        elif role == "supervisor":
            return redirect(url_for('supervisor.dashboard'))
        else:  # lider_cdp / cdp
            return redirect(url_for('lider_cdp.dashboard'))

    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip()
        contrasena = request.form.get('contrasena', '').strip()

        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT id, username, password, tipo_usuario FROM usuario WHERE username = %s",
                    (usuario,)
                )
                r = cur.fetchone()

                password_valid = bool(r and _check_password(r['password'], contrasena))
                if not password_valid:
                    p = "Usuario o contraseña incorrectos"
                else:
                    if r['password'] == contrasena:
                        cur.execute(
                            "UPDATE usuario SET password = %s WHERE id = %s",
                            (generate_password_hash(contrasena), r['id'])
                        )
                        conn.commit()

                    # Guardar todos los datos en sesión
                    session["usuario_id"] = str(r['id'])  # Convertir UUID a string
                    session["usuario"] = r['username']
                    # Normalizar 'cdp' a 'lider_cdp' si viene de BD legacy
                    rol_final = 'lider_cdp' if r['tipo_usuario'] == 'cdp' else r['tipo_usuario']
                    session["rol"] = rol_final
                    return _redirect_by_role(rol_final)
            except Exception as e:
                current_app.logger.exception("[DB] Error login: %s", e)
                p = "Error al verificar credenciales"
            finally:
                conn.close()
        else:
            # Modo demo: ESTRICTAMENTE habilitado SOLO en entorno de desarrollo
            if is_dev:
                if usuario == "admin" and contrasena == "admin":
                    session["usuario_id"] = "702f2129-7d4e-11f1-bf9e-2016d8516279"
                    session["usuario"] = "admin"
                    session["rol"] = "admin"
                    return _redirect_by_role("admin")
                elif usuario == "supervisor" and contrasena == "supervisor":
                    session["usuario_id"] = "ca58cfc6-8337-11f1-8217-2016d8516279"
                    session["usuario"] = "supervisor"
                    session["rol"] = "supervisor"
                    return _redirect_by_role("supervisor")
                elif usuario == "lider" and contrasena == "lider":
                    session["usuario_id"] = "1d4f7c99-7d51-11f1-bf9e-2016d8516279"
                    session["usuario"] = "lider"
                    session["rol"] = "lider_cdp"
                    return _redirect_by_role("lider_cdp")
                elif usuario and contrasena:
                    from mock_data import get_mock_usuarios
                    m_user = next((u for u in get_mock_usuarios() if u['username'] == usuario), None)
                    if m_user:
                        session["usuario_id"] = m_user['id']
                        session["usuario"] = m_user['username']
                        session["rol"] = m_user['rol']
                        return _redirect_by_role(m_user['rol'])
                    session["usuario_id"] = "1d4f7c99-7d51-11f1-bf9e-2016d8516279"
                    session["usuario"] = usuario
                    session["rol"] = "lider_cdp"
                    return _redirect_by_role("lider_cdp")
                else:
                    p = "Modo desarrollo activo: ingresa admin/admin, supervisor/supervisor o un líder"
            else:
                current_app.logger.error("[PROD] Conexión a BD no disponible durante inicio de sesión")
                p = "Servicio no disponible temporalmente. Intente más tarde."

    return render_template('login.html', p=p, is_dev=is_dev)


def _check_password(stored_password, provided_password):
    """Valida hashes Werkzeug y permite migrar una contraseña legacy una vez."""
    if not stored_password or not provided_password:
        return False

    if stored_password.count('$') < 2:
        return stored_password == provided_password

    try:
        return check_password_hash(stored_password, provided_password)
    except (ValueError, TypeError):
        return False


@auth_bp.route('/logout')
def logout():
    """Cierra la sesión del usuario."""
    session.pop("usuario_id", None)
    session.pop("usuario", None)
    session.pop("rol", None)
    return redirect(url_for("auth.login"))


# Legacy routes
@auth_bp.route('/')
def index():
    """Ruta raíz - redirige al dashboard según el rol del usuario."""
    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))
    
    rol = session.get("rol")
    
    if rol == "admin":
        return redirect(url_for('admin.dashboard'), code=301)
    elif rol == "supervisor":
        return redirect(url_for('supervisor.dashboard'), code=301)
    else:  # lider_cdp / cdp
        return redirect(url_for('lider_cdp.dashboard'), code=301)