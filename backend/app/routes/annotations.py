# -*- coding: utf-8 -*-
"""
Annotation Routes
"""
from flask import Blueprint, request, jsonify
from app.models import Annotation, Image, LabelClass
from app.extensions import db

annotations_bp = Blueprint('annotations', __name__)


@annotations_bp.route('/image/<int:image_id>', methods=['GET'])
def list_annotations(image_id):
    """List all annotations for an image"""
    image = Image.query.get_or_404(image_id)
    annotations = Annotation.query.filter_by(image_id=image_id).all()
    return jsonify([a.to_dict() for a in annotations])


@annotations_bp.route('/image/<int:image_id>', methods=['POST'])
def save_annotations(image_id):
    """Save annotations for an image (batch save - replaces existing)"""
    image = Image.query.get_or_404(image_id)
    data = request.get_json()
    annotations_data = data.get('annotations', [])
    annotated_by = data.get('annotated_by')  # Username of annotator

    # Delete existing annotations
    Annotation.query.filter_by(image_id=image_id).delete()

    # Create new annotations
    for anno_data in annotations_data:
        # Support both class_id and label_class_id
        class_id = anno_data.get('label_class_id') or anno_data.get('class_id')

        annotation = Annotation(
            image_id=image_id,
            class_id=class_id,
            annotation_type=anno_data.get('annotation_type', 'bbox'),
            user_id=anno_data.get('user_id')
        )
        annotation.set_data(anno_data.get('data', {}))
        db.session.add(annotation)

    # Update image status and annotator
    if annotations_data:
        image.status = 'annotated'
        if annotated_by:
            image.annotated_by = annotated_by
    else:
        image.status = 'pending'

    db.session.commit()

    return jsonify({
        'success': True,
        'count': len(annotations_data)
    })


@annotations_bp.route('/<int:annotation_id>', methods=['GET'])
def get_annotation(annotation_id):
    """Get a single annotation"""
    annotation = Annotation.query.get_or_404(annotation_id)
    return jsonify(annotation.to_dict())


@annotations_bp.route('/<int:annotation_id>', methods=['PUT'])
def update_annotation(annotation_id):
    """Update an annotation"""
    annotation = Annotation.query.get_or_404(annotation_id)
    data = request.get_json()

    if 'class_id' in data:
        annotation.class_id = data['class_id']
    if 'label_class_id' in data:
        annotation.class_id = data['label_class_id']
    if 'data' in data:
        annotation.set_data(data['data'])
    if 'annotation_type' in data:
        annotation.annotation_type = data['annotation_type']

    db.session.commit()
    return jsonify(annotation.to_dict())


@annotations_bp.route('/<int:annotation_id>', methods=['DELETE'])
def delete_annotation(annotation_id):
    """Delete an annotation"""
    annotation = Annotation.query.get_or_404(annotation_id)
    db.session.delete(annotation)
    db.session.commit()
    return jsonify({'success': True})


@annotations_bp.route('/project/<int:project_id>/stats', methods=['GET'])
def annotation_stats(project_id):
    """Get annotation statistics for a project"""
    from sqlalchemy import func

    # Count by class
    class_counts = db.session.query(
        LabelClass.name,
        func.count(Annotation.id)
    ).join(
        Annotation, LabelClass.id == Annotation.class_id
    ).join(
        Image, Annotation.image_id == Image.id
    ).filter(
        Image.project_id == project_id
    ).group_by(LabelClass.name).all()

    # Total counts
    total_images = Image.query.filter_by(project_id=project_id).count()
    annotated_images = Image.query.filter_by(
        project_id=project_id,
        status='annotated'
    ).count()
    total_annotations = db.session.query(func.count(Annotation.id)).join(
        Image
    ).filter(Image.project_id == project_id).scalar() or 0

    return jsonify({
        'total_images': total_images,
        'annotated_images': annotated_images,
        'total_annotations': total_annotations,
        'by_class': {name: count for name, count in class_counts}
    })
