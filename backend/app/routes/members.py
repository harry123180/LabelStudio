# -*- coding: utf-8 -*-
"""
Project Members Routes
"""
import re
from datetime import datetime
from flask import Blueprint, request, jsonify
from app.models import Project, ProjectMember, Image
from app.extensions import db

members_bp = Blueprint('members', __name__)


def generate_unique_username(project_id, desired_name):
    """
    Generate a unique username for a project.
    If 'alice' exists, returns 'alice_1', then 'alice_2', etc.
    """
    desired_name = desired_name.strip()
    if not desired_name:
        desired_name = 'user'

    # Check if exact name exists
    existing = ProjectMember.query.filter_by(
        project_id=project_id,
        username=desired_name
    ).first()

    if not existing:
        return desired_name

    # Find all usernames with this base name
    pattern = f"^{re.escape(desired_name)}(_\\d+)?$"
    similar = ProjectMember.query.filter(
        ProjectMember.project_id == project_id,
        ProjectMember.username.op('REGEXP')(pattern) if db.engine.dialect.name != 'sqlite'
        else ProjectMember.username.like(f"{desired_name}%")
    ).all()

    # Extract numbers and find max
    max_num = 0
    for member in similar:
        if member.username == desired_name:
            max_num = max(max_num, 0)
        elif member.username.startswith(desired_name + '_'):
            try:
                suffix = member.username[len(desired_name) + 1:]
                num = int(suffix)
                max_num = max(max_num, num)
            except ValueError:
                pass

    return f"{desired_name}_{max_num + 1}"


@members_bp.route('/project/<int:project_id>/join', methods=['POST'])
def join_project(project_id):
    """Join a project with a username"""
    project = Project.query.get_or_404(project_id)
    data = request.get_json()

    desired_name = data.get('username', 'user').strip()
    if not desired_name:
        return jsonify({'error': 'Username is required'}), 400

    # Generate unique username
    unique_username = generate_unique_username(project_id, desired_name)

    # Create member
    member = ProjectMember(
        project_id=project_id,
        username=unique_username,
        display_name=desired_name
    )
    db.session.add(member)
    db.session.commit()

    return jsonify({
        'success': True,
        'member': member.to_dict(),
        'username': unique_username,
        'was_renamed': unique_username != desired_name
    }), 201


@members_bp.route('/project/<int:project_id>/members', methods=['GET'])
def list_members(project_id):
    """List all members in a project"""
    project = Project.query.get_or_404(project_id)
    members = project.members.order_by(ProjectMember.joined_at).all()

    # Calculate stats for each member
    result = []
    for member in members:
        data = member.to_dict()
        # Count assigned and completed images
        data['images_assigned'] = Image.query.filter_by(
            project_id=project_id,
            assigned_to=member.username
        ).count()
        data['images_completed'] = Image.query.filter_by(
            project_id=project_id,
            annotated_by=member.username
        ).count()
        result.append(data)

    return jsonify(result)


@members_bp.route('/project/<int:project_id>/member/<username>', methods=['GET'])
def get_member(project_id, username):
    """Get a specific member"""
    member = ProjectMember.query.filter_by(
        project_id=project_id,
        username=username
    ).first_or_404()
    return jsonify(member.to_dict())


@members_bp.route('/project/<int:project_id>/member/<username>/active', methods=['POST'])
def update_activity(project_id, username):
    """Update member's last active time"""
    member = ProjectMember.query.filter_by(
        project_id=project_id,
        username=username
    ).first_or_404()

    member.last_active = datetime.utcnow()
    db.session.commit()

    return jsonify(member.to_dict())


@members_bp.route('/project/<int:project_id>/assign', methods=['POST'])
def assign_images(project_id):
    """Assign images to members"""
    project = Project.query.get_or_404(project_id)
    data = request.get_json()

    mode = data.get('mode', 'auto')  # auto, manual
    members_list = data.get('members', [])  # For auto mode: list of usernames to include

    if mode == 'auto':
        # Get members to assign to
        if members_list:
            members = ProjectMember.query.filter(
                ProjectMember.project_id == project_id,
                ProjectMember.username.in_(members_list)
            ).all()
        else:
            members = project.members.all()

        if not members:
            return jsonify({'error': 'No members to assign to'}), 400

        # Get unassigned images
        unassigned = Image.query.filter_by(
            project_id=project_id,
            assigned_to=None
        ).all()

        # Round-robin assignment
        for i, image in enumerate(unassigned):
            member = members[i % len(members)]
            image.assigned_to = member.username

        db.session.commit()

        return jsonify({
            'success': True,
            'assigned': len(unassigned),
            'members_count': len(members)
        })

    elif mode == 'manual':
        # Manual assignment: { image_id: username }
        assignments = data.get('assignments', {})
        count = 0
        for image_id, username in assignments.items():
            image = Image.query.get(int(image_id))
            if image and image.project_id == project_id:
                image.assigned_to = username if username else None
                count += 1

        db.session.commit()
        return jsonify({'success': True, 'assigned': count})

    return jsonify({'error': 'Invalid mode'}), 400


@members_bp.route('/project/<int:project_id>/my-images/<username>', methods=['GET'])
def get_my_images(project_id, username):
    """Get images assigned to a specific user"""
    project = Project.query.get_or_404(project_id)

    images = Image.query.filter_by(
        project_id=project_id,
        assigned_to=username
    ).order_by(Image.uploaded_at.desc()).all()

    return jsonify([img.to_dict() for img in images])
