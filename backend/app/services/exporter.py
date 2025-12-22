# -*- coding: utf-8 -*-
"""
Dataset Exporter Service
"""
from app.models import Project, Image, Annotation
from .augmentation import Augmentor
import os
import json
import shutil
import zipfile
from datetime import datetime


class DatasetExporter:
    """Export dataset in various formats"""

    def __init__(self, project: Project, export_folder: str):
        self.project = project
        self.export_folder = export_folder
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    def export(self, format_type: str, include_augmentation: bool = False,
               augmentation_config: dict = None) -> str:
        """
        Export dataset

        Args:
            format_type: yolo, coco, voc, createml, csv
            include_augmentation: Whether to apply augmentation
            augmentation_config: Augmentation settings

        Returns:
            Path to zip file
        """
        # Create export directory
        export_dir = os.path.join(
            self.export_folder,
            f"{self.project.id}_{self.timestamp}"
        )
        os.makedirs(export_dir, exist_ok=True)

        # Export based on format
        if format_type == 'yolo':
            self._export_yolo(export_dir, include_augmentation, augmentation_config)
        elif format_type == 'coco':
            self._export_coco(export_dir, include_augmentation, augmentation_config)
        elif format_type == 'voc':
            self._export_voc(export_dir, include_augmentation, augmentation_config)
        elif format_type == 'createml':
            self._export_createml(export_dir, include_augmentation, augmentation_config)
        elif format_type == 'csv':
            self._export_csv(export_dir)
        else:
            raise ValueError(f"Unsupported format: {format_type}")

        # Create zip file
        zip_path = f"{export_dir}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(export_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, export_dir)
                    zipf.write(file_path, arcname)

        # Cleanup directory
        shutil.rmtree(export_dir)

        return zip_path

    def _export_yolo(self, export_dir: str, include_augmentation: bool,
                     augmentation_config: dict):
        """Export in YOLO format"""
        # Create directory structure
        for split in ['train', 'val', 'test']:
            os.makedirs(os.path.join(export_dir, split, 'images'), exist_ok=True)
            os.makedirs(os.path.join(export_dir, split, 'labels'), exist_ok=True)

        # Get class mapping
        classes = list(self.project.label_classes.order_by('id').all())
        class_map = {c.id: idx for idx, c in enumerate(classes)}

        # Write classes file
        with open(os.path.join(export_dir, 'classes.txt'), 'w', encoding='utf-8') as f:
            for c in classes:
                f.write(f"{c.name}\n")

        # Write data.yaml
        with open(os.path.join(export_dir, 'data.yaml'), 'w', encoding='utf-8') as f:
            f.write(f"train: ./train/images\n")
            f.write(f"val: ./val/images\n")
            f.write(f"test: ./test/images\n")
            f.write(f"nc: {len(classes)}\n")
            f.write(f"names: {[c.name for c in classes]}\n")

        # Export images and annotations
        for image in self.project.images.all():
            split_dir = image.split if image.split else 'train'

            # Copy image
            src_path = image.file_path
            dst_path = os.path.join(export_dir, split_dir, 'images', image.filename)
            shutil.copy(src_path, dst_path)

            # Write YOLO format labels
            label_filename = os.path.splitext(image.filename)[0] + '.txt'
            label_path = os.path.join(export_dir, split_dir, 'labels', label_filename)

            with open(label_path, 'w') as f:
                for anno in image.annotations.all():
                    if anno.annotation_type == 'bbox':
                        data = anno.get_data()
                        class_idx = class_map.get(anno.class_id, 0)

                        # Convert to YOLO format (normalized xywh)
                        x_center = (data['x'] + data['width'] / 2) / image.width
                        y_center = (data['y'] + data['height'] / 2) / image.height
                        w = data['width'] / image.width
                        h = data['height'] / image.height

                        f.write(f"{class_idx} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}\n")

    def _export_coco(self, export_dir: str, include_augmentation: bool,
                     augmentation_config: dict):
        """Export in COCO format"""
        # Create directory structure
        os.makedirs(os.path.join(export_dir, 'images'), exist_ok=True)

        # Build COCO structure
        coco_data = {
            'info': {
                'description': self.project.name,
                'version': '1.0',
                'year': datetime.now().year
            },
            'licenses': [],
            'images': [],
            'annotations': [],
            'categories': []
        }

        # Add categories
        classes = list(self.project.label_classes.order_by('id').all())
        for idx, c in enumerate(classes):
            coco_data['categories'].append({
                'id': idx + 1,
                'name': c.name,
                'supercategory': 'object'
            })

        class_map = {c.id: idx + 1 for idx, c in enumerate(classes)}

        # Add images and annotations
        anno_id = 1
        for img_idx, image in enumerate(self.project.images.all()):
            # Copy image
            shutil.copy(image.file_path, os.path.join(export_dir, 'images', image.filename))

            # Add image entry
            coco_data['images'].append({
                'id': img_idx + 1,
                'file_name': image.filename,
                'width': image.width,
                'height': image.height
            })

            # Add annotations
            for anno in image.annotations.all():
                if anno.annotation_type == 'bbox':
                    data = anno.get_data()
                    coco_data['annotations'].append({
                        'id': anno_id,
                        'image_id': img_idx + 1,
                        'category_id': class_map.get(anno.class_id, 1),
                        'bbox': [data['x'], data['y'], data['width'], data['height']],
                        'area': data['width'] * data['height'],
                        'iscrowd': 0
                    })
                    anno_id += 1

        # Write JSON
        with open(os.path.join(export_dir, 'annotations.json'), 'w', encoding='utf-8') as f:
            json.dump(coco_data, f, ensure_ascii=False, indent=2)

    def _export_voc(self, export_dir: str, include_augmentation: bool,
                    augmentation_config: dict):
        """Export in Pascal VOC format"""
        os.makedirs(os.path.join(export_dir, 'JPEGImages'), exist_ok=True)
        os.makedirs(os.path.join(export_dir, 'Annotations'), exist_ok=True)

        for image in self.project.images.all():
            # Copy image
            shutil.copy(image.file_path, os.path.join(export_dir, 'JPEGImages', image.filename))

            # Create XML annotation
            xml_content = self._create_voc_xml(image)
            xml_filename = os.path.splitext(image.filename)[0] + '.xml'
            with open(os.path.join(export_dir, 'Annotations', xml_filename), 'w', encoding='utf-8') as f:
                f.write(xml_content)

    def _create_voc_xml(self, image: Image) -> str:
        """Create Pascal VOC XML for an image"""
        xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<annotation>
    <folder>JPEGImages</folder>
    <filename>{image.filename}</filename>
    <size>
        <width>{image.width}</width>
        <height>{image.height}</height>
        <depth>3</depth>
    </size>
