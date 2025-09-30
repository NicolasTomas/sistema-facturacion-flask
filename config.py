

import os

class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-cambiar-en-produccion'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
   
    SESSION_COOKIE_SECURE = False 
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  
    
   
    ITEMS_PER_PAGE = 20
    
    DATE_FORMAT = '%d/%m/%Y'
    DATETIME_FORMAT = '%d/%m/%Y %H:%M'

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///facturacion.db'
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///facturacion.db'
    
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}