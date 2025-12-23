# -*- coding: utf-8 -*-
"""
LabelStudio Backend Application Factory
"""
from flask import Flask, send_from_directory, jsonify
import os
import sys

from app.extensions import db, cors


def get_resource_path(relative_path: str) -> str:
    """Get resource path, supporting PyInstaller packaging"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), '..', '..', relative_path)


def get_data_dir() -> str:
    """Get data directory (beside exe when packaged)"""
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    data_dir = os.path.join(base_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def create_app(config_name: str = 'default') -> Flask:
    """Application factory"""
    # Static files path (Vue build output)
    static_folder = get_resource_path('dist')

    # Create app
    app = Flask(__name__,
                static_folder=static_folder if os.path.exists(static_folder) else None,
                static_url_path='')

    # Load config
    from app.config import config as app_config
    app.config.from_object(app_config[config_name])

    # Data directory
    data_dir = get_data_dir()
    app.config['DATA_DIR'] = data_dir
    app.config['UPLOAD_FOLDER'] = os.path.join(data_dir, 'uploads')
    app.config['EXPORT_FOLDER'] = os.path.join(data_dir, 'exports')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(data_dir, 'labelstudio.db')}"

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['EXPORT_FOLDER'], exist_ok=True)

    # Initialize extensions
    cors.init_app(app)
    db.init_app(app)

    # Register blueprints
    from app.routes import register_blueprints
    register_blueprints(app)

    # Frontend routes: return index.html for non-API requests (SPA)
    @app.route('/')
    def index():
        if app.static_folder and os.path.exists(os.path.join(app.static_folder, 'index.html')):
            return send_from_directory(app.static_folder, 'index.html')
        return jsonify({
            'name': 'LabelStudio API',
            'version': '0.1.0',
            'status': 'running',
            'message': 'Frontend not built. Run: cd frontend && npm run build'
        })

    @app.route('/<path:path>')
    def serve_static(path):
        if path.startswith('api/'):
            return jsonify({'error': 'Not Found'}), 404

        if app.static_folder:
            file_path = os.path.join(app.static_folder, path)
            if os.path.isfile(file_path):
                return send_from_directory(app.static_folder, path)
            # SPA fallback
            index_path = os.path.join(app.static_folder, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(app.static_folder, 'index.html')

        return jsonify({'error': 'Not Found'}), 404

    return app
