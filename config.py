

import os

class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-cambiar-en-produccion'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de sesión
    SESSION_COOKIE_SECURE = False  # Cambiar a True en producción con HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora en segundos
    
    # Configuración de paginación
    ITEMS_PER_PAGE = 20
    
    # Formato de fecha
    DATE_FORMAT = '%d/%m/%Y'
    DATETIME_FORMAT = '%d/%m/%Y %H:%M'

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///facturacion.db'
    SQLALCHEMY_ECHO = True  # Mostrar consultas SQL en consola

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    
    # Usar una base de datos más robusta en producción
    # Ejemplos:
    # PostgreSQL: postgresql://usuario:password@localhost/facturacion
    # MySQL: mysql://usuario:password@localhost/facturacion
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///facturacion.db'
    
    # Seguridad mejorada
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Diccionario de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}