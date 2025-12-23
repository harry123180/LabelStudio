# -*- coding: utf-8 -*-
"""
Image Routes
"""
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from app.models import Image, Project
from app.extensions import db
from PIL import Image as PILImage
import os
import uuid

images_bp = Blueprint('images', __name__)


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@images_bp.route('/project/<int:project_id>', methods=['GET'])
def list_images(project_id):
    """List all images in a project"""
    project = Project.query.get_or_404(project_id)
    images = project.images.order_by(Image.uploaded_at.desc()).all()
    return jsonify([img.to_dict() for img in images])


@images_bp.route('/project/<int:project_id>/upload', methods=['POST'])
def upload_images(project_id):
    """Upload images to a project"""
    project = Project.query.get_or_404(project_id)

    if 'images' not in request.files:
        return jsonify({'error': 'No images provided'}), 400

    files = request.files.getlist('images')
    uploaded = []

    for file in files:
        if file and allowed_file(file.filename):
            # Generate unique filename
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"

            # Save file
            project_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(project_id))
            os.makedirs(project_folder, exist_ok=True)
            file_path = os.path.join(project_folder, filename)
            file.save(file_path)

            # Get image dimensions
            with PILImage.open(file_path) as img:
                width, height = img.size

            # Create database record
            image = Image(
                project_id=project.id,
                filename=filename,
                original_filename=secure_filename(file.filename),
                file_path=file_path,
                width=width,
                height=height,
                file_size=os.path.getsize(file_path),
                upload_source='web'
            )
            db.session.add(image)
            uploaded.append(image)

    db.session.commit()

    return jsonify({
        'success': True,
        'uploaded': len(uploaded),
        'images': [img.to_dict() for img in uploaded]
    })


@images_bp.route('/<int:image_id>', methods=['GET'])
def get_image(image_id):
    """Get image details"""
    image = Image.query.get_or_404(image_id)
    return jsonify(image.to_dict())


@images_bp.route('/<int:image_id>/file', methods=['GET'])
def get_image_file(image_id):
    """Serve image file"""
    image = Image.query.get_or_404(image_id)
    directory = os.path.dirname(image.file_path)
    return send_from_directory(directory, image.filename)


@images_bp.route('/<int:image_id>/split', methods=['PUT'])
def update_split(image_id):
    """Update image dataset split"""
    image = Image.query.get_or_404(image_id)
    data = request.get_json()

    if 'split' in data:
        image.split = data['split']
    if 'locked' in data:
        image.split_locked = data['locked']

    db.session.commit()
    return jsonify(image.to_dict())


@images_bp.route('/<int:image_id>/status', methods=['PUT'])
def update_status(image_id):
    """Update image status"""
    image = Image.query.get_or_404(image_id)
    data = request.get_json()

    if 'status' in data:
        image.status = data['status']

    db.session.commit()
    return jsonify(image.to_dict())


@images_bp.route('/<int:image_id>', methods=['DELETE'])
def delete_image(image_id):
    """Delete an image"""
    image = Image.query.get_or_404(image_id)

    # Delete file if exists
    if os.path.exists(image.file_path):
        os.remove(image.file_path)

    db.session.delete(image)
    db.session.commit()
    return jsonify({'success': True})
