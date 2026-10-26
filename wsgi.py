"""
WSGI Entry Point for Production Deployment

This file is the production entry point for the Momentum Clips application.
Use this with gunicorn or other WSGI servers.

Production deployment:
    gunicorn wsgi:app

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

logger.info("Starting Momentum Clips application...")
logger.info(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
logger.info(f"Port: {os.getenv('PORT', '5000')}")

from app import create_app

# Create the Flask application (top level, so Vercel's Flask detection finds it)
app = create_app()
logger.info("Application created successfully!")

if __name__ == '__main__':
    # This block only runs when executing: python wsgi.py
    # For development/testing only - production should use gunicorn
    print("=" * 70)
    print("[WARNING] Running in development mode")
    print("=" * 70)
    print("For production, use: gunicorn wsgi:app")
    print("=" * 70)

    app.run(
        debug=app.config.get('DEBUG', False),
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000))
    )

