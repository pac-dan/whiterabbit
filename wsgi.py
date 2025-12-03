"""
WSGI Entry Point for Production Deployment

This file is the production entry point for the Momentum Clips application.
Use this with gunicorn or other WSGI servers.

Production deployment:
    gunicorn wsgi:app

With eventlet worker (for SocketIO):
    gunicorn --worker-class eventlet -w 1 wsgi:app

Local testing (development only):
    python wsgi.py
"""

import os
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Fix Redis URL format if needed
redis_url = os.getenv('REDIS_URL', '')
if redis_url and not redis_url.startswith('redis://') and not redis_url.startswith('rediss://'):
    logger.warning(f"REDIS_URL format issue detected. Original: {redis_url}")
    # If it looks like host:port, try to fix it
    if ':' in redis_url and not '://' in redis_url:
        # Assume it needs redis:// prefix
        fixed_url = f"redis://{redis_url}/0"
        os.environ['REDIS_URL'] = fixed_url
        logger.info(f"Fixed REDIS_URL to: {fixed_url}")

# Fix DATABASE_URL format for SQLAlchemy 2.0+ (postgres:// -> postgresql://)
database_url = os.getenv('DATABASE_URL', '')
if database_url and database_url.startswith('postgres://'):
    fixed_url = database_url.replace('postgres://', 'postgresql://', 1)
    os.environ['DATABASE_URL'] = fixed_url
    logger.info("Fixed DATABASE_URL format for SQLAlchemy 2.0+")

logger.info("Starting Momentum Clips application...")
logger.info(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
logger.info(f"Port: {os.getenv('PORT', '5000')}")

try:
    from app import create_app, socketio
    
    # Create the Flask application
    app = create_app()
    logger.info("Application created successfully!")
    
except Exception as e:
    logger.error(f"Failed to create application: {str(e)}", exc_info=True)
    raise

if __name__ == '__main__':
    # This block only runs when executing: python wsgi.py
    # For development/testing only - production should use gunicorn
    print("=" * 70)
    print("[WARNING] Running in development mode")
    print("=" * 70)
    print("For production, use: gunicorn --worker-class eventlet -w 1 wsgi:app")
    print("=" * 70)
    
    # Run with SocketIO for development
    socketio.run(
        app,
        debug=app.config.get('DEBUG', False),
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000))
    )

