"""
Terra Pravah - Configuration Management
========================================
Environment-based configuration for the SaaS platform.
"""

import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).parent.parent.resolve()


class Config:
    """Base configuration."""
    
    # Application
    APP_NAME = "Terra Pravah"
    APP_VERSION = "2.0.0"
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        f'sqlite:///{BASE_DIR}/database/terrapravah.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Frontend
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    
    # Admin Configuration
    ADMIN_EMAILS = set(
        email.strip().lower() 
        for email in os.getenv('ADMIN_EMAILS', '').split(',')
        if email.strip()
    )
    
    # File Storage
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    RESULTS_FOLDER = BASE_DIR / 'results'
    # Changed default from 500MB to 5000MB (5GB) to support large LiDAR files
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_FILE_SIZE_MB', 5000)) * 1024 * 1024
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', 5000))
    
    # File format support - now using smart detection instead of hardcoded extensions
    # The file validator will auto-detect format from content
    RASTER_FORMATS = {'.tif', '.tiff', '.geotiff', '.img', '.asc', '.grd', '.dem'}
    LIDAR_FORMATS = {'.las', '.laz'}
    VECTOR_FORMATS = {'.shp', '.geojson', '.kml', '.gpkg', '.gml', '.dxf'}
    
    # Combined allowed extensions (for backward compatibility)
    ALLOWED_EXTENSIONS = RASTER_FORMATS | LIDAR_FORMATS | VECTOR_FORMATS
    
    # Enable Cloud Optimized GeoTIFF (COG) support
    ENABLE_COG_SUPPORT = os.getenv('ENABLE_COG_SUPPORT', 'true').lower() == 'true'
    
    # Sample data configuration
    ENABLE_SAMPLE_DATA = os.getenv('ENABLE_SAMPLE_DATA', 'true').lower() == 'true'
    SAMPLE_DATA_PATH = BASE_DIR / 'sample_data'
    
    # Default admin user (configurable via environment variables)
    DEFAULT_ADMIN_EMAIL = os.getenv('DEFAULT_ADMIN_EMAIL', None)
    DEFAULT_ADMIN_PASSWORD = os.getenv('DEFAULT_ADMIN_PASSWORD', None)
    CREATE_DEFAULT_ADMIN = os.getenv('CREATE_DEFAULT_ADMIN', 'false').lower() == 'true'
    
    # JWT Authentication
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers', 'cookies']
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_CSRF_PROTECT = True
    
    # OAuth Providers
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
    GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID', '')
    GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET', '')
    
    # Email (SendGrid/SMTP)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.sendgrid.net')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@terrapravah.com')
    
    # Stripe Billing
    STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', '')
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')
    
    # Celery (Background Tasks)
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', REDIS_URL)
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', REDIS_URL)
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATELIMIT_DEFAULT = "100/hour"
    RATELIMIT_HEADERS_ENABLED = True
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Feature Flags
    ENABLE_AI_ASSISTANT = os.getenv('ENABLE_AI_ASSISTANT', 'true').lower() == 'true'
    ENABLE_COLLABORATION = os.getenv('ENABLE_COLLABORATION', 'true').lower() == 'true'
    ENABLE_MARKETPLACE = os.getenv('ENABLE_MARKETPLACE', 'false').lower() == 'true'
    
    # Cloud Storage (S3/GCS)
    STORAGE_BACKEND = os.getenv('STORAGE_BACKEND', 'local')  # local, s3, gcs
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME', 'terrapravah-storage')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Subscription Plans
    PLANS = {
        'free': {
            'name': 'Free',
            'price_monthly': 0,
            'price_yearly': 0,
            'max_projects': 3,
            'max_file_size_mb': 1000,
            'max_team_members': 1,
            'features': ['basic_analysis', 'basic_visualization', 'community_support']
        },
        'professional': {
            'name': 'Professional',
            'price_monthly': 99,
            'price_yearly': 990,
            'max_projects': -1,  # Unlimited
            'max_file_size_mb': 5000,
            'max_team_members': 10,
            'features': [
                'basic_analysis', 'advanced_analysis', 'ai_assistant',
                'basic_visualization', 'advanced_visualization', '3d_export',
                'api_access', 'priority_support', 'collaboration',
                'custom_reports', 'regulatory_templates'
            ]
        },
        'enterprise': {
            'name': 'Enterprise',
            'price_monthly': None,  # Custom pricing
            'price_yearly': None,
            'max_projects': -1,
            'max_file_size_mb': 50000,
            'max_team_members': -1,
            'features': [
                'basic_analysis', 'advanced_analysis', 'ai_assistant',
                'basic_visualization', 'advanced_visualization', '3d_export',
                'api_access', 'dedicated_support', 'collaboration',
                'custom_reports', 'regulatory_templates',
                'white_label', 'sso', 'audit_logs', 'sla',
                'custom_integrations', 'training'
            ]
        }
    }


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    JWT_COOKIE_SECURE = False
    CORS_ORIGINS = ['*']


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    JWT_COOKIE_SECURE = True


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_COOKIE_SECURE = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on environment."""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
