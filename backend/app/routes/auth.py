# -*- coding: utf-8 -*-
"""
Authentication Routes
"""
from flask import Blueprint, request, jsonify
from app.models import User
from app.extensions import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing credentials'}), 400

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return jsonify({
            'success': True,
            'user': user.to_dict()
        })

    return jsonify({'error': 'Invalid credentials'}), 401


@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'labeler')

    if not username or not password:
        return jsonify({'error': 'Missing required fields'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 409

    user = User(username=username, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'success': True,
        'user': user.to_dict()
    }), 201
