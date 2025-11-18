from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_compress import Compress
from config import get_config
import redis

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
socketio = SocketIO()
compress = Compress()
talisman = None  # Will be initialized conditionally in create_app
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Redis connection
redis_client = None


def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)

    # Load configuration
    if config_name:
        from config import config_dict
        app.config.from_object(config_dict[config_name])
    else:
        app.config.from_object(get_config())

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # CSRF Protection - enabled by default from config
    # Note: Individual routes can be exempted using @csrf.exempt decorator
    
    # Initialize rate limiter
    limiter.init_app(app)
    
    # Initialize compression for better performance & SEO
    compress.init_app(app)
    
    # Make config variables available in templates
    @app.context_processor
    def inject_config():
        return {
            'RETELL_PUBLIC_KEY': app.config.get('RETELL_PUBLIC_KEY', ''),
            'RETELL_AGENT_ID': app.config.get('RETELL_AGENT_ID', ''),
            'support_email': app.config.get('SUPPORT_EMAIL', '')
        }
    
    # Initialize Flask-Talisman for production security
    # Only enforce HTTPS in production
    if not app.config.get('DEBUG', False):
        global talisman
        # Content Security Policy - adjusted for Retell AI chat widget
        csp = {
            'default-src': ["'self'"],
            'script-src': [
                "'self'",
                "'unsafe-inline'",  # Required for some inline scripts
                "https://cdn.socket.io",
                "https://js.stripe.com",
                "https://player.vimeo.com",
                "https://dashboard.retellai.com",  # Retell widget script
                "https://cdn.tailwindcss.com"  # Tailwind CDN
            ],
            'style-src': [
                "'self'",
                "'unsafe-inline'",  # Required for inline styles
                "https://fonts.googleapis.com"
            ],
            'font-src': [
                "'self'",
                "https://fonts.gstatic.com",
                "https://cdnjs.cloudflare.com"  # Font Awesome
            ],
            'img-src': [
                "'self'",
                "data:",
                "https:",
                "blob:"
            ],
            'frame-src': [
                "https://js.stripe.com",
                "https://player.vimeo.com"
            ],
            'connect-src': [
                "'self'",
                "https://api.stripe.com",
                "https://api.retellai.com",  # Retell API
                "wss://*",  # WebSocket connections
                "ws://*"
            ]
        }
        
        talisman = Talisman(
            app,
            force_https=True,
            strict_transport_security=True,
            strict_transport_security_max_age=31536000,  # 1 year
            session_cookie_secure=True,
            session_cookie_http_only=True,
            content_security_policy=csp,
            content_security_policy_nonce_in=['script-src'],
            feature_policy={
                'geolocation': "'none'",
                'microphone': "'none'",
                'camera': "'none'"
            }
        )
        print("[SECURITY] Flask-Talisman enabled: HTTPS enforcement & security headers active")

    # Initialize SocketIO
    # For development, use threading mode (works without Redis)
    # For production, use eventlet with Redis message queue
    socketio_options = {
        'cors_allowed_origins': app.config['CORS_ORIGINS'],
        'logger': app.config.get('SOCKETIO_LOGGER', False),
        'engineio_logger': app.config.get('SOCKETIO_ENGINEIO_LOGGER', False)
    }
    
    # Try to use Redis message queue if available (for production)
    try:
        redis_test = redis.from_url(app.config['REDIS_URL'])
        redis_test.ping()
        socketio_options['message_queue'] = app.config['REDIS_URL']
        socketio_options['async_mode'] = 'eventlet'
        print("[OK] Redis connected - using eventlet with message queue")
    except Exception as e:
        # Fall back to threading mode for development
        socketio_options['async_mode'] = 'threading'
        print(f"[INFO] Running in development mode (threading) - Redis not available")
    
    socketio.init_app(app, **socketio_options)

    # Initialize Redis client if available
    global redis_client
    try:
        redis_client = redis.from_url(app.config['REDIS_URL'])
        redis_client.ping()
    except Exception:
        redis_client = None
        print("[WARN] Redis not available - session storage will use default")

    # Configure Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # User loader for Flask-Login
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.booking import booking_bp
    from app.routes.admin import admin_bp
    from app.routes.chat import chat_bp
    from app.routes.sitemap import seo_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(booking_bp, url_prefix='/booking')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(seo_bp)

    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        from flask import render_template
        return render_template('errors/403.html'), 403

    # Create database tables
    with app.app_context():
        db.create_all()

    # Register custom template filters
    @app.template_filter('datetime')
    def format_datetime(value, format='%B %d, %Y at %I:%M %p'):
        """Format a datetime object for display"""
        if value is None:
            return ""
        return value.strftime(format)

    @app.template_filter('currency')
    def format_currency(value):
        """Format a number as currency"""
        if value is None:
            return "$0.00"
        return f"${value:,.2f}"

    # Context processors
    @app.context_processor
    def utility_processor():
        """Make utility functions available in templates"""
        return {
            'app_name': app.config['APP_NAME'],
            'support_email': app.config['SUPPORT_EMAIL']
        }

    return app