'''
        for anno in image.annotations.all():
            if anno.annotation_type == 'bbox':
                data = anno.get_data()
                xml += f'''    <object>
        <name>{anno.label_class.name}</name>
        <bndbox>
            <xmin>{int(data['x'])}</xmin>
            <ymin>{int(data['y'])}</ymin>
            <xmax>{int(data['x'] + data['width'])}</xmax>
            <ymax>{int(data['y'] + data['height'])}</ymax>
        </bndbox>
    </object>
'''
        xml += '</annotation>'
        return xml

    def _export_createml(self, export_dir: str, include_augmentation: bool,
                         augmentation_config: dict):
        """Export in Apple CreateML format"""
        os.makedirs(os.path.join(export_dir, 'images'), exist_ok=True)

        annotations = []

        for image in self.project.images.all():
            # Copy image
            shutil.copy(image.file_path, os.path.join(export_dir, 'images', image.filename))

            # Build annotation entry
            image_annos = []
            for anno in image.annotations.all():
                if anno.annotation_type == 'bbox':
                    data = anno.get_data()
                    image_annos.append({
                        'label': anno.label_class.name,
                        'coordinates': {
                            'x': data['x'] + data['width'] / 2,
                            'y': data['y'] + data['height'] / 2,
                            'width': data['width'],
                            'height': data['height']
                        }
                    })

            annotations.append({
                'image': image.filename,
                'annotations': image_annos
            })

        # Write JSON
        with open(os.path.join(export_dir, 'annotations.json'), 'w', encoding='utf-8') as f:
            json.dump(annotations, f, ensure_ascii=False, indent=2)

    def _export_csv(self, export_dir: str):
        """Export in CSV format"""
        os.makedirs(os.path.join(export_dir, 'images'), exist_ok=True)

        with open(os.path.join(export_dir, 'annotations.csv'), 'w', encoding='utf-8') as f:
            f.write('filename,class,x,y,width,height\n')

            for image in self.project.images.all():
                shutil.copy(image.file_path, os.path.join(export_dir, 'images', image.filename))

                for anno in image.annotations.all():
                    if anno.annotation_type == 'bbox':
                        data = anno.get_data()
                        f.write(f"{image.filename},{anno.label_class.name},"
                                f"{data['x']},{data['y']},{data['width']},{data['height']}\n")
