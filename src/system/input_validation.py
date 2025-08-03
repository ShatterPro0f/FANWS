"""
FANWS Input Validation System

Comprehensive validation for user inputs including API keys, project settings,
file paths, and configuration parameters.
"""

import re
import os
import json
import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ValidationResult:
    """Result of input validation."""

    def __init__(self, is_valid: bool, message: str = "", suggestions: List[str] = None):
        self.is_valid = is_valid
        self.message = message
        self.suggestions = suggestions or []

    def __bool__(self):
        return self.is_valid

class InputType(Enum):
    """Types of inputs that can be validated."""
    API_KEY = "api_key"
    PROJECT_NAME = "project_name"
    FILE_PATH = "file_path"
    DIRECTORY_PATH = "directory_path"
    EMAIL = "email"
    URL = "url"
    JSON_CONFIG = "json_config"
    NUMERIC = "numeric"
    TEXT = "text"

class APIProvider(Enum):
    """Supported API providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    HUGGINGFACE = "huggingface"
    WORDSAPI = "wordsapi"

class InputValidator:
    """Comprehensive input validation system."""

    def __init__(self):
        self.api_key_patterns = {
            APIProvider.OPENAI: {
                'pattern': r'^sk-[A-Za-z0-9]{20}T3BlbkFJ[A-Za-z0-9]{20}$',
                'min_length': 51,
                'max_length': 51,
                'description': 'OpenAI API keys start with "sk-" and are 51 characters long'
            },
            APIProvider.ANTHROPIC: {
                'pattern': r'^sk-ant-api03-[A-Za-z0-9_-]{95}$',
                'min_length': 108,
                'max_length': 108,
                'description': 'Anthropic API keys start with "sk-ant-api03-" and are 108 characters long'
            },
            APIProvider.GOOGLE: {
                'pattern': r'^[A-Za-z0-9_-]{39}$',
                'min_length': 39,
                'max_length': 39,
                'description': 'Google API keys are typically 39 characters long'
            },
            APIProvider.HUGGINGFACE: {
                'pattern': r'^hf_[A-Za-z0-9]{34}$',
                'min_length': 37,
                'max_length': 37,
                'description': 'Hugging Face tokens start with "hf_" and are 37 characters long'
            },
            APIProvider.WORDSAPI: {
                'pattern': r'^[A-Za-z0-9]{50}$',
                'min_length': 50,
                'max_length': 50,
                'description': 'WordsAPI keys are typically 50 characters long'
            }
        }

    def validate_api_key(self, api_key: str, provider: APIProvider) -> ValidationResult:
        """Validate an API key for a specific provider."""
        if not api_key or not api_key.strip():
            return ValidationResult(False, "API key cannot be empty")

        api_key = api_key.strip()

        if provider not in self.api_key_patterns:
            return ValidationResult(False, f"Unknown API provider: {provider.value}")

        pattern_info = self.api_key_patterns[provider]

        # Check length
        if len(api_key) < pattern_info['min_length']:
            return ValidationResult(
                False,
                f"API key too short. Expected at least {pattern_info['min_length']} characters, got {len(api_key)}",
                [pattern_info['description']]
            )

        if len(api_key) > pattern_info['max_length']:
            return ValidationResult(
                False,
                f"API key too long. Expected at most {pattern_info['max_length']} characters, got {len(api_key)}",
                [pattern_info['description']]
            )

        # Check pattern (if strict validation is enabled)
        # For now, we'll use relaxed validation for better user experience
        if provider == APIProvider.OPENAI and not api_key.startswith('sk-'):
            return ValidationResult(
                False,
                "OpenAI API keys must start with 'sk-'",
                [pattern_info['description']]
            )

        if provider == APIProvider.ANTHROPIC and not api_key.startswith('sk-ant-'):
            return ValidationResult(
                False,
                "Anthropic API keys must start with 'sk-ant-'",
                [pattern_info['description']]
            )

        if provider == APIProvider.HUGGINGFACE and not api_key.startswith('hf_'):
            return ValidationResult(
                False,
                "Hugging Face tokens must start with 'hf_'",
                [pattern_info['description']]
            )

        # Check for common issues
        if ' ' in api_key:
            return ValidationResult(False, "API key cannot contain spaces")

        if api_key != api_key.strip():
            return ValidationResult(False, "API key cannot have leading/trailing whitespace")

        return ValidationResult(True, "API key format appears valid")

    def validate_project_name(self, project_name: str) -> ValidationResult:
        """Validate a project name."""
        if not project_name or not project_name.strip():
            return ValidationResult(False, "Project name cannot be empty")

        project_name = project_name.strip()

        # Check length
        if len(project_name) < 1:
            return ValidationResult(False, "Project name must be at least 1 character long")

        if len(project_name) > 50:
            return ValidationResult(False, "Project name cannot exceed 50 characters")

        # Check for invalid characters
        invalid_chars = r'[<>:"/\\|?*]'
        if re.search(invalid_chars, project_name):
            return ValidationResult(
                False,
                "Project name contains invalid characters",
                ["Avoid: < > : \" / \\ | ? *"]
            )

        # Check for reserved names
        reserved_names = {
            'con', 'prn', 'aux', 'nul', 'com1', 'com2', 'com3', 'com4', 'com5',
            'com6', 'com7', 'com8', 'com9', 'lpt1', 'lpt2', 'lpt3', 'lpt4',
            'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9', 'default', 'system'
        }

        if project_name.lower() in reserved_names:
            return ValidationResult(False, f"'{project_name}' is a reserved name")

        # Check for leading/trailing dots or spaces
        if project_name.startswith('.') or project_name.endswith('.'):
            return ValidationResult(False, "Project name cannot start or end with a dot")

        return ValidationResult(True, "Project name is valid")

    def validate_file_path(self, file_path: str, must_exist: bool = False,
                          allowed_extensions: List[str] = None) -> ValidationResult:
        """Validate a file path."""
        if not file_path or not file_path.strip():
            return ValidationResult(False, "File path cannot be empty")

        file_path = file_path.strip()

        try:
            path = Path(file_path)

            # Check if path is absolute (recommended for reliability)
            if not path.is_absolute():
                return ValidationResult(
                    False,
                    "Relative paths may cause issues",
                    ["Use absolute paths for better reliability"]
                )

            # Check if file exists (if required)
            if must_exist and not path.exists():
                return ValidationResult(False, f"File does not exist: {file_path}")

            # Check if it's actually a file (not a directory)
            if path.exists() and not path.is_file():
                return ValidationResult(False, f"Path is not a file: {file_path}")

            # Check file extension
            if allowed_extensions:
                if not any(file_path.lower().endswith(ext.lower()) for ext in allowed_extensions):
                    return ValidationResult(
                        False,
                        f"Invalid file extension",
                        [f"Allowed extensions: {', '.join(allowed_extensions)}"]
                    )

            # Check if parent directory exists (for new files)
            if not must_exist and not path.parent.exists():
                return ValidationResult(False, f"Parent directory does not exist: {path.parent}")

            return ValidationResult(True, "File path is valid")

        except Exception as e:
            return ValidationResult(False, f"Invalid file path: {str(e)}")

    def validate_directory_path(self, dir_path: str, must_exist: bool = False,
                               create_if_missing: bool = False) -> ValidationResult:
        """Validate a directory path."""
        if not dir_path or not dir_path.strip():
            return ValidationResult(False, "Directory path cannot be empty")

        dir_path = dir_path.strip()

        try:
            path = Path(dir_path)

            # Check if directory exists
            if must_exist and not path.exists():
                return ValidationResult(False, f"Directory does not exist: {dir_path}")

            # Check if it's actually a directory
            if path.exists() and not path.is_dir():
                return ValidationResult(False, f"Path is not a directory: {dir_path}")

            # Try to create directory if requested
            if create_if_missing and not path.exists():
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Created directory: {dir_path}")
                except Exception as e:
                    return ValidationResult(False, f"Cannot create directory: {str(e)}")

            # Check write permissions
            if path.exists():
                test_file = path / '.write_test'
                try:
                    test_file.touch()
                    test_file.unlink()
                except Exception:
                    return ValidationResult(False, f"No write permission for directory: {dir_path}")

            return ValidationResult(True, "Directory path is valid")

        except Exception as e:
            return ValidationResult(False, f"Invalid directory path: {str(e)}")

    def validate_json_config(self, json_str: str, required_keys: List[str] = None) -> ValidationResult:
        """Validate JSON configuration."""
        if not json_str or not json_str.strip():
            return ValidationResult(False, "JSON configuration cannot be empty")

        try:
            data = json.loads(json_str)

            if not isinstance(data, dict):
                return ValidationResult(False, "JSON must be an object/dictionary")

            # Check for required keys
            if required_keys:
                missing_keys = [key for key in required_keys if key not in data]
                if missing_keys:
                    return ValidationResult(
                        False,
                        f"Missing required keys: {', '.join(missing_keys)}",
                        [f"Required keys: {', '.join(required_keys)}"]
                    )

            return ValidationResult(True, "JSON configuration is valid")

        except json.JSONDecodeError as e:
            return ValidationResult(False, f"Invalid JSON: {str(e)}")

    def validate_numeric_input(self, value: str, min_value: float = None,
                              max_value: float = None, integer_only: bool = False) -> ValidationResult:
        """Validate numeric input."""
        if not value or not value.strip():
            return ValidationResult(False, "Numeric value cannot be empty")

        try:
            if integer_only:
                num_value = int(value)
            else:
                num_value = float(value)

            if min_value is not None and num_value < min_value:
                return ValidationResult(False, f"Value must be at least {min_value}")

            if max_value is not None and num_value > max_value:
                return ValidationResult(False, f"Value must be at most {max_value}")

            return ValidationResult(True, f"Valid {'integer' if integer_only else 'number'}")

        except ValueError:
            return ValidationResult(False, f"Invalid {'integer' if integer_only else 'number'}")

    def validate_text_input(self, text: str, min_length: int = 0, max_length: int = None,
                           required: bool = True, pattern: str = None) -> ValidationResult:
        """Validate text input."""
        if required and (not text or not text.strip()):
            return ValidationResult(False, "Text input is required")

        if not text:
            text = ""

        text = text.strip()

        if len(text) < min_length:
            return ValidationResult(False, f"Text must be at least {min_length} characters long")

        if max_length and len(text) > max_length:
            return ValidationResult(False, f"Text cannot exceed {max_length} characters")

        if pattern and text and not re.match(pattern, text):
            return ValidationResult(False, "Text does not match required pattern")

        return ValidationResult(True, "Text input is valid")

    def validate_project_settings(self, settings: Dict[str, Any]) -> Tuple[ValidationResult, Dict[str, ValidationResult]]:
        """Validate complete project settings."""
        results = {}
        overall_valid = True

        # Validate project name
        if 'name' in settings:
            results['name'] = self.validate_project_name(settings['name'])
            if not results['name']:
                overall_valid = False

        # Validate output directory
        if 'output_dir' in settings:
            results['output_dir'] = self.validate_directory_path(
                settings['output_dir'],
                create_if_missing=True
            )
            if not results['output_dir']:
                overall_valid = False

        # Validate word count goal
        if 'word_count_goal' in settings:
            results['word_count_goal'] = self.validate_numeric_input(
                str(settings['word_count_goal']),
                min_value=100,
                max_value=1000000,
                integer_only=True
            )
            if not results['word_count_goal']:
                overall_valid = False

        # Validate genre
        if 'genre' in settings:
            results['genre'] = self.validate_text_input(
                settings['genre'],
                min_length=2,
                max_length=50,
                required=False
            )
            if not results['genre']:
                overall_valid = False

        overall_result = ValidationResult(
            overall_valid,
            "All project settings are valid" if overall_valid else "Some project settings are invalid"
        )

        return overall_result, results

# Create global validator instance
validator = InputValidator()

def validate_input(input_type: InputType, value: Any, **kwargs) -> ValidationResult:
    """Convenience function for input validation."""
    if input_type == InputType.API_KEY:
        provider = kwargs.get('provider')
        if not provider:
            return ValidationResult(False, "API provider must be specified")
        return validator.validate_api_key(value, provider)

    elif input_type == InputType.PROJECT_NAME:
        return validator.validate_project_name(value)

    elif input_type == InputType.FILE_PATH:
        return validator.validate_file_path(
            value,
            must_exist=kwargs.get('must_exist', False),
            allowed_extensions=kwargs.get('allowed_extensions')
        )

    elif input_type == InputType.DIRECTORY_PATH:
        return validator.validate_directory_path(
            value,
            must_exist=kwargs.get('must_exist', False),
            create_if_missing=kwargs.get('create_if_missing', False)
        )

    elif input_type == InputType.JSON_CONFIG:
        return validator.validate_json_config(
            value,
            required_keys=kwargs.get('required_keys')
        )

    elif input_type == InputType.NUMERIC:
        return validator.validate_numeric_input(
            value,
            min_value=kwargs.get('min_value'),
            max_value=kwargs.get('max_value'),
            integer_only=kwargs.get('integer_only', False)
        )

    elif input_type == InputType.TEXT:
        return validator.validate_text_input(
            value,
            min_length=kwargs.get('min_length', 0),
            max_length=kwargs.get('max_length'),
            required=kwargs.get('required', True),
            pattern=kwargs.get('pattern')
        )

    else:
        return ValidationResult(False, f"Unknown input type: {input_type}")
