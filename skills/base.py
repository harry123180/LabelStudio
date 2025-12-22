# -*- coding: utf-8 -*-
"""
Base Skill Class

Provides common functionality for all skills including:
- Database connection management
- Logging
- Error handling
- Configuration loading
"""
import os
import sys
import logging
from typing import Any, Dict, Optional
from abc import ABC, abstractmethod

# Add backend to path for imports
SKILLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SKILLS_DIR)
BACKEND_DIR = os.path.join(ROOT_DIR, 'backend')
sys.path.insert(0, BACKEND_DIR)


class BaseSkill(ABC):
    """Base class for all LabelStudio skills"""

    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize skill

        Args:
            data_dir: Path to data directory. If None, uses default.
        """
        self.data_dir = data_dir or self._get_default_data_dir()
        self.logger = self._setup_logging()
        self._app = None
        self._db = None

    def _get_default_data_dir(self) -> str:
        """Get default data directory"""
        return os.path.join(ROOT_DIR, 'data')

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for this skill"""
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    @property
    def app(self):
        """Get Flask app instance (lazy loading)"""
        if self._app is None:
            from app import create_app
            self._app = create_app()
        return self._app

    @property
    def db(self):
        """Get database session"""
        if self._db is None:
            from app import db
            self._db = db
        return self._db

    def execute_in_context(self, func, *args, **kwargs) -> Any:
        """Execute function within Flask app context"""
        with self.app.app_context():
            return func(*args, **kwargs)

    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """
        Return skill information for agent discovery

        Returns:
            Dict containing:
                - name: Skill name
                - description: What this skill does
                - methods: Available methods and their parameters
        """
        pass

    def log_action(self, action: str, details: Dict[str, Any] = None):
        """Log an action performed by this skill"""
        msg = f"Action: {action}"
        if details:
            msg += f" | Details: {details}"
        self.logger.info(msg)
