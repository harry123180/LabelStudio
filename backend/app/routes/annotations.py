# -*- coding: utf-8 -*-
"""
Annotation Routes
"""
from flask import Blueprint, request, jsonify
from app.models import Annotation, Image
from app import db

annotations_bp = Blueprint('annotations', __name__)


@annotations_bp.route('/image/<int:image_id>', methods=['GET'])
def list_annotations(image_id):
    """List all annotations for an image"""
    image = Image.query.get_or_404(image_id)
    annotations = image.annotations.all()
    return jsonify([a.to_dict() for a in annotations])


@annotations_bp.route('/image/<int:image_id>', methods=['POST'])
def create_annotation(image_id):
    """Create a new annotation"""
    image = Image.query.get_or_404(image_id)
    data = request.get_json()

    annotation = Annotation(
        image_id=image.id,
        class_id=data.get('class_id'),
        annotation_type=data.get('type', 'bbox'),
        user_id=data.get('user_id')
    )
    annotation.set_data(data.get('data', {}))

    db.session.add(annotation)

    # Update image status
    image.status = 'annotated'

    db.session.commit()
    return jsonify(annotation.to_dict()), 201


@annotations_bp.route('/<int:annotation_id>', methods=['PUT'])
def update_annotation(annotation_id):
    """Update an annotation"""
    annotation = Annotation.query.get_or_404(annotation_id)
    data = request.get_json()

    if 'class_id' in data:
        annotation.class_id = data['class_id']
    if 'data' in data:
        annotation.set_data(data['data'])

    db.session.commit()
    return jsonify(annotation.to_dict())


@annotations_bp.route('/<int:annotation_id>', methods=['DELETE'])
def delete_annotation(annotation_id):
    """Delete an annotation"""
    annotation = Annotation.query.get_or_404(annotation_id)
    db.session.delete(annotation)
    db.session.commit()
    return jsonify({'success': True})
