import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def validate_production_secrets():
    """Validate that all required secrets are set in production and not placeholders"""
    env = os.getenv('FLASK_ENV', 'development')
    
    if env != 'production':
        return  # Only validate in production
    
    required_secrets = {
        'SECRET_KEY': os.getenv('SECRET_KEY'),
        'DATABASE_URL': os.getenv('DATABASE_URL'),
        'STRIPE_SECRET_KEY': os.getenv('STRIPE_SECRET_KEY'),
        'STRIPE_PUBLISHABLE_KEY': os.getenv('STRIPE_PUBLISHABLE_KEY'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'MAIL_USERNAME': os.getenv('MAIL_USERNAME'),
        'MAIL_PASSWORD': os.getenv('MAIL_PASSWORD'),
    }
    
    # Check for missing or placeholder values
    placeholder_keywords = ['PLACEHOLDER', 'CHANGE_THIS', 'your-email', 'dev-secret-key']
    errors = []
    
    for key, value in required_secrets.items():
        if not value:
            errors.append(f"[ERROR] {key} is missing or empty")
        elif any(placeholder in value for placeholder in placeholder_keywords):
            errors.append(f"[ERROR] {key} still contains a placeholder value")
    
    if errors:
        error_msg = "\n".join([
            "PRODUCTION SECURITY ERROR",
            "Cannot start in production mode with missing or placeholder secrets:",
            "",
            *errors,
            "",
            "Fix this by:",
            "1. Copy .env.example to .env",
            "2. Replace ALL placeholder values with real secrets",
            "3. Ensure FLASK_ENV=production is set",
            "",
            "This check protects your production deployment."
        ])
        raise ValueError(error_msg)
    
    print("[OK] All production secrets validated successfully")


class Config:
    """Base configuration class"""

    # Flask Core
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///snowboard_media.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # Session
    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'snowboard_session:'

    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    # Flask-Login
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True

    # File Upload
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 524288000))  # 500MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'app/static/uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}

    # API Keys
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
    AYRSHARE_API_KEY = os.getenv('AYRSHARE_API_KEY')
    VIMEO_ACCESS_TOKEN = os.getenv('VIMEO_ACCESS_TOKEN')

    # Email Configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME')

    # Application Settings
    APP_NAME = os.getenv('APP_NAME', 'Momentum Clips')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@momentumclips.com')
    SUPPORT_EMAIL = os.getenv('SUPPORT_EMAIL', 'support@momentumclips.com')
    
    # Retell AI Chat Widget Configuration
    RETELL_PUBLIC_KEY = os.getenv('RETELL_PUBLIC_KEY', '')
    RETELL_AGENT_ID = os.getenv('RETELL_AGENT_ID', '')

    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    WTF_CSRF_CHECK_DEFAULT = True
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5000').split(',')

    # SocketIO
    SOCKETIO_MESSAGE_QUEUE = REDIS_URL
    SOCKETIO_ASYNC_MODE = 'eventlet'

    # Claude AI Configuration
    CLAUDE_MODEL = 'claude-sonnet-4-5-20250929'
    CLAUDE_MAX_TOKENS = 1024
    CLAUDE_TEMPERATURE = 0.7

    # Booking System
    BOOKING_ADVANCE_DAYS = 90  # How far in advance users can book
    BOOKING_BUFFER_HOURS = 24  # Minimum hours before booking date
    DEFAULT_BOOKING_DURATION = 4  # Default session duration in hours

    # Pagination
    ITEMS_PER_PAGE = 12
    ADMIN_ITEMS_PER_PAGE = 20

    # Social Media Posting Schedule
    SOCIAL_MEDIA_TIMEZONE = 'Europe/Sofia'  # Eastern European Time for Bansko, Bulgaria


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

    # Use SQLite for development if MySQL not available
    if not os.getenv('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = 'sqlite:///dev_snowboard_media.db'

    # Less strict security for development
    REMEMBER_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = True  # CSRF enabled even in dev for better testing

    # Verbose logging
    SQLALCHEMY_ECHO = False  # Set to True to see SQL queries

    # Socket.IO development settings
    SOCKETIO_LOGGER = True
    SOCKETIO_ENGINEIO_LOGGER = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    def __init__(self):
        # Validate all secrets on initialization
        validate_production_secrets()

    # Enforce HTTPS
    PREFERRED_URL_SCHEME = 'https'

    # Strict security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True

    # Database connection pooling
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 10,
        'max_overflow': 20,
    }

    # Production logging
    LOG_TO_STDOUT = True
    LOG_LEVEL = 'INFO'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

    # Use in-memory SQLite for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    # Disable CSRF for easier testing
    WTF_CSRF_ENABLED = False

    # Fast password hashing for tests
    BCRYPT_LOG_ROUNDS = 4

    # Disable rate limiting in tests
    RATELIMIT_ENABLED = False


# Configuration dictionary
config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on FLASK_ENV"""
    env = os.getenv('FLASK_ENV', 'development')
    
    # Validate production secrets before returning config
    if env == 'production':
        validate_production_secrets()
    
    return config_dict.get(env, DevelopmentConfig)
