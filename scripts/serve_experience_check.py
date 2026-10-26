"""Local-only empty-database server for acceptance checks; never imported by wsgi."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from config import TestingConfig

if __name__ == '__main__':
    # Recycled in-memory connections lose their schema after five minutes.
    TestingConfig.SQLALCHEMY_ENGINE_OPTIONS = {'pool_pre_ping': True, 'pool_recycle': -1}
    app = create_app('testing')
    app.run(host='127.0.0.1', port=5002, debug=False, use_reloader=False)
