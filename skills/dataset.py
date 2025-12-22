# -*- coding: utf-8 -*-
"""
Dataset Skill

Provides dataset management operations for AI agents:
- Split dataset into train/val/test
- Get dataset statistics
- Manage images
"""
import random
from typing import Dict, Any, List, Optional
from .base import BaseSkill


class DatasetSkill(BaseSkill):
    """Dataset management skill for AI agents"""

    def get_info(self) -> Dict[str, Any]:
        return {
            'name': 'DatasetSkill',
            'description': 'Manage datasets: split, statistics, image operations',
            'methods': {
                'split_dataset': {
                    'description': 'Split dataset into train/val/test sets',
                    'params': {
                        'project_id': 'int - Project ID',
                        'train': 'float - Training set ratio (0-1)',
                        'val': 'float - Validation set ratio (0-1)',
                        'test': 'float - Test set ratio (0-1)',
                        'strategy': 'str - random/sequential/stratified'
                    }
                },
                'get_statistics': {
                    'description': 'Get dataset statistics',
                    'params': {
                        'project_id': 'int - Project ID'
                    }
                },
                'list_images': {
                    'description': 'List all images in a project',
                    'params': {
                        'project_id': 'int - Project ID',
                        'split': 'str - Optional filter by split'
                    }
                }
            }
        }

    def split_dataset(
        self,
        project_id: int,
        train: float = 0.7,
        val: float = 0.2,
        test: float = 0.1,
        strategy: str = 'random'
    ) -> Dict[str, Any]:
        """
        Split dataset into train/val/test sets

        Args:
            project_id: Project ID
            train: Training set ratio
            val: Validation set ratio
            test: Test set ratio
            strategy: 'random', 'sequential', or 'stratified'

        Returns:
            Split results with counts per set
        """
        def _do_split():
            from app.models import Project, Image

            project = Project.query.get(project_id)
            if not project:
                return {'error': f'Project {project_id} not found'}

            # Get all unlocked images
            images = Image.query.filter_by(
                project_id=project_id,
                split_locked=False
            ).all()

            if not images:
                return {'error': 'No unlocked images to split'}

            # Validate ratios
            total = train + val + test
            if abs(total - 1.0) > 0.01:
                return {'error': f'Ratios must sum to 1.0, got {total}'}

            # Apply strategy
            if strategy == 'random':
                random.shuffle(images)
            elif strategy == 'sequential':
                images.sort(key=lambda x: x.uploaded_at)
            elif strategy == 'stratified':
                # Group by class, then split each group
                # Simplified: just shuffle for now
                random.shuffle(images)

            # Calculate split points
            n = len(images)
            train_end = int(n * train)
            val_end = train_end + int(n * val)

            # Assign splits
            counts = {'train': 0, 'val': 0, 'test': 0}
            for i, img in enumerate(images):
                if i < train_end:
                    img.split = 'train'
                    counts['train'] += 1
                elif i < val_end:
                    img.split = 'val'
                    counts['val'] += 1
                else:
                    img.split = 'test'
                    counts['test'] += 1

            # Update project ratios
            project.train_ratio = train
            project.val_ratio = val
            project.test_ratio = test

            from app import db
            db.session.commit()

            self.log_action('split_dataset', {
                'project_id': project_id,
                'strategy': strategy,
                'counts': counts
            })

            return {
                'success': True,
                'total_images': n,
                'counts': counts
            }

        return self.execute_in_context(_do_split)

    def get_statistics(self, project_id: int) -> Dict[str, Any]:
        """
        Get dataset statistics

        Args:
            project_id: Project ID

        Returns:
            Statistics including image counts, annotation counts, etc.
        """
        def _get_stats():
            from app.models import Project, Image, Annotation, LabelClass
            from sqlalchemy import func

            project = Project.query.get(project_id)
            if not project:
                return {'error': f'Project {project_id} not found'}

            # Image counts by split
            split_counts = dict(
                Image.query.filter_by(project_id=project_id)
                .with_entities(Image.split, func.count(Image.id))
                .group_by(Image.split)
                .all()
            )

            # Image counts by status
            status_counts = dict(
                Image.query.filter_by(project_id=project_id)
                .with_entities(Image.status, func.count(Image.id))
                .group_by(Image.status)
                .all()
            )

            # Annotation counts by class
            class_counts = {}
            for lc in project.label_classes.all():
                count = Annotation.query.filter_by(class_id=lc.id).count()
                class_counts[lc.name] = count

            total_images = project.images.count()
            total_annotations = sum(class_counts.values())

            return {
                'project_id': project_id,
                'project_name': project.name,
                'total_images': total_images,
                'total_annotations': total_annotations,
                'by_split': split_counts,
                'by_status': status_counts,
                'by_class': class_counts
            }

        return self.execute_in_context(_get_stats)

    def list_images(
        self,
        project_id: int,
        split: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List images in a project

        Args:
            project_id: Project ID
            split: Optional filter by split (train/val/test)
            status: Optional filter by status (pending/annotated/reviewed)
            limit: Maximum number of images to return

        Returns:
            List of image dictionaries
        """
        def _list():
            from app.models import Image

            query = Image.query.filter_by(project_id=project_id)

            if split:
                query = query.filter_by(split=split)
            if status:
                query = query.filter_by(status=status)

            images = query.limit(limit).all()
            return [img.to_dict() for img in images]

        return self.execute_in_context(_list)
