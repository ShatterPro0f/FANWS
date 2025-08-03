"""
Constants and configuration values for FANWS application.
"""

import os
from typing import Dict, Any, List

# Application Information
APP_NAME = "FANWS"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Fiction AI Novel Writing Suite"
APP_AUTHOR = "FANWS Development Team"

# Legacy API Constants (preserved for compatibility)
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
WORDSAPI_URL = "https://wordsapiv1.p.rapidapi.com/words/{}/synonyms"
DEFAULT_WORD_COUNTS = [10000, 25000, 50000, 75000, 100000, 150000, 200000, 250000]
TONE_MAP = {
    "dark": "gritty",
    "tense": "urgent",
    "humorous": "witty",
    "neutral": "neutral"
}

# File and Directory Constants
DEFAULT_PROJECT_DIR = "projects"
DEFAULT_CONFIG_DIR = "config"
DEFAULT_CACHE_DIR = "cache"
DEFAULT_LOGS_DIR = "logs"
DEFAULT_BACKUP_DIR = "backups"

# Database Constants
DATABASE_NAME = "fanws.db"
DATABASE_VERSION = 1

# File Extensions
SUPPORTED_TEXT_FORMATS = ['.txt', '.md', '.markdown', '.rtf']
SUPPORTED_PROJECT_FORMATS = ['.json', '.fanws']
SUPPORTED_EXPORT_FORMATS = ['.txt', '.md', '.html', '.pdf', '.docx']

# GUI Constants
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600
WINDOW_DEFAULT_WIDTH = 1200
WINDOW_DEFAULT_HEIGHT = 800

# Colors (hex values)
COLORS = {
    'primary': '#2C3E50',
    'secondary': '#3498DB',
    'accent': '#E74C3C',
    'success': '#27AE60',
    'warning': '#F39C12',
    'error': '#E74C3C',
    'info': '#3498DB',
    'light': '#ECF0F1',
    'dark': '#2C3E50',
    'background': '#FFFFFF',
    'text': '#2C3E50',
    'text_light': '#7F8C8D',
    'border': '#BDC3C7',
    'hover': '#34495E',
    'selected': '#3498DB',
    'disabled': '#95A5A6'
}

# Font Settings
FONTS = {
    'default': 'Arial',
    'monospace': 'Courier New',
    'serif': 'Times New Roman',
    'sans_serif': 'Arial'
}

FONT_SIZES = {
    'small': 8,
    'normal': 10,
    'medium': 12,
    'large': 14,
    'extra_large': 16,
    'title': 18,
    'heading': 20
}

# API Configuration
API_TIMEOUT = 30  # seconds
API_RETRY_COUNT = 3
API_RETRY_DELAY = 1  # seconds

# Rate Limiting
DEFAULT_RATE_LIMIT = 100  # requests per hour
API_RATE_LIMITS = {
    'openai': 3000,  # requests per minute
    'anthropic': 1000,  # requests per minute
    'google': 60,  # requests per minute
    'huggingface': 1000  # requests per hour
}

# Cache Settings
CACHE_MAX_SIZE = 1000  # items
CACHE_TTL = 3600  # seconds (1 hour)
FILE_CACHE_MAX_SIZE = 500  # items per project

# Text Processing
MAX_WORD_COUNT = 1000000  # Maximum words per project
MAX_CHAPTER_COUNT = 1000  # Maximum chapters per project
MAX_CHARACTER_COUNT = 10000000  # Maximum characters per project

# Writing Statistics
WORDS_PER_PAGE = 250  # Average words per page
READING_SPEED_WPM = 200  # Words per minute reading speed

# Project Templates
PROJECT_TEMPLATES = {
    'novel': {
        'name': 'Novel',
        'description': 'Full-length novel template',
        'structure': ['Chapter 1', 'Chapter 2', 'Chapter 3'],
        'word_count_goal': 80000
    },
    'short_story': {
        'name': 'Short Story',
        'description': 'Short story template',
        'structure': ['Beginning', 'Middle', 'End'],
        'word_count_goal': 5000
    },
    'novella': {
        'name': 'Novella',
        'description': 'Novella template',
        'structure': ['Part 1', 'Part 2', 'Part 3'],
        'word_count_goal': 30000
    },
    'screenplay': {
        'name': 'Screenplay',
        'description': 'Screenplay template',
        'structure': ['Act 1', 'Act 2', 'Act 3'],
        'word_count_goal': 25000
    }
}

# Export Settings
EXPORT_SETTINGS = {
    'txt': {
        'extension': '.txt',
        'mime_type': 'text/plain',
        'encoding': 'utf-8'
    },
    'md': {
        'extension': '.md',
        'mime_type': 'text/markdown',
        'encoding': 'utf-8'
    },
    'html': {
        'extension': '.html',
        'mime_type': 'text/html',
        'encoding': 'utf-8'
    },
    'pdf': {
        'extension': '.pdf',
        'mime_type': 'application/pdf'
    },
    'docx': {
        'extension': '.docx',
        'mime_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
}

# Default Configuration
DEFAULT_CONFIG = {
    'general': {
        'auto_save': True,
        'auto_save_interval': 300,
        'backup_enabled': True,
        'backup_interval': 1800,
        'theme': 'default',
        'language': 'en'
    },
    'editor': {
        'font_family': FONTS['default'],
        'font_size': FONT_SIZES['normal'],
        'line_spacing': 1.5,
        'word_wrap': True,
        'show_line_numbers': True,
        'highlight_current_line': True,
        'tab_size': 4,
        'insert_spaces': True
    },
    'ai': {
        'default_provider': 'openai',
        'model': 'gpt-3.5-turbo',
        'max_tokens': 500,
        'temperature': 0.7,
        'use_cache': True
    },
    'export': {
        'default_format': 'txt',
        'include_metadata': True,
        'include_statistics': False,
        'custom_css': ''
    },
    'performance': {
        'enable_monitoring': True,
        'monitor_interval': 60,
        'memory_threshold': 80,
        'cpu_threshold': 80
    }
}

# Validation Rules
VALIDATION_RULES = {
    'project_name': {
        'min_length': 1,
        'max_length': 100,
        'pattern': r'^[a-zA-Z0-9_\s\-\.]+$',
        'forbidden_chars': ['<', '>', ':', '"', '|', '?', '*', '/']
    },
    'novel_title': {
        'min_length': 1,
        'max_length': 200,
        'required': True
    },
    'chapter_title': {
        'min_length': 1,
        'max_length': 100,
        'required': False
    },
    'word_count': {
        'min_value': 1,
        'max_value': 1000000,
        'required': True
    },
    'api_key': {
        'min_length': 10,
        'max_length': 200,
        'required': True
    }
}

# Rate Limiting Constants
