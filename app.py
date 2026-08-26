"""
Punto de entrada de la aplicación Flask.
Inicializa la app y registra los Blueprints.
"""
import os
from flask import Flask, render_template, request, url_for
from dotenv import load_dotenv

from config import config
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.supervisor_routes import supervisor_bp
from routes.cdp_routes import cdp_bp
from routes.api_routes import api_bp
from utils.context import context_functions
from database import get_db_connection

load_dotenv()

env = os.getenv('FLASK_ENV', 'development')
app = Flask(__name__)
app.config.from_object(config[env])
app.secret_key = app.config['SECRET_KEY']

# ---------------------------------------------------------------------------
# Registrar Blueprints
# ---------------------------------------------------------------------------
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(supervisor_bp)
app.register_blueprint(cdp_bp)
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
# Caché de activos estáticos CSS/JS en el navegador
# ---------------------------------------------------------------------------
@app.after_request
def add_static_cache_headers(response):
    """Inyecta cabeceras Cache-Control para archivos estáticos."""
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=2592000'
        response.headers['X-Content-Type-Options'] = 'nosniff'
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
    """Error 400 - Solicitud inválida (UUID mal formado)."""
    return render_template('404.html'), 400


# ---------------------------------------------------------------------------
# Ejecución
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(
        host=app.config.get('APP_HOST', app.config.get('HOST', '0.0.0.0')),
        port=app.config.get('APP_PORT', app.config.get('PORT', 5000)),
        debug=app.config.get('DEBUG', True)
    )