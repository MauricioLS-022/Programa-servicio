"""
Punto de entrada de la aplicación Flask.
Inicializa la app y registra los Blueprints.
"""
import os
from flask import Flask, render_template, request, url_for
from dotenv import load_dotenv

from config import config
from extensions import csrf, limiter
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.supervisor_routes import supervisor_bp
from routes.lider_cdp_routes import lider_cdp_bp
from routes.api_routes import api_bp
from utils.context import context_functions
from database import get_db_connection, close_db_connection

load_dotenv()

env = os.getenv('FLASK_ENV', 'development')
app = Flask(__name__)
app.config.from_object(config[env])
app.secret_key = app.config['SECRET_KEY']

# Inicializar extensiones de seguridad (CSRF y Rate Limiting)
csrf.init_app(app)
limiter.init_app(app)

@app.before_request
def handle_testing_modes():
    """Desactiva automáticamente CSRF en modo testing salvo que el test lo fuerce explícitamente."""
    if app.config.get('TESTING') and not app.config.get('FORCE_CSRF_IN_TESTING', False):
        app.config['WTF_CSRF_ENABLED'] = False

# Limpieza de conexión por ciclo de petición
app.teardown_appcontext(close_db_connection)

# ---------------------------------------------------------------------------
# Registrar Blueprints
# ---------------------------------------------------------------------------
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(supervisor_bp)
app.register_blueprint(lider_cdp_bp)
app.register_blueprint(api_bp)

# ---------------------------------------------------------------------------
# Context Processors
# ---------------------------------------------------------------------------
@app.context_processor
def utility_processor():
    """Inyecta funciones helper en todas las plantillas Jinja2."""
    return context_functions


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    """Agrega versionado a archivos estáticos para cache busting."""
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path, endpoint, filename)
            try:
                values['v'] = int(os.stat(file_path).st_mtime)
            except OSError:
                pass
    return url_for(endpoint, **values)


# ---------------------------------------------------------------------------
# Hardening de Cabeceras HTTP y Caché de activos estáticos
# ---------------------------------------------------------------------------
@app.after_request
def apply_security_headers(response):
    """Inyecta cabeceras defensivas HTTP (OWASP) y control de caché."""
    # Cabeceras globales de seguridad
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    # Content-Security-Policy alineada con los estilos, iconos y fuentes del sistema
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com data:; "
        "img-src 'self' data: https:; "
        "connect-src 'self'; "
        "frame-ancestors 'self';"
    )

    # HSTS en producción
    if not app.config.get('DEBUG', False) and request.is_secure:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

    # Cache específico para estáticos
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=2592000'

    return response


# ---------------------------------------------------------------------------
# Error Handlers
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(403)
def forbidden_error(e):
    """Error 403 - Acceso denegado (violación de propiedad o rol)."""
    return render_template('403.html'), 403


@app.errorhandler(400)
def bad_request_error(e):
    """Error 400 - Solicitud inválida (validación fallida o CSRF)."""
    desc = getattr(e, 'description', None) or 'Los datos de la solicitud no son válidos o el token de seguridad expiró.'
    return render_template('400.html', description=desc), 400


@app.errorhandler(429)
def ratelimit_handler(e):
    """Error 429 - Límite de intentos excedido (Rate Limiting)."""
    return render_template('429.html'), 429


@app.errorhandler(500)
def internal_server_error(e):
    """Error 500 - Error interno del servidor sin fugas de traza."""
    app.logger.error("Error 500: %s", e)
    return render_template('500.html'), 500


# ---------------------------------------------------------------------------
# Ejecución
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(
        host=app.config.get('APP_HOST', app.config.get('HOST', '0.0.0.0')),
        port=app.config.get('APP_PORT', app.config.get('PORT', 5000)),
        debug=app.config.get('DEBUG', True)
    )