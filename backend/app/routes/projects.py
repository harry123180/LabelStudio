# -*- coding: utf-8 -*-
"""
Project Routes
"""
from flask import Blueprint, request, jsonify
from app.models import Project, LabelClass
from app import db

projects_bp = Blueprint('projects', __name__)


@projects_bp.route('', methods=['GET'])
def list_projects():
    """List all projects"""
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return jsonify([p.to_dict() for p in projects])


@projects_bp.route('', methods=['POST'])
def create_project():
    """Create a new project"""
    data = request.get_json()

    project = Project(
        name=data.get('name'),
        description=data.get('description'),
        project_type=data.get('project_type', 'object_detection'),
        train_ratio=data.get('train_ratio', 0.7),
        val_ratio=data.get('val_ratio', 0.2),
        test_ratio=data.get('test_ratio', 0.1)
    )
    db.session.add(project)
    db.session.commit()

    return jsonify(project.to_dict()), 201


@projects_bp.route('/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """Get project details"""
    project = Project.query.get_or_404(project_id)
    return jsonify(project.to_dict())


@projects_bp.route('/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    """Update project"""
    project = Project.query.get_or_404(project_id)
    data = request.get_json()

    if 'name' in data:
        project.name = data['name']
    if 'description' in data:
        project.description = data['description']
    if 'train_ratio' in data:
        project.train_ratio = data['train_ratio']
    if 'val_ratio' in data:
        project.val_ratio = data['val_ratio']
    if 'test_ratio' in data:
        project.test_ratio = data['test_ratio']

    db.session.commit()
    return jsonify(project.to_dict())


@projects_bp.route('/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete project"""
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return jsonify({'success': True})


@projects_bp.route('/<int:project_id>/classes', methods=['GET'])
def list_classes(project_id):
    """List label classes for a project"""
    project = Project.query.get_or_404(project_id)
    classes = project.label_classes.all()
    return jsonify([c.to_dict() for c in classes])


@projects_bp.route('/<int:project_id>/classes', methods=['POST'])
def create_class(project_id):
    """Create a new label class"""
    project = Project.query.get_or_404(project_id)
    data = request.get_json()

    label_class = LabelClass(
        project_id=project.id,
        name=data.get('name'),
        color=data.get('color', '#FF0000'),
        description=data.get('description'),
        shortcut_key=data.get('shortcut_key')
    )
    db.session.add(label_class)
    db.session.commit()

    return jsonify(label_class.to_dict()), 201
