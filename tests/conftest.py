"""
Test configuration and fixtures for pytest tests
"""

import pytest
import tempfile
import shutil
import os
import sys
from unittest.mock import Mock, patch

# Add src to path for all tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Global test fixtures and configuration

@pytest.fixture(scope="session")
def temp_test_dir():
    """Create a temporary directory for test session"""
    temp_dir = tempfile.mkdtemp(prefix="fanws_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def temp_dir():
    """Create a temporary directory for individual tests"""
    temp_dir = tempfile.mkdtemp(prefix="fanws_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def mock_logger():
    """Mock logger for testing"""
    with patch('logging.getLogger') as mock_get_logger:
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        yield mock_logger

@pytest.fixture
def sample_project_structure():
    """Sample project structure for testing"""
    return {
        "chapters": {"type": "directory"},
        "characters": {"type": "directory"},
        "research": {"type": "directory"},
        "outline.txt": {"type": "file", "content": "Story outline"},
        "settings.json": {"type": "file", "content": '{"genre": "fantasy"}'}
    }

@pytest.fixture
def sample_template_metadata():
    """Sample template metadata for testing"""
    return {
        "id": "test_template_123",
        "name": "Test Template",
        "description": "Template for testing purposes",
        "category": "fiction",
        "template_type": "project",
        "version": "1.0",
        "author": "Test Author",
        "created_at": "2024-01-01T00:00:00",
        "tags": ["test", "sample"]
    }

@pytest.fixture
def mock_api_response():
    """Mock AI API response for testing"""
    return {
        "choices": [{
            "message": {
                "content": "This is a test AI response for story generation."
            }
        }],
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 15,
            "total_tokens": 65
        }
    }

@pytest.fixture
def mock_export_validation_result():
    """Mock export validation result"""
    class MockValidationResult:
        def __init__(self, is_valid=True, format_type="DOCX", file_path="test.docx"):
            self.is_valid = is_valid
            self.format_type = format_type
            self.file_path = file_path
            self.message = "Validation successful" if is_valid else "Validation failed"
            self.warnings = []
            self.metadata = {"word_count": 250}

    return MockValidationResult

# Test markers for organization
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.ui = pytest.mark.ui
pytest.mark.slow = pytest.mark.slow

# Skip conditions
try:
    import PyQt5
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Test data constants
TEST_PROJECT_CONFIG = {
    "name": "Test Novel",
    "genre": "Fantasy",
    "style": "Epic",
    "target_audience": "Young Adult",
    "themes": ["friendship", "courage", "growth"],
    "characters": [
        {"name": "Alex", "role": "protagonist"},
        {"name": "Morgan", "role": "mentor"}
    ],
    "setting": "Medieval fantasy world"
}

TEST_PLUGIN_MANIFEST = {
    "name": "test_plugin",
    "version": "1.0.0",
    "author": "Test Author",
    "description": "A test plugin for validation",
    "plugin_type": "content_generator",
    "api_version": "1.0.0",
    "dependencies": ["requests"],
    "permissions": ["file_read", "api_access"],
    "entry_point": "TestPlugin",
    "required_methods": ["generate_content", "get_supported_types"]
}

# Test utilities
def create_mock_file(file_path, content=""):
    """Create a mock file for testing"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def create_mock_json_file(file_path, data):
    """Create a mock JSON file for testing"""
    import json
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def assert_file_exists(file_path):
    """Assert that a file exists"""
    assert os.path.exists(file_path), f"File should exist: {file_path}"

def assert_file_not_exists(file_path):
    """Assert that a file does not exist"""
    assert not os.path.exists(file_path), f"File should not exist: {file_path}"

def assert_directory_exists(dir_path):
    """Assert that a directory exists"""
    assert os.path.isdir(dir_path), f"Directory should exist: {dir_path}"
