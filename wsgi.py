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
from app import create_app, socketio

# Create the Flask application
app = create_app()

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

