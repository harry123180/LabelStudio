# -*- coding: utf-8 -*-
"""
Image Model
"""
from datetime import datetime
from app import db


class Image(db.Model):
    """Image in a project"""
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=True)
    file_path = db.Column(db.String(500), nullable=False)
    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    file_size = db.Column(db.Integer, nullable=True)

    # Dataset split
    split = db.Column(db.String(20), default='train')  # train, val, test
    split_locked = db.Column(db.Boolean, default=False)

    # Upload info
    uploader_name = db.Column(db.String(80), nullable=True)  # For mobile quick upload
    upload_source = db.Column(db.String(20), default='web')  # web, mobile
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Status
    status = db.Column(db.String(20), default='pending')  # pending, annotated, reviewed
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relationships
    annotations = db.relationship('Annotation', backref='image', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'width': self.width,
            'height': self.height,
            'split': self.split,
            'status': self.status,
            'uploader': self.uploader_name,
            'upload_source': self.upload_source,
            'uploaded_at': self.uploaded_at.isoformat(),
            'annotation_count': self.annotations.count()
        }
