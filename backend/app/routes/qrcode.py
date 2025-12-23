# -*- coding: utf-8 -*-
"""
QR Code Routes for Mobile Upload
"""
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.models import Image, Project
from app.utils.network import get_local_ip
from app.extensions import db
from PIL import Image as PILImage
import qrcode
import io
import base64
import os
import uuid

qr_bp = Blueprint('qrcode', __name__)


@qr_bp.route('/project/<int:project_id>', methods=['GET'])
def generate_qr(project_id):
    """Generate QR code for project upload page"""
    project = Project.query.get_or_404(project_id)

    local_ip = get_local_ip()
    port = current_app.config.get('PORT', 5000)

    # Upload page URL
    upload_url = f"http://{local_ip}:{port}/upload/{project_id}"

    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(upload_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode()

    return jsonify({
        'qrcode': f'data:image/png;base64,{img_base64}',
        'url': upload_url,
        'project_id': project_id,
        'project_name': project.name
    })


@qr_bp.route('/project/<int:project_id>/quick-upload', methods=['POST'])
def quick_upload(project_id):
    """Mobile quick upload (no login required)"""
    project = Project.query.get_or_404(project_id)

    nickname = request.form.get('nickname', '匿名')
    files = request.files.getlist('images')

    if not files:
        return jsonify({'error': 'No images provided'}), 400

    uploaded = []

    for file in files:
        if file and file.filename:
            # Generate unique filename
            ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
            filename = f"{uuid.uuid4().hex}.{ext}"

            # Save file
            project_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(project_id))
            os.makedirs(project_folder, exist_ok=True)
            file_path = os.path.join(project_folder, filename)
            file.save(file_path)

            # Get image dimensions
            try:
                with PILImage.open(file_path) as img:
                    width, height = img.size
            except Exception:
                width, height = None, None

            # Create database record
            image = Image(
                project_id=project.id,
                filename=filename,
                original_filename=secure_filename(file.filename),
                file_path=file_path,
                width=width,
                height=height,
                file_size=os.path.getsize(file_path),
                uploader_name=nickname,
                upload_source='mobile'
            )
            db.session.add(image)
            uploaded.append({
                'filename': filename,
                'uploader': nickname
            })

    db.session.commit()

    return jsonify({
        'success': True,
        'uploaded': len(uploaded),
        'files': uploaded
    })


@qr_bp.route('/project/<int:project_id>/stats', methods=['GET'])
def upload_stats(project_id):
    """Get upload statistics for a project"""
    project = Project.query.get_or_404(project_id)

    total = project.images.count()
    mobile = project.images.filter_by(upload_source='mobile').count()

    # Get unique uploaders
    uploaders = db.session.query(Image.uploader_name).filter(
        Image.project_id == project_id,
        Image.uploader_name.isnot(None)
    ).distinct().count()

    return jsonify({
        'total_images': total,
        'mobile_uploads': mobile,
        'unique_uploaders': uploaders
    })
