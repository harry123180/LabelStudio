# -*- coding: utf-8 -*-
"""
Annotation Model
"""
from datetime import datetime
from app.extensions import db
import json


class Annotation(db.Model):
    """Annotation on an image"""
    __tablename__ = 'annotations'

    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('images.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('label_classes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Annotation type
    annotation_type = db.Column(db.String(20), default='bbox')  # bbox, polygon, mask

    # Annotation data (JSON)
    # bbox: {"x": 0, "y": 0, "width": 100, "height": 100}
    # polygon: {"points": [[x1,y1], [x2,y2], ...]}
    # mask: {"rle": "..."}  # Run-length encoding
    data = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    label_class = db.relationship('LabelClass', backref='annotations')

    def get_data(self) -> dict:
        return json.loads(self.data)

    def set_data(self, data: dict):
        self.data = json.dumps(data)

    @property
    def label_class_id(self):
        """Alias for class_id"""
        return self.class_id

    @label_class_id.setter
    def label_class_id(self, value):
        self.class_id = value

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'image_id': self.image_id,
            'class_id': self.class_id,
            'label_class_id': self.class_id,  # Alias for frontend
            'class_name': self.label_class.name if self.label_class else None,
            'annotation_type': self.annotation_type,
            'type': self.annotation_type,
            'data': self.get_data(),
            'created_at': self.created_at.isoformat()
        }
