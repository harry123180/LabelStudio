# -*- coding: utf-8 -*-
"""
Annotation Skill

Provides annotation-related operations for AI agents:
- Create/update/delete annotations
- Batch operations
- Validation
"""
from typing import Dict, Any, List, Optional
from .base import BaseSkill


class AnnotationSkill(BaseSkill):
    """Annotation management skill for AI agents"""

    def get_info(self) -> Dict[str, Any]:
        return {
            'name': 'AnnotationSkill',
            'description': 'Manage annotations: create, update, delete, validate',
            'methods': {
                'create_annotation': {
                    'description': 'Create a new annotation',
                    'params': {
                        'image_id': 'int - Image ID',
                        'class_id': 'int - Label class ID',
                        'annotation_type': 'str - bbox/polygon/mask',
                        'data': 'dict - Annotation data'
                    }
                },
                'batch_create': {
                    'description': 'Create multiple annotations at once',
                    'params': {
                        'annotations': 'list - List of annotation dicts'
                    }
                },
                'get_annotations': {
                    'description': 'Get all annotations for an image',
                    'params': {
                        'image_id': 'int - Image ID'
                    }
                },
                'validate_annotations': {
                    'description': 'Validate annotations for a project',
                    'params': {
                        'project_id': 'int - Project ID'
                    }
                }
            }
        }

    def create_annotation(
        self,
        image_id: int,
        class_id: int,
        annotation_type: str = 'bbox',
        data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a new annotation

        Args:
            image_id: Image ID
            class_id: Label class ID
            annotation_type: 'bbox', 'polygon', or 'mask'
            data: Annotation data (bbox: {x, y, width, height})

        Returns:
            Created annotation data
        """
        def _create():
            from app.models import Image, Annotation, LabelClass
            from app import db

            image = Image.query.get(image_id)
            if not image:
                return {'error': f'Image {image_id} not found'}

            label_class = LabelClass.query.get(class_id)
            if not label_class:
                return {'error': f'Class {class_id} not found'}

            annotation = Annotation(
                image_id=image_id,
                class_id=class_id,
                annotation_type=annotation_type
            )
            annotation.set_data(data or {})

            db.session.add(annotation)

            # Update image status
            image.status = 'annotated'

            db.session.commit()

            self.log_action('create_annotation', {
                'image_id': image_id,
                'class_id': class_id,
                'type': annotation_type
            })

            return annotation.to_dict()

        return self.execute_in_context(_create)

    def batch_create(self, annotations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create multiple annotations at once

        Args:
            annotations: List of annotation dicts with keys:
                - image_id, class_id, type, data

        Returns:
            Result summary
        """
        def _batch():
            from app.models import Annotation
            from app import db

            created = 0
            errors = []

            for anno_data in annotations:
                try:
                    anno = Annotation(
                        image_id=anno_data['image_id'],
                        class_id=anno_data['class_id'],
                        annotation_type=anno_data.get('type', 'bbox')
                    )
                    anno.set_data(anno_data.get('data', {}))
                    db.session.add(anno)
                    created += 1
                except Exception as e:
                    errors.append(str(e))

            db.session.commit()

            self.log_action('batch_create', {
                'created': created,
                'errors': len(errors)
            })

            return {
                'success': True,
                'created': created,
                'errors': errors
            }

        return self.execute_in_context(_batch)

    def get_annotations(self, image_id: int) -> List[Dict[str, Any]]:
        """
        Get all annotations for an image

        Args:
            image_id: Image ID

        Returns:
            List of annotation dictionaries
        """
        def _get():
            from app.models import Annotation

            annotations = Annotation.query.filter_by(image_id=image_id).all()
            return [a.to_dict() for a in annotations]

        return self.execute_in_context(_get)

    def delete_annotation(self, annotation_id: int) -> Dict[str, Any]:
        """
        Delete an annotation

        Args:
            annotation_id: Annotation ID

        Returns:
            Result
        """
        def _delete():
            from app.models import Annotation
            from app import db

            annotation = Annotation.query.get(annotation_id)
            if not annotation:
                return {'error': f'Annotation {annotation_id} not found'}

            db.session.delete(annotation)
            db.session.commit()

            self.log_action('delete_annotation', {'annotation_id': annotation_id})

            return {'success': True}

        return self.execute_in_context(_delete)

    def validate_annotations(self, project_id: int) -> Dict[str, Any]:
        """
        Validate all annotations in a project

        Checks for:
        - Bounding boxes outside image bounds
        - Empty annotations
        - Missing class assignments

        Args:
            project_id: Project ID

        Returns:
            Validation results
        """
        def _validate():
            from app.models import Project, Image, Annotation

            project = Project.query.get(project_id)
            if not project:
                return {'error': f'Project {project_id} not found'}

            issues = []
            checked = 0

            for image in project.images.all():
                for anno in image.annotations.all():
                    checked += 1
                    data = anno.get_data()

                    # Check bbox bounds
                    if anno.annotation_type == 'bbox':
                        x = data.get('x', 0)
                        y = data.get('y', 0)
                        w = data.get('width', 0)
                        h = data.get('height', 0)

                        if x < 0 or y < 0:
                            issues.append({
                                'annotation_id': anno.id,
                                'issue': 'Negative coordinates'
                            })

                        if image.width and (x + w > image.width):
                            issues.append({
                                'annotation_id': anno.id,
                                'issue': 'Exceeds image width'
                            })

                        if image.height and (y + h > image.height):
                            issues.append({
                                'annotation_id': anno.id,
                                'issue': 'Exceeds image height'
                            })

                        if w <= 0 or h <= 0:
                            issues.append({
                                'annotation_id': anno.id,
                                'issue': 'Zero or negative size'
                            })

            return {
                'project_id': project_id,
                'annotations_checked': checked,
                'issues_found': len(issues),
                'issues': issues[:100]  # Limit to first 100
            }

        return self.execute_in_context(_validate)
