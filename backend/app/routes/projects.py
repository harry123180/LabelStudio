# -*- coding: utf-8 -*-
"""
Project Routes
"""
import os
import json
import random
import zipfile
import tempfile
import numpy as np
from io import BytesIO
from flask import Blueprint, request, jsonify, send_file, current_app
from PIL import Image as PILImage, ImageEnhance, ImageFilter
from app.models import Project, LabelClass, Image, Annotation
from app.extensions import db

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


@projects_bp.route('/<int:project_id>/classes/<int:class_id>', methods=['PUT'])
def update_class(project_id, class_id):
    """Update a label class"""
    Project.query.get_or_404(project_id)
    label_class = LabelClass.query.get_or_404(class_id)

    data = request.get_json()
    if 'name' in data:
        label_class.name = data['name']
    if 'color' in data:
        label_class.color = data['color']
    if 'shortcut_key' in data:
        label_class.shortcut_key = data['shortcut_key']
    if 'description' in data:
        label_class.description = data['description']

    db.session.commit()
    return jsonify(label_class.to_dict())


@projects_bp.route('/<int:project_id>/classes/<int:class_id>', methods=['DELETE'])
def delete_class(project_id, class_id):
    """Delete a label class"""
    Project.query.get_or_404(project_id)
    label_class = LabelClass.query.get_or_404(class_id)
    db.session.delete(label_class)
    db.session.commit()
    return jsonify({'success': True})


@projects_bp.route('/<int:project_id>/apply-split', methods=['POST'])
def apply_split(project_id):
    """Apply train/val/test split to images"""
    project = Project.query.get_or_404(project_id)
    images = project.images.filter_by(split_locked=False).all()

    if not images:
        return jsonify({'success': True, 'message': 'No images to split'})

    random.shuffle(images)
    total = len(images)

    train_count = int(total * project.train_ratio)
    val_count = int(total * project.val_ratio)

    for i, image in enumerate(images):
        if i < train_count:
            image.split = 'train'
        elif i < train_count + val_count:
            image.split = 'val'
        else:
            image.split = 'test'

    db.session.commit()

    return jsonify({
        'success': True,
        'train': train_count,
        'val': val_count,
        'test': total - train_count - val_count
    })


