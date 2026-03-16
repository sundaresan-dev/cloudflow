import os

class Config:
    """Application Configuration"""
    
    # Flask Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = True
    SESSION_PERMANENT = False
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # Database Settings
    DB_HOST = 'localhost'
    DB_USER = 'flaskapp'
    
    DB_PASSWORD = 'flaskapp123'
    DB_NAME = 'website_deployment_system'
    DB_PORT = 3306
    
    # Deployment Settings
    DEPLOYED_SITES_PATH = os.path.join(os.path.dirname(__file__), 'deployed_sites')
    TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), 'templates_websites')
    MAX_DEPLOYMENTS_PER_USER = 10
    
    # Custom Domain & Port Settings
    CUSTOM_DOMAIN = 'deployment.local'  # Fake domain name
    APP_PORT = 8080  # Custom port number
    APP_HOST = '0.0.0.0'  # Listen on all interfaces
    APP_URL = 'http://deployment.local:8080'  # Full URL for the application
