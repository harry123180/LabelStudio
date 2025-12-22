# -*- coding: utf-8 -*-
"""
LabelStudio Skills Module

This module contains Python scripts that can be invoked by AI agents
to perform various automation tasks for the LabelStudio application.

Skills are organized by category:
- dataset: Dataset management operations
- annotation: Annotation-related operations
- export: Data export operations
- augmentation: Image augmentation operations
- utils: Utility scripts

Usage:
    from skills import DatasetSkill
    skill = DatasetSkill()
    result = skill.split_dataset(project_id=1, train=0.7, val=0.2, test=0.1)
"""

from .dataset import DatasetSkill
from .annotation import AnnotationSkill
from .export import ExportSkill
from .augmentation import AugmentationSkill

__all__ = [
    'DatasetSkill',
    'AnnotationSkill',
    'ExportSkill',
    'AugmentationSkill'
]
