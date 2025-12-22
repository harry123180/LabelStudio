# -*- coding: utf-8 -*-
"""
Export Routes
"""
from flask import Blueprint, request, jsonify, send_file, current_app
from app.models import Project
from app.services.exporter import DatasetExporter
import os

export_bp = Blueprint('export', __name__)


@export_bp.route('/project/<int:project_id>', methods=['POST'])
def export_project(project_id):
    """Export project dataset"""
    project = Project.query.get_or_404(project_id)
    data = request.get_json()

    format_type = data.get('format', 'yolo')  # yolo, coco, voc, createml, csv
    include_augmentation = data.get('augmentation', False)
    augmentation_config = data.get('augmentation_config', {})

    exporter = DatasetExporter(project, current_app.config['EXPORT_FOLDER'])

    try:
        zip_path = exporter.export(
            format_type=format_type,
            include_augmentation=include_augmentation,
            augmentation_config=augmentation_config
        )

        return send_file(
            zip_path,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'{project.name}_{format_type}.zip'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@export_bp.route('/formats', methods=['GET'])
def list_formats():
    """List available export formats"""
    return jsonify({
        'formats': [
            {'id': 'yolo', 'name': 'YOLO', 'description': 'YOLOv5/v8/v11 format'},
            {'id': 'coco', 'name': 'COCO JSON', 'description': 'COCO format for Detectron2/MMDetection'},
            {'id': 'voc', 'name': 'Pascal VOC', 'description': 'Pascal VOC XML format'},
            {'id': 'createml', 'name': 'CreateML', 'description': 'Apple CreateML JSON format'},
            {'id': 'csv', 'name': 'CSV', 'description': 'Simple CSV format'}
        ]
    })
