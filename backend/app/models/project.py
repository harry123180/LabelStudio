# -*- coding: utf-8 -*-
"""
Project Model
"""
from datetime import datetime
from app.extensions import db


class Project(db.Model):
    """Annotation project"""
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    project_type = db.Column(db.String(50), default='object_detection')  # object_detection, segmentation, classification
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Dataset split ratios
    train_ratio = db.Column(db.Float, default=0.7)
    val_ratio = db.Column(db.Float, default=0.2)
    test_ratio = db.Column(db.Float, default=0.1)

    # Relationships
    images = db.relationship('Image', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    label_classes = db.relationship('LabelClass', backref='project', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'project_type': self.project_type,
            'created_at': self.created_at.isoformat(),
            'image_count': self.images.count(),
            'class_count': self.label_classes.count(),
            'split_ratios': {
                'train': self.train_ratio,
                'val': self.val_ratio,
                'test': self.test_ratio
            }
        }
