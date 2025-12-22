# -*- coding: utf-8 -*-
"""
Data Augmentation Service
"""
import cv2
import numpy as np
import random
from typing import List, Tuple, Dict, Any


class Augmentor:
    """Data augmentation for images and annotations"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize augmentor with configuration

        Args:
            config: Augmentation settings
                - horizontal_flip: bool
                - vertical_flip: bool
                - rotation: bool, rotation_range: tuple (-45, 45)
                - scale: bool, scale_range: tuple (0.8, 1.2)
                - brightness: bool, brightness_range: tuple (-0.3, 0.3)
                - contrast: bool, contrast_range: tuple (0.7, 1.3)
                - gaussian_noise: bool, noise_sigma: int
                - blur: bool, blur_radius: int
        """
        self.config = config

    def augment(self, image: np.ndarray, annotations: List[Dict]) -> Tuple[np.ndarray, List[Dict]]:
        """
        Apply augmentation to image and adjust annotations

        Args:
            image: OpenCV format image (BGR)
            annotations: List of annotation dicts with 'bbox': [x, y, w, h]

        Returns:
            (augmented_image, adjusted_annotations)
        """
        img = image.copy()
        annos = [a.copy() for a in annotations]

        # Geometric transforms (require annotation adjustment)
        if self.config.get('horizontal_flip') and random.random() < 0.5:
            img, annos = self._horizontal_flip(img, annos)

        if self.config.get('vertical_flip') and random.random() < 0.5:
            img, annos = self._vertical_flip(img, annos)

        if self.config.get('rotation'):
            angle = random.uniform(*self.config.get('rotation_range', (-15, 15)))
            img, annos = self._rotate(img, annos, angle)

        if self.config.get('scale'):
            factor = random.uniform(*self.config.get('scale_range', (0.8, 1.2)))
            img, annos = self._scale(img, annos, factor)

        # Color transforms (no annotation adjustment needed)
        if self.config.get('brightness'):
            img = self._adjust_brightness(img, self.config.get('brightness_range', (-0.2, 0.2)))

        if self.config.get('contrast'):
            img = self._adjust_contrast(img, self.config.get('contrast_range', (0.8, 1.2)))

        if self.config.get('saturation'):
            img = self._adjust_saturation(img, self.config.get('saturation_range', (0.8, 1.2)))

        if self.config.get('gaussian_noise'):
            img = self._add_gaussian_noise(img, self.config.get('noise_sigma', 10))

        if self.config.get('blur'):
            img = self._apply_blur(img, self.config.get('blur_radius', 3))

        return img, annos

    def _horizontal_flip(self, img: np.ndarray, annos: List[Dict]) -> Tuple[np.ndarray, List[Dict]]:
        """Horizontal flip"""
        h, w = img.shape[:2]
        img = cv2.flip(img, 1)

        for anno in annos:
            if 'bbox' in anno:
                x, y, bw, bh = anno['bbox']
                anno['bbox'] = [w - x - bw, y, bw, bh]

        return img, annos

    def _vertical_flip(self, img: np.ndarray, annos: List[Dict]) -> Tuple[np.ndarray, List[Dict]]:
        """Vertical flip"""
        h, w = img.shape[:2]
        img = cv2.flip(img, 0)

        for anno in annos:
            if 'bbox' in anno:
                x, y, bw, bh = anno['bbox']
                anno['bbox'] = [x, h - y - bh, bw, bh]

        return img, annos

    def _rotate(self, img: np.ndarray, annos: List[Dict], angle: float) -> Tuple[np.ndarray, List[Dict]]:
        """Rotate image and annotations"""
        h, w = img.shape[:2]
        center = (w // 2, h // 2)

        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        img = cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REFLECT)

        for anno in annos:
            if 'bbox' in anno:
                anno['bbox'] = self._rotate_bbox(anno['bbox'], M, w, h)

        return img, annos

    def _rotate_bbox(self, bbox: List[float], M: np.ndarray, img_w: int, img_h: int) -> List[float]:
        """Rotate bounding box and get new axis-aligned bbox"""
        x, y, w, h = bbox

        # Get corners
        corners = np.array([
            [x, y],
            [x + w, y],
            [x + w, y + h],
            [x, y + h]
        ], dtype=np.float32)

        # Transform corners
        ones = np.ones((4, 1))
        corners_h = np.hstack([corners, ones])
        rotated = M @ corners_h.T
        rotated = rotated.T

        # Get new bounding box
        x_min = max(0, rotated[:, 0].min())
        y_min = max(0, rotated[:, 1].min())
        x_max = min(img_w, rotated[:, 0].max())
        y_max = min(img_h, rotated[:, 1].max())

        return [x_min, y_min, x_max - x_min, y_max - y_min]

    def _scale(self, img: np.ndarray, annos: List[Dict], factor: float) -> Tuple[np.ndarray, List[Dict]]:
        """Scale image and annotations"""
        h, w = img.shape[:2]
        new_h, new_w = int(h * factor), int(w * factor)

        img = cv2.resize(img, (new_w, new_h))

        # Pad or crop to original size
        if factor > 1:
            # Crop center
            start_x = (new_w - w) // 2
            start_y = (new_h - h) // 2
            img = img[start_y:start_y + h, start_x:start_x + w]
            offset_x, offset_y = -start_x, -start_y
        else:
            # Pad
            pad_x = (w - new_w) // 2
            pad_y = (h - new_h) // 2
            img = cv2.copyMakeBorder(img, pad_y, h - new_h - pad_y,
                                     pad_x, w - new_w - pad_x,
                                     cv2.BORDER_REFLECT)
            offset_x, offset_y = pad_x, pad_y

        for anno in annos:
            if 'bbox' in anno:
                x, y, bw, bh = anno['bbox']
                anno['bbox'] = [
                    x * factor + offset_x,
                    y * factor + offset_y,
                    bw * factor,
                    bh * factor
                ]

        return img, annos

    def _adjust_brightness(self, img: np.ndarray, range_: Tuple[float, float]) -> np.ndarray:
        """Adjust brightness"""
        factor = random.uniform(*range_)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * (1 + factor), 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    def _adjust_contrast(self, img: np.ndarray, range_: Tuple[float, float]) -> np.ndarray:
        """Adjust contrast"""
        factor = random.uniform(*range_)
        mean = np.mean(img)
        return np.clip((img - mean) * factor + mean, 0, 255).astype(np.uint8)

    def _adjust_saturation(self, img: np.ndarray, range_: Tuple[float, float]) -> np.ndarray:
        """Adjust saturation"""
        factor = random.uniform(*range_)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * factor, 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    def _add_gaussian_noise(self, img: np.ndarray, sigma: int) -> np.ndarray:
        """Add Gaussian noise"""
        noise = np.random.normal(0, sigma, img.shape).astype(np.float32)
        noisy = np.clip(img.astype(np.float32) + noise, 0, 255)
        return noisy.astype(np.uint8)

    def _apply_blur(self, img: np.ndarray, radius: int) -> np.ndarray:
        """Apply Gaussian blur"""
        if radius > 0:
            ksize = radius * 2 + 1
            return cv2.GaussianBlur(img, (ksize, ksize), 0)
        return img
