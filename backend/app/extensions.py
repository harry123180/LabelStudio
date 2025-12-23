# -*- coding: utf-8 -*-
"""
Flask Extensions

Centralized extension instances to avoid circular imports.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()
cors = CORS()
