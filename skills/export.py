# -*- coding: utf-8 -*-
"""
Export Skill

Provides data export operations for AI agents:
- Export to various formats
- Generate dataset statistics
"""
import os
from typing import Dict, Any, Optional
from .base import BaseSkill


class ExportSkill(BaseSkill):
    """Dataset export skill for AI agents"""

    def get_info(self) -> Dict[str, Any]:
        return {
            'name': 'ExportSkill',
            'description': 'Export datasets in various formats',
            'methods': {
                'export_dataset': {
                    'description': 'Export dataset to specified format',
                    'params': {
                        'project_id': 'int - Project ID',
                        'format': 'str - yolo/coco/voc/createml/csv',
                        'output_dir': 'str - Output directory path',
                        'include_augmentation': 'bool - Apply augmentation'
                    }
                },
                'get_export_formats': {
                    'description': 'List available export formats',
                    'params': {}
                },
                'preview_export': {
                    'description': 'Preview export without writing files',
                    'params': {
                        'project_id': 'int - Project ID',
                        'format': 'str - Export format'
                    }
                }
            }
        }

    def get_export_formats(self) -> Dict[str, Any]:
        """Get available export formats"""
        return {
            'formats': [
                {
                    'id': 'yolo',
                    'name': 'YOLO',
                    'description': 'YOLO format (YOLOv5/v8/v11)',
                    'extensions': ['.txt', '.yaml']
                },
                {
                    'id': 'coco',
                    'name': 'COCO JSON',
                    'description': 'COCO format for Detectron2/MMDetection',
                    'extensions': ['.json']
                },
                {
                    'id': 'voc',
                    'name': 'Pascal VOC',
                    'description': 'Pascal VOC XML format',
                    'extensions': ['.xml']
                },
                {
                    'id': 'createml',
                    'name': 'CreateML',
                    'description': 'Apple CreateML JSON format',
                    'extensions': ['.json']
                },
                {
                    'id': 'csv',
                    'name': 'CSV',
                    'description': 'Simple CSV format',
                    'extensions': ['.csv']
                }
            ]
        }

    def export_dataset(
        self,
        project_id: int,
        format: str = 'yolo',
        output_dir: Optional[str] = None,
        include_augmentation: bool = False,
        augmentation_config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Export dataset to specified format

        Args:
            project_id: Project ID
            format: Export format (yolo/coco/voc/createml/csv)
            output_dir: Output directory (uses default if None)
            include_augmentation: Whether to apply augmentation
            augmentation_config: Augmentation settings

        Returns:
            Export result with file path
        """
        def _export():
            from app.models import Project
            from app.services.exporter import DatasetExporter

            project = Project.query.get(project_id)
            if not project:
                return {'error': f'Project {project_id} not found'}

            # Set output directory
            export_folder = output_dir or os.path.join(self.data_dir, 'exports')
            os.makedirs(export_folder, exist_ok=True)

            # Create exporter and export
            exporter = DatasetExporter(project, export_folder)

            try:
                zip_path = exporter.export(
                    format_type=format,
                    include_augmentation=include_augmentation,
                    augmentation_config=augmentation_config or {}
                )

                self.log_action('export_dataset', {
                    'project_id': project_id,
                    'format': format,
                    'output': zip_path
                })

                return {
                    'success': True,
                    'project_id': project_id,
                    'format': format,
                    'file_path': zip_path,
                    'file_size': os.path.getsize(zip_path)
                }

            except Exception as e:
                return {'error': str(e)}

        return self.execute_in_context(_export)

    def preview_export(self, project_id: int, format: str = 'yolo') -> Dict[str, Any]:
        """
        Preview what would be exported without writing files

        Args:
            project_id: Project ID
            format: Export format

        Returns:
            Preview of export contents
        """
        def _preview():
            from app.models import Project

            project = Project.query.get(project_id)
            if not project:
                return {'error': f'Project {project_id} not found'}

            classes = [c.to_dict() for c in project.label_classes.all()]

            # Count images by split
            splits = {'train': 0, 'val': 0, 'test': 0}
            total_annotations = 0

            for image in project.images.all():
                split = image.split or 'train'
                splits[split] = splits.get(split, 0) + 1
                total_annotations += image.annotations.count()

            return {
                'project_id': project_id,
                'project_name': project.name,
                'format': format,
                'classes': classes,
                'class_count': len(classes),
                'image_splits': splits,
                'total_images': sum(splits.values()),
                'total_annotations': total_annotations,
                'estimated_files': self._estimate_files(format, splits)
            }

        return self.execute_in_context(_preview)

    def _estimate_files(self, format: str, splits: Dict[str, int]) -> Dict[str, int]:
        """Estimate number of files that will be generated"""
        total_images = sum(splits.values())

        if format == 'yolo':
            return {
                'images': total_images,
                'label_files': total_images,
                'config_files': 2  # data.yaml, classes.txt
            }
        elif format == 'coco':
            return {
                'images': total_images,
                'json_files': 1
            }
        elif format == 'voc':
            return {
                'images': total_images,
                'xml_files': total_images
            }
        elif format == 'csv':
            return {
                'images': total_images,
                'csv_files': 1
            }
        else:
            return {'images': total_images}
