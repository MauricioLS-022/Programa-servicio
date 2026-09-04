import os
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
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    MOCK_MODE = os.getenv('MOCK_MODE', 'False').lower() in ('true', '1', 't', 'yes')
    
    # Flask
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        ssl_param = "?ssl-mode=REQUIRED" if self.DB_SSL and self.DB_HOST not in ('localhost', '127.0.0.1') else ""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}{ssl_param}"


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}