# -*- coding: utf-8 -*-
"""
LabelStudio Backend Application Factory
"""
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
import sys

db = SQLAlchemy()


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

    app = Flask(__name__,
                static_folder=static_folder,
                static_url_path='')

    # Load config
    from .config import config
    app.config.from_object(config[config_name])

    # Initialize extensions
    CORS(app)
    db.init_app(app)

    # Data directory
    data_dir = get_data_dir()
    app.config['DATA_DIR'] = data_dir
    app.config['UPLOAD_FOLDER'] = os.path.join(data_dir, 'uploads')
    app.config['EXPORT_FOLDER'] = os.path.join(data_dir, 'exports')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(data_dir, 'labelstudio.db')}"

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['EXPORT_FOLDER'], exist_ok=True)

    # Register blueprints
    from .routes import register_blueprints
    register_blueprints(app)

    # Frontend routes: return index.html for non-API requests (SPA)
    @app.route('/')
    @app.route('/<path:path>')
    def serve_frontend(path=''):
        if path.startswith('api/'):
            return {'error': 'Not Found'}, 404

        file_path = os.path.join(app.static_folder, path)
        if os.path.isfile(file_path):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, 'index.html')

    return app
