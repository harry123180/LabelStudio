# -*- coding: utf-8 -*-
"""
Label Class Model
"""
from datetime import datetime
from app import db


class LabelClass(db.Model):
    """Label class (category) for annotations"""
    __tablename__ = 'label_classes'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(7), default='#FF0000')  # Hex color
    description = db.Column(db.Text, nullable=True)
    shortcut_key = db.Column(db.String(1), nullable=True)  # Keyboard shortcut
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'description': self.description,
            'shortcut_key': self.shortcut_key,
            'annotation_count': len(self.annotations)
        }
