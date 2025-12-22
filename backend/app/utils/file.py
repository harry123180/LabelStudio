# -*- coding: utf-8 -*-
"""
File Utilities
"""
import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file, project_id: int) -> str:
    """
    Save uploaded file with unique filename

    Args:
        file: FileStorage object
        project_id: Project ID

    Returns:
        Saved filename
    """
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
    filename = f"{uuid.uuid4().hex}.{ext}"

    project_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(project_id))
    os.makedirs(project_folder, exist_ok=True)

    file_path = os.path.join(project_folder, filename)
    file.save(file_path)

    return filename
