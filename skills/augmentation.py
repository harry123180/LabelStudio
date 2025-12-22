# -*- coding: utf-8 -*-
"""
Augmentation Skill

Provides image augmentation operations for AI agents:
- Configure augmentation settings
- Preview augmented images
- Batch augmentation
"""
import os
from typing import Dict, Any, List, Optional
from .base import BaseSkill


class AugmentationSkill(BaseSkill):
    """Image augmentation skill for AI agents"""

    # Default augmentation presets
    PRESETS = {
        'light': {
            'horizontal_flip': True,
            'brightness': True,
            'brightness_range': (-0.1, 0.1)
        },
        'medium': {
            'horizontal_flip': True,
            'rotation': True,
            'rotation_range': (-15, 15),
            'scale': True,
            'scale_range': (0.9, 1.1),
            'brightness': True,
            'brightness_range': (-0.2, 0.2)
        },
        'heavy': {
            'horizontal_flip': True,
            'vertical_flip': True,
            'rotation': True,
            'rotation_range': (-30, 30),
            'scale': True,
            'scale_range': (0.8, 1.2),
            'brightness': True,
            'brightness_range': (-0.3, 0.3),
            'contrast': True,
            'contrast_range': (0.8, 1.2),
            'gaussian_noise': True,
            'noise_sigma': 10
        },
        'detection': {
            'horizontal_flip': True,
            'rotation': True,
            'rotation_range': (-15, 15),
            'scale': True,
            'scale_range': (0.8, 1.2),
            'brightness': True,
            'brightness_range': (-0.2, 0.2),
            'blur': True,
            'blur_radius': 2
        }
    }

    def get_info(self) -> Dict[str, Any]:
        return {
            'name': 'AugmentationSkill',
            'description': 'Configure and apply image augmentation',
            'methods': {
                'get_presets': {
                    'description': 'Get available augmentation presets',
                    'params': {}
                },
                'get_options': {
                    'description': 'Get all available augmentation options',
                    'params': {}
                },
                'preview_augmentation': {
                    'description': 'Preview augmentation on a single image',
                    'params': {
                        'image_id': 'int - Image ID',
                        'config': 'dict - Augmentation config'
                    }
                },
                'apply_augmentation': {
                    'description': 'Apply augmentation to project images',
                    'params': {
                        'project_id': 'int - Project ID',
                        'config': 'dict - Augmentation config',
                        'multiplier': 'int - Number of augmented copies per image'
                    }
                }
            }
        }

    def get_presets(self) -> Dict[str, Any]:
        """Get available augmentation presets"""
        return {
            'presets': {
                'light': {
                    'description': 'Light augmentation - horizontal flip + minor brightness',
                    'config': self.PRESETS['light']
                },
                'medium': {
                    'description': 'Medium augmentation - adds rotation and scaling',
                    'config': self.PRESETS['medium']
                },
                'heavy': {
                    'description': 'Heavy augmentation - all transforms + noise',
                    'config': self.PRESETS['heavy']
                },
                'detection': {
                    'description': 'Optimized for object detection tasks',
                    'config': self.PRESETS['detection']
                }
            }
        }

    def get_options(self) -> Dict[str, Any]:
        """Get all available augmentation options"""
        return {
            'geometric': [
                {
                    'id': 'horizontal_flip',
                    'name': 'Horizontal Flip',
                    'name_zh': '水平翻轉',
                    'type': 'bool'
                },
                {
                    'id': 'vertical_flip',
                    'name': 'Vertical Flip',
                    'name_zh': '垂直翻轉',
                    'type': 'bool'
                },
                {
                    'id': 'rotation',
                    'name': 'Rotation',
                    'name_zh': '旋轉',
                    'type': 'range',
                    'range_param': 'rotation_range',
                    'default': (-15, 15),
                    'min': -45,
                    'max': 45
                },
                {
                    'id': 'scale',
                    'name': 'Scale',
                    'name_zh': '縮放',
                    'type': 'range',
                    'range_param': 'scale_range',
                    'default': (0.8, 1.2),
                    'min': 0.5,
                    'max': 1.5
                }
            ],
            'color': [
                {
                    'id': 'brightness',
                    'name': 'Brightness',
                    'name_zh': '亮度',
                    'type': 'range',
                    'range_param': 'brightness_range',
                    'default': (-0.2, 0.2),
                    'min': -0.5,
                    'max': 0.5
                },
                {
                    'id': 'contrast',
                    'name': 'Contrast',
                    'name_zh': '對比度',
                    'type': 'range',
                    'range_param': 'contrast_range',
                    'default': (0.8, 1.2),
                    'min': 0.5,
                    'max': 1.5
                },
                {
                    'id': 'saturation',
                    'name': 'Saturation',
                    'name_zh': '飽和度',
                    'type': 'range',
                    'range_param': 'saturation_range',
                    'default': (0.8, 1.2),
                    'min': 0.5,
                    'max': 1.5
                }
            ],
            'noise': [
                {
                    'id': 'gaussian_noise',
                    'name': 'Gaussian Noise',
                    'name_zh': '高斯噪點',
                    'type': 'value',
                    'value_param': 'noise_sigma',
                    'default': 10,
                    'min': 0,
                    'max': 30
                },
                {
                    'id': 'blur',
                    'name': 'Gaussian Blur',
                    'name_zh': '高斯模糊',
                    'type': 'value',
                    'value_param': 'blur_radius',
                    'default': 2,
                    'min': 0,
                    'max': 5
                }
            ]
        }

    def preview_augmentation(
        self,
        image_id: int,
        config: Optional[Dict[str, Any]] = None,
        preset: Optional[str] = None,
        num_samples: int = 4
    ) -> Dict[str, Any]:
        """
        Preview augmentation on a single image

        Args:
            image_id: Image ID
            config: Custom augmentation config
            preset: Use a preset instead of custom config
            num_samples: Number of augmented samples to generate

        Returns:
            Augmentation preview results
        """
        def _preview():
            import cv2
            import base64
            from app.models import Image
            from app.services.augmentation import Augmentor

            image = Image.query.get(image_id)
            if not image:
                return {'error': f'Image {image_id} not found'}

            # Get config
            aug_config = config
            if preset and preset in self.PRESETS:
                aug_config = self.PRESETS[preset]
            if not aug_config:
                aug_config = self.PRESETS['medium']

            # Load image
            img = cv2.imread(image.file_path)
            if img is None:
                return {'error': 'Failed to load image'}

            # Get annotations
            annotations = []
            for anno in image.annotations.all():
                if anno.annotation_type == 'bbox':
                    data = anno.get_data()
                    annotations.append({
                        'bbox': [data['x'], data['y'], data['width'], data['height']],
                        'class': anno.label_class.name
                    })

            # Generate augmented samples
            augmentor = Augmentor(aug_config)
            samples = []

            for i in range(num_samples):
                aug_img, aug_annos = augmentor.augment(img, annotations)

                # Convert to base64 for preview
                _, buffer = cv2.imencode('.jpg', aug_img, [cv2.IMWRITE_JPEG_QUALITY, 80])
                img_base64 = base64.b64encode(buffer).decode()

                samples.append({
                    'index': i,
                    'image_base64': f'data:image/jpeg;base64,{img_base64}',
                    'annotations': aug_annos
                })

            return {
                'image_id': image_id,
                'config': aug_config,
                'samples': samples
            }

        return self.execute_in_context(_preview)

    def estimate_output(
        self,
        project_id: int,
        multiplier: int = 3,
        split: str = 'train'
    ) -> Dict[str, Any]:
        """
        Estimate augmentation output size

        Args:
            project_id: Project ID
            multiplier: Number of augmented copies per image
            split: Which split to augment (train/val/test/all)

        Returns:
            Estimation of output size
        """
        def _estimate():
            from app.models import Project, Image

            project = Project.query.get(project_id)
            if not project:
                return {'error': f'Project {project_id} not found'}

            if split == 'all':
                images = project.images.all()
            else:
                images = project.images.filter_by(split=split).all()

            original_count = len(images)
            augmented_count = original_count * multiplier
            total_count = original_count + augmented_count

            # Estimate file size (rough average)
            avg_size = sum(img.file_size or 0 for img in images) / max(original_count, 1)
            estimated_size = total_count * avg_size

            return {
                'project_id': project_id,
                'split': split,
                'original_images': original_count,
                'augmented_images': augmented_count,
                'total_images': total_count,
                'multiplier': multiplier,
                'estimated_size_mb': estimated_size / (1024 * 1024)
            }

        return self.execute_in_context(_estimate)
