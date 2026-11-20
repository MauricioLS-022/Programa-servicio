"""
Punto de entrada de la aplicación Flask.
Inicializa la app y registra los Blueprints.
"""
import mimetypes
import os
from flask import Flask, jsonify, render_template, request, url_for, send_from_directory
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import safe_join

from config import config
from domain.exceptions import DomainError
from extensions import csrf, limiter
try:
    from flask_cors import CORS
except ImportError:
    CORS = None
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.supervisor_routes import supervisor_bp
from routes.lider_cdp_routes import lider_cdp_bp
from routes.api import api_bp
from utils.context import context_functions
from database import get_db_connection, close_db_connection

load_dotenv()

env = os.getenv('FLASK_ENV', 'development')
app = Flask(__name__)
app.config.from_object(config[env])
config[env].init_app(app)
app.secret_key = app.config['SECRET_KEY']

# Confianza en reverse proxy TLS (Render/Nginx) en producción para request.is_secure y HSTS
trust_proxy_hops = int(os.getenv('TRUST_PROXY_HOPS', '1' if env == 'production' else '0'))
if trust_proxy_hops > 0:
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=trust_proxy_hops,
        x_proto=trust_proxy_hops,
        x_host=trust_proxy_hops,
        x_prefix=trust_proxy_hops,
    )

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

# Desacoplamiento de API REST: exención de CSRF por formulario y soporte CORS
csrf.exempt(api_bp)
cors_origins = app.config.get('CORS_ORIGINS', [])
if CORS and cors_origins and env != 'production':
    CORS(app, resources={r"/api/*": {"origins": cors_origins}}, supports_credentials=True)

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
    
    # Content-Security-Policy estricta sin 'unsafe-inline' en script-src
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' https://cdn.jsdelivr.net https://google.com/recaptcha/ https://www.google.com/recaptcha/ https://gstatic.com https://www.gstatic.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com data:; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://google.com/recaptcha/ https://www.google.com/recaptcha/; "
        "frame-src 'self' https://google.com/recaptcha/ https://www.google.com/recaptcha/ https://recaptcha.google.com/; "
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
# ---------------------------------------------------------------------------
# Servicio de Single Page Application (SPA en React)
# ---------------------------------------------------------------------------
frontend_dist_dir = os.path.abspath(os.path.join(app.root_path, '..', 'frontend', 'dist'))

@app.route('/app', defaults={'path': ''})
@app.route('/app/<path:path>')
def serve_spa(path):
    """Sirve la SPA en React compilada bajo /app/ sin colisionar con rutas Flask."""
    if os.path.exists(frontend_dist_dir):
        target_path = os.path.join(frontend_dist_dir, path)
        if path != '' and os.path.exists(target_path):
            return send_from_directory(frontend_dist_dir, path)
        return send_from_directory(frontend_dist_dir, 'index.html')
    return render_template('404.html'), 404

@app.route('/assets/<path:path>')
def serve_spa_assets(path):
    """Sirve los assets compilados por Vite en dist/assets/ negociando variantes .br / .gz."""
    assets_dir = os.path.join(frontend_dist_dir, 'assets')
    plain_target = safe_join(assets_dir, path)
    if not plain_target or not os.path.isfile(plain_target):
        return render_template('404.html'), 404

    accept_encoding = request.headers.get('Accept-Encoding', '')
    original_mimetype = mimetypes.guess_type(path)[0] or 'application/octet-stream'

    chosen_path = path
    chosen_encoding = None
    if not path.endswith(('.br', '.gz')):
        if 'br' in accept_encoding and os.path.exists(f'{plain_target}.br'):
            chosen_path = f'{path}.br'
            chosen_encoding = 'br'
        elif 'gzip' in accept_encoding and os.path.exists(f'{plain_target}.gz'):
            chosen_path = f'{path}.gz'
            chosen_encoding = 'gzip'

    response = send_from_directory(assets_dir, chosen_path, mimetype=original_mimetype)
    if chosen_encoding:
        response.headers['Content-Encoding'] = chosen_encoding
    response.headers['Vary'] = 'Accept-Encoding'
    response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    return response


def _wants_json_response():
    """Determina si la respuesta debe serializarse en JSON (rutas /api/* o Accept JSON)."""
    if request.path.startswith('/api/'):
        return True
    best = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    return (
        best == 'application/json'
        and request.accept_mimetypes[best] > request.accept_mimetypes['text/html']
    )


@app.errorhandler(DomainError)
def handle_domain_error(e):
    """Traduce excepciones semánticas de dominio a JSON o plantilla HTML según negociación."""
    if _wants_json_response():
        return jsonify(e.to_dict()), e.status_code
    template_map = {400: '400.html', 403: '403.html', 404: '404.html', 429: '429.html', 500: '500.html'}
    tpl = template_map.get(e.status_code, '400.html')
    if tpl == '400.html':
        return render_template('400.html', description=e.message), e.status_code
    return render_template(tpl), e.status_code


@app.errorhandler(404)
def page_not_found(e):
    if _wants_json_response():
        return jsonify({"success": False, "error": "Recurso no encontrado", "code": "not_found"}), 404
    return render_template('404.html'), 404


@app.errorhandler(403)
def forbidden_error(e):
    """Error 403 - Acceso denegado (violación de propiedad o rol)."""
    if _wants_json_response():
        desc = getattr(e, 'description', None) or 'Acceso denegado.'
        return jsonify({"success": False, "error": desc, "code": "forbidden"}), 403
    return render_template('403.html'), 403


@app.errorhandler(400)
def bad_request_error(e):
    """Error 400 - Solicitud inválida (validación fallida o CSRF)."""
    desc = getattr(e, 'description', None) or 'Los datos de la solicitud no son válidos o el token de seguridad expiró.'
    if _wants_json_response():
        return jsonify({"success": False, "error": desc, "code": "bad_request"}), 400
    return render_template('400.html', description=desc), 400


@app.errorhandler(429)
def ratelimit_handler(e):
    """Error 429 - Límite de intentos excedido (Rate Limiting)."""
    if _wants_json_response():
        return jsonify({
            "success": False,
            "error": "Demasiados intentos. Por favor espera un minuto antes de reintentar.",
            "code": "rate_limit_exceeded",
        }), 429
    return render_template('429.html'), 429


@app.errorhandler(500)
def internal_server_error(e):
    """Error 500 - Error interno del servidor sin fugas de traza."""
    app.logger.error("Error 500: %s", e)
    if _wants_json_response():
        return jsonify({"success": False, "error": "Error interno del servidor.", "code": "internal_error"}), 500
    return render_template('500.html'), 500


# ---------------------------------------------------------------------------
# Ejecución
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(
        host=app.config.get('APP_HOST', app.config.get('HOST', '0.0.0.0')),
        port=app.config.get('APP_PORT', app.config.get('PORT', 5000)),
        debug=app.config.get('DEBUG', False)
    )