def apply_augmentation(pil_image, aug_type):
    """Apply augmentation to image and return transformation info for labels"""
    if aug_type == 'flip_h':
        return pil_image.transpose(PILImage.FLIP_LEFT_RIGHT), 'flip_h'
    elif aug_type == 'flip_v':
        return pil_image.transpose(PILImage.FLIP_TOP_BOTTOM), 'flip_v'
    elif aug_type == 'rotate90':
        return pil_image.transpose(PILImage.ROTATE_270), 'rotate90'  # Clockwise 90
    elif aug_type == 'brightness':
        factor = random.uniform(0.8, 1.2)
        enhancer = ImageEnhance.Brightness(pil_image)
        return enhancer.enhance(factor), 'none'  # No label change
    elif aug_type == 'contrast':
        factor = random.uniform(0.8, 1.2)
        enhancer = ImageEnhance.Contrast(pil_image)
        return enhancer.enhance(factor), 'none'
    elif aug_type == 'blur':
        return pil_image.filter(ImageFilter.GaussianBlur(radius=1)), 'none'
    elif aug_type == 'noise':
        # Add random noise
        img_array = np.array(pil_image)
        noise = np.random.randint(-15, 15, img_array.shape, dtype=np.int16)
        noisy = np.clip(img_array.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        return PILImage.fromarray(noisy), 'none'
    return pil_image, 'none'


def transform_yolo_label(x_center, y_center, w, h, transform_type, img_w, img_h):
    """Transform YOLO label based on augmentation type"""
    if transform_type == 'flip_h':
        # Horizontal flip: mirror x coordinate
        return 1.0 - x_center, y_center, w, h
    elif transform_type == 'flip_v':
        # Vertical flip: mirror y coordinate
        return x_center, 1.0 - y_center, w, h
    elif transform_type == 'rotate90':
        # Rotate 90 degrees clockwise: (x,y) -> (1-y, x), swap w/h
        return 1.0 - y_center, x_center, h, w
    return x_center, y_center, w, h


@projects_bp.route('/<int:project_id>/export', methods=['POST'])
def export_project(project_id):
    """Export project data in specified format with optional augmentation"""
    project = Project.query.get_or_404(project_id)
    data = request.get_json()

    format_type = data.get('format', 'yolo')
    include_images = data.get('includeImages', True)
    only_annotated = data.get('onlyAnnotated', False)

    # Augmentation settings
    augmentation = data.get('augmentation', {})
    aug_enabled = augmentation.get('enabled', False)
    aug_multiplier = augmentation.get('multiplier', 1)

    # Get images
    images_query = project.images
    if only_annotated:
        images_query = images_query.filter(Image.status == 'annotated')
    images = images_query.all()

    # Get classes
    classes = project.label_classes.all()
    class_map = {c.id: i for i, c in enumerate(classes)}

    # Determine which augmentations to apply
    aug_types = []
    if aug_enabled:
        if augmentation.get('flipHorizontal'):
            aug_types.append('flip_h')
        if augmentation.get('flipVertical'):
            aug_types.append('flip_v')
        if augmentation.get('rotate90'):
            aug_types.append('rotate90')
        if augmentation.get('brightness'):
            aug_types.append('brightness')
        if augmentation.get('contrast'):
            aug_types.append('contrast')
        if augmentation.get('blur'):
            aug_types.append('blur')
        if augmentation.get('noise'):
            aug_types.append('noise')

    # Create ZIP file
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        if format_type == 'yolo':
            # YOLO format (Ultralytics compatible)
            class_names = '\n'.join([c.name for c in classes])
            zf.writestr('classes.txt', class_names)

            names_yaml = '\n'.join([f'  {i}: {c.name}' for i, c in enumerate(classes)])
            yaml_content = f"""# Ultralytics YOLO dataset config
path: .
train: images/train
val: images/val
test: images/test

nc: {len(classes)}
names:
{names_yaml}
"""
            zf.writestr('data.yaml', yaml_content)

            for image in images:
                split = image.split or 'train'
                base_name = os.path.splitext(image.filename)[0]
                ext = os.path.splitext(image.filename)[1]

                # Get annotations for this image
                annotations = Annotation.query.filter_by(image_id=image.id).all()

                # Prepare original YOLO labels
                def get_yolo_labels(transform_type='none'):
                    label_lines = []
                    for anno in annotations:
                        if anno.class_id in class_map:
                            class_idx = class_map[anno.class_id]
                            d = anno.get_data()
                            x_center = (d['x'] + d['width'] / 2) / image.width
                            y_center = (d['y'] + d['height'] / 2) / image.height
                            w = d['width'] / image.width
                            h = d['height'] / image.height

                            # Transform if needed
                            x_center, y_center, w, h = transform_yolo_label(
                                x_center, y_center, w, h, transform_type, image.width, image.height
                            )
                            label_lines.append(f"{class_idx} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}")
                    return '\n'.join(label_lines)

                # Add original image and label
                if include_images and os.path.exists(image.file_path):
                    zf.write(image.file_path, f'images/{split}/{image.filename}')
                zf.writestr(f'labels/{split}/{base_name}.txt', get_yolo_labels())

                # Apply augmentation only to training set
                if aug_enabled and split == 'train' and os.path.exists(image.file_path):
                    try:
                        pil_img = PILImage.open(image.file_path)
                        if pil_img.mode != 'RGB':
                            pil_img = pil_img.convert('RGB')

                        for aug_type in aug_types:
                            for mult_idx in range(aug_multiplier):
                                aug_img, transform = apply_augmentation(pil_img.copy(), aug_type)
                                suffix = f"_{aug_type}_{mult_idx}" if aug_multiplier > 1 else f"_{aug_type}"

                                # Save augmented image
                                img_buffer = BytesIO()
                                aug_img.save(img_buffer, format='JPEG', quality=95)
                                img_buffer.seek(0)
                                zf.writestr(f'images/{split}/{base_name}{suffix}.jpg', img_buffer.read())

                                # Save transformed label
                                zf.writestr(f'labels/{split}/{base_name}{suffix}.txt', get_yolo_labels(transform))

                    except Exception as e:
                        print(f"Augmentation failed for {image.filename}: {e}")

        elif format_type == 'coco':
            # COCO format
            coco_data = {
                'images': [],
                'annotations': [],
                'categories': [{'id': i, 'name': c.name} for i, c in enumerate(classes)]
            }

            anno_id = 1
            for img_idx, image in enumerate(images):
                coco_data['images'].append({
                    'id': img_idx,
                    'file_name': image.filename,
                    'width': image.width,
                    'height': image.height
                })

                if include_images and os.path.exists(image.file_path):
                    zf.write(image.file_path, f'images/{image.filename}')

                annotations = Annotation.query.filter_by(image_id=image.id).all()
                for anno in annotations:
                    if anno.class_id in class_map:
                        d = anno.get_data()
                        coco_data['annotations'].append({
                            'id': anno_id,
                            'image_id': img_idx,
                            'category_id': class_map[anno.class_id],
                            'bbox': [d['x'], d['y'], d['width'], d['height']],
                            'area': d['width'] * d['height'],
                            'iscrowd': 0
                        })
                        anno_id += 1

            zf.writestr('annotations.json', json.dumps(coco_data, indent=2))

        elif format_type == 'voc':
            # Pascal VOC format
            for image in images:
                if include_images and os.path.exists(image.file_path):
                    zf.write(image.file_path, f'JPEGImages/{image.filename}')

                annotations = Annotation.query.filter_by(image_id=image.id).all()
                xml_content = f"""<annotation>
    <folder>JPEGImages</folder>
    <filename>{image.filename}</filename>
    <size>
        <width>{image.width}</width>
        <height>{image.height}</height>
        <depth>3</depth>
    </size>
"""
                for anno in annotations:
                    label_class = LabelClass.query.get(anno.class_id)
                    if label_class:
                        d = anno.get_data()
                        xml_content += f"""    <object>
        <name>{label_class.name}</name>
        <bndbox>
            <xmin>{int(d['x'])}</xmin>
            <ymin>{int(d['y'])}</ymin>
            <xmax>{int(d['x'] + d['width'])}</xmax>
            <ymax>{int(d['y'] + d['height'])}</ymax>
        </bndbox>
    </object>
"""
                xml_content += "</annotation>"
                xml_filename = os.path.splitext(image.filename)[0] + '.xml'
                zf.writestr(f'Annotations/{xml_filename}', xml_content)

        elif format_type == 'csv':
            # CSV format
            csv_lines = ['image,class,x,y,width,height']
            for image in images:
                if include_images and os.path.exists(image.file_path):
                    zf.write(image.file_path, f'images/{image.filename}')

                annotations = Annotation.query.filter_by(image_id=image.id).all()
                for anno in annotations:
                    label_class = LabelClass.query.get(anno.class_id)
                    if label_class:
                        d = anno.get_data()
                        csv_lines.append(f"{image.filename},{label_class.name},{d['x']},{d['y']},{d['width']},{d['height']}")

            zf.writestr('annotations.csv', '\n'.join(csv_lines))

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'{project.name}_{format_type}.zip'
    )
