# -*- coding: utf-8 -*-
"""
Project Member Model
"""
from datetime import datetime
from app.extensions import db


class ProjectMember(db.Model):
    """Project member - tracks users working on a project"""
    __tablename__ = 'project_members'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)  # Original name before numbering
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    images_assigned = db.Column(db.Integer, default=0)
    images_completed = db.Column(db.Integer, default=0)

    # Relationships
    project = db.relationship('Project', backref=db.backref('members', lazy='dynamic'))

    __table_args__ = (
        db.UniqueConstraint('project_id', 'username', name='unique_project_username'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'username': self.username,
            'display_name': self.display_name,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'images_assigned': self.images_assigned,
            'images_completed': self.images_completed
        }
