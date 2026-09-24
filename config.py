import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', '3306'))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'serv_comunitario')
    DB_TIMEOUT = float(os.getenv('DB_TIMEOUT', '5.0'))
    DB_SSL = os.getenv('DB_SSL', 'true').lower() in ('true', '1', 't', 'required')
    
    # App
    HOST = os.getenv('APP_HOST', '0.0.0.0')
    PORT = int(os.getenv('APP_PORT', '5000'))
    APP_HOST = HOST
    APP_PORT = PORT
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    MOCK_MODE = os.getenv('MOCK_MODE', 'False').lower() in ('true', '1', 't', 'yes')
    
    # Flask & Security Hardening
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 7200

    RECAPTCHA_SITE_KEY = os.getenv("RECAPTCHA_SITE_KEY", "")
    RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY", "")
    
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        ssl_param = "?ssl-mode=REQUIRED" if self.DB_SSL and self.DB_HOST not in ('localhost', '127.0.0.1') else ""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}{ssl_param}"


INSECURE_SECRET_KEYS = {
    'dev-secret-key-change-in-production',
    'secret',
    'secret-key',
    'change-me',
    'change-in-production',
    'default-key',
    '123456',
    'password',
}


def validate_production_config(cfg):
    """
    Valida rigurosamente la configuración para entornos de producción (Fail-Fast).
    Lanza RuntimeError con la lista detallada de incumplimientos si detecta
    valores faltantes, flags inseguras o credenciales por defecto.
    """
    errors = []

    def get_val(key, default=None):
        if hasattr(cfg, 'get'):
            val = cfg.get(key, default)
            if val is not None:
                return val
        return getattr(cfg, key, default)

    # 1. Validación de DEBUG y TESTING
    if get_val('DEBUG') is True:
        errors.append("DEBUG no puede ser True en entorno de producción.")
    if get_val('TESTING') is True:
        errors.append("TESTING no puede ser True en entorno de producción.")

    # 2. Validación de MOCK_MODE
    if get_val('MOCK_MODE') is True:
        errors.append("MOCK_MODE no puede ser True en entorno de producción.")

    # 3. Validación de SECRET_KEY
    secret = str(get_val('SECRET_KEY') or '').strip()
    if not secret:
        errors.append("SECRET_KEY es obligatoria y no puede estar vacía.")
    elif secret.lower() in INSECURE_SECRET_KEYS:
        errors.append(f"SECRET_KEY contiene un valor de desarrollo inseguro ('{secret}'). Debe generarse una clave criptográfica real.")
    elif len(secret) < 16:
        errors.append("SECRET_KEY debe tener una longitud mínima de 16 caracteres para garantizar suficiente entropía criptográfica.")

    # 4. Validación de credenciales de Base de Datos
    db_host = str(get_val('DB_HOST') or '').strip()
    db_user = str(get_val('DB_USER') or '').strip()
    db_password = str(get_val('DB_PASSWORD') or '').strip()
    db_name = str(get_val('DB_NAME') or '').strip()

    if not db_host:
        errors.append("DB_HOST es obligatoria en producción.")
    if not db_user:
        errors.append("DB_USER es obligatoria en producción.")
    if not db_password:
        errors.append("DB_PASSWORD es obligatoria y no puede ser vacía en producción.")
    if not db_name:
        errors.append("DB_NAME es obligatoria en producción.")

    # 5. Validación de reCAPTCHA
    recaptcha_site = str(get_val('RECAPTCHA_SITE_KEY') or '').strip()
    recaptcha_secret = str(get_val('RECAPTCHA_SECRET_KEY') or '').strip()
    if not recaptcha_site or not recaptcha_secret:
        errors.append("RECAPTCHA_SITE_KEY y RECAPTCHA_SECRET_KEY son obligatorias en producción para proteger el inicio de sesión.")

    # 6. Validación de cookies seguras
    if not get_val('SESSION_COOKIE_SECURE'):
        errors.append("SESSION_COOKIE_SECURE debe ser True en producción.")

    if errors:
        msg = "Fallo de validación de seguridad para producción:\n  - " + "\n  - ".join(errors)
        raise RuntimeError(msg)


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False

    @classmethod
    def init_app(cls, app):
        pass


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    MOCK_MODE = False
    SESSION_COOKIE_SECURE = True
    FLASK_ENV = 'production'

    @classmethod
    def init_app(cls, app):
        validate_production_config(app.config)


class TestingConfig(Config):
    TESTING = True
    DEBUG = False
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False

    @classmethod
    def init_app(cls, app):
        pass


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

