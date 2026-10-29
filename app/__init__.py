from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_compress import Compress
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from config import get_config
from app.services.email_service import mail

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
compress = Compress()
csrf = CSRFProtect()
talisman = None  # Will be initialized conditionally in create_app

# Rate limiter will be initialized in create_app
limiter = None


def create_app(config_name=None):
    """Application factory pattern"""
    import logging
    import sys
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("[1/10] Creating Flask app...")
    # Vercel's filesystem is read-only except /tmp; the SQLite fallback lives in the instance folder
    import os
    app = Flask(__name__, instance_path='/tmp/instance' if os.getenv('VERCEL') else None)

    # Load configuration
    logger.info("[2/10] Loading configuration...")
    if config_name:
        from config import config_dict
        app.config.from_object(config_dict[config_name])
    else:
        app.config.from_object(get_config())
    
    # Disable template caching for development
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

    @app.after_request
    def cache_experience_assets(response):
        from flask import request
        if request.path.startswith(('/static/vendor/', '/static/experience/')) and response.status_code in (200, 206):
            response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
        return response

    # Initialize extensions with app
    logger.info("[3/10] Initializing database...")
    db.init_app(app)
    logger.info("[3/10] Initializing migrations...")
    migrate.init_app(app, db)
    logger.info("[3/10] Initializing login manager...")
    login_manager.init_app(app)
    logger.info("[3/10] Initializing bcrypt...")
    bcrypt.init_app(app)
    logger.info("[3/10] Initializing CSRF...")
    csrf.init_app(app)  # Initialize CSRF protection
    logger.info("[3/10] Initializing mail...")
    mail.init_app(app)
    logger.info("[3/10] Initializing CORS...")
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # CSRF Protection - now properly initialized
    # Note: Individual routes can be exempted using @csrf.exempt decorator
    
    # Initialize rate limiter with in-memory storage
    # (on Vercel each function instance keeps its own counts)
    logger.info("[4/10] Initializing rate limiter...")
    global limiter
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"]
    )
    app.logger.info("[OK] Rate limiter using memory storage")
    
    # Initialize compression for better performance & SEO
    compress.init_app(app)
    
    # Make config variables available in templates
    @app.context_processor
    def inject_config():
        return {
            'support_email': app.config.get('SUPPORT_EMAIL', '')
        }

    from app.experience.public import public_context
    app.context_processor(public_context)
    
    # Initialize Flask-Talisman for production security
    # Only enforce HTTPS in production
    if not app.config.get('DEBUG', False):
        global talisman
        # Content Security Policy
        csp = {
            'default-src': ["'self'"],
            'script-src': [
                "'self'",
                "'unsafe-inline'",  # Required for some inline scripts
                "https://js.stripe.com",
                "https://player.vimeo.com",
                "https://assets.calendly.com",
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
                "https://player.vimeo.com",
                "https://calendly.com",
                "https://www.youtube-nocookie.com"
            ],
            'connect-src': [
                "'self'",
                "https://api.stripe.com",
                "wss://*",  # WebSocket connections (Retell voice widget)
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
        app.logger.info("Flask-Talisman enabled: HTTPS enforcement & security headers active")

    # Configure Flask-Login
    logger.info("[6/10] Configuring Flask-Login...")
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # User loader for Flask-Login
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    logger.info("[7/10] Registering blueprints...")
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.sitemap import seo_bp
    from app.routes.payment import payment_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(payment_bp, url_prefix='/payment')
    app.register_blueprint(seo_bp)

    # Register error handlers
    logger.info("[8/10] Registering error handlers...")
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

    from app.models.inquiry import Inquiry
    from app.commands import register_commands
    register_commands(app)

    # Create database tables
    logger.info("[9/10] Creating database tables...")
    with app.app_context():
        db.create_all()
    logger.info("[9/10] Database tables created successfully")

    # Context processor for global template variables
    @app.context_processor
    def inject_globals():
        """Inject global variables into all templates"""
        return {
            'SOCIAL_INSTAGRAM': app.config.get('SOCIAL_INSTAGRAM', 'https://www.instagram.com/momentumclipsbansko/'),
            'SOCIAL_TIKTOK': app.config.get('SOCIAL_TIKTOK', 'https://www.tiktok.com/@momentumclipsbansko'),
            'SOCIAL_FACEBOOK': app.config.get('SOCIAL_FACEBOOK', 'https://facebook.com/momentumclips'),
            'SOCIAL_LINKEDIN': app.config.get('SOCIAL_LINKEDIN', 'https://linkedin.com/company/momentumclips'),
            'SOCIAL_TWITTER': app.config.get('SOCIAL_TWITTER', 'https://twitter.com/momentumclips'),
            'SOCIAL_YOUTUBE': app.config.get('SOCIAL_YOUTUBE', 'https://youtube.com/@momentumclipsbansko'),
        }
    
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
            return "?0.00"
        return f"?{value:,.2f}"

    # Context processors
    logger.info("[10/10] Setting up template context processors...")
    @app.context_processor
    def utility_processor():
        """Make utility functions available in templates"""
        return {
            'app_name': app.config['APP_NAME'],
            'support_email': app.config['SUPPORT_EMAIL']
        }

    logger.info("✅ Application created successfully!")
    return app
