# -*- coding: utf-8 -*-
"""
API Routes Registration
"""
from flask import Flask


def register_blueprints(app: Flask):
    """Register all API blueprints"""
    from .auth import auth_bp
    from .projects import projects_bp
    from .images import images_bp
    from .annotations import annotations_bp
    from .export import export_bp
    from .qrcode import qr_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(projects_bp, url_prefix='/api/projects')
    app.register_blueprint(images_bp, url_prefix='/api/images')
    app.register_blueprint(annotations_bp, url_prefix='/api/annotations')
    app.register_blueprint(export_bp, url_prefix='/api/export')
    app.register_blueprint(qr_bp, url_prefix='/api/qr')
