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
    p = ""

    # Helper para redirigir según el rol
    def _redirect_by_role(role, usuario_id):
        if role == "admin":
            return redirect(url_for('admin.dashboard', id=usuario_id))
        elif role == "supervisor":
            return redirect(url_for('supervisor.dashboard', id=usuario_id))
        else:  # cdp
            return redirect(url_for('cdp.dashboard', id=usuario_id))

    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']

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
                    p = "El usuario no se encuentra registrado"
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
                    session["rol"] = r['tipo_usuario']
                    return _redirect_by_role(r['tipo_usuario'], session["usuario_id"])
            except Exception as e:
                print(f"[DB] Error login: {e}")
                p = "Error al verificar credenciales"
            finally:
                conn.close()
        else:
            # Modo demo sin BD: login simulado
            if usuario == "admin" and contrasena == "admin":
                session["usuario_id"] = "702f2129-7d4e-11f1-bf9e-2016d8516279"
                session["usuario"] = "admin"
                session["rol"] = "admin"
                return _redirect_by_role("admin", session["usuario_id"])
            elif usuario == "supervisor" and contrasena == "supervisor":
                session["usuario_id"] = "ca58cfc6-8337-11f1-8217-2016d8516279"
                session["usuario"] = "supervisor"
                session["rol"] = "supervisor"
                return _redirect_by_role("supervisor", session["usuario_id"])
            elif usuario and contrasena:
                session["usuario_id"] = "1d4f7c99-7d51-11f1-bf9e-2016d8516279"
                session["usuario"] = usuario
                session["rol"] = "cdp"
                return _redirect_by_role("cdp", session["usuario_id"])
            else:
                p = "Modo demo: usa admin/admin, supervisor/supervisor o cualquier usuario/contraseña"

    return render_template('login.html', p=p)


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
    
    usuario_id = session.get("usuario_id")
    rol = session.get("rol")
    
    if rol == "admin":
        return redirect(url_for('admin.dashboard', id=usuario_id), code=301)
    elif rol == "supervisor":
        return redirect(url_for('supervisor.dashboard', id=usuario_id), code=301)
    else:  # cdp
        return redirect(url_for('cdp.dashboard', id=usuario_id), code=301)