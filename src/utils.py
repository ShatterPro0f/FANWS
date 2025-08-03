"""
Utility functions for FANWS application.
"""

import os
import re
import json
import shutil
import hashlib
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path
from .constants import (
    DEFAULT_PROJECT_DIR, DEFAULT_CONFIG_DIR, DEFAULT_CACHE_DIR,
    VALIDATION_RULES, SUPPORTED_TEXT_FORMATS
)

def project_file_path(project_name: str, filename: str) -> str:
    """Return file path for project file with per-project isolation."""
    # Import here to avoid circular imports
    try:
        from .per_project_config_manager import PerProjectConfigManager
        config_manager = PerProjectConfigManager(project_name)
        return config_manager.get_project_file_path(filename)
    except ImportError:
        # Fallback to legacy behavior if new manager not available
        base_path = os.path.join("projects", project_name)
        if filename in ["config.txt", "synonyms_cache.txt", "wordsapi_log.txt", "context.txt", "plot_points.txt", "continuity_rules.txt"]:
            return os.path.join(base_path, "config", filename)
        elif filename.startswith("drafts/"):
            return os.path.join(base_path, filename)
        elif filename.startswith("backups/"):
            return os.path.join(base_path, filename)
        return os.path.join(base_path, filename)

def ensure_directory(path: str) -> bool:
    """Ensure directory exists, create if necessary."""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Failed to create directory {path}: {str(e)}")
        return False

def safe_filename(filename: str) -> str:
    """Make filename safe for all operating systems."""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'[^\w\-_\. ]', '', filename)

    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')

    # Ensure filename is not empty
    if not filename:
        filename = 'untitled'

    # Limit length
    if len(filename) > 200:
        filename = filename[:200]

    return filename

def get_file_size(file_path: str) -> int:
    """Get file size in bytes."""
    try:
        return os.path.getsize(file_path)
    except Exception:
        return 0

def get_file_modified_time(file_path: str) -> datetime:
    """Get file modification time."""
    try:
        timestamp = os.path.getmtime(file_path)
        return datetime.fromtimestamp(timestamp)
    except Exception:
        return datetime.now()

def calculate_file_hash(file_path: str) -> str:
    """Calculate MD5 hash of file."""
    try:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        logging.error(f"Failed to calculate hash for {file_path}: {str(e)}")
        return ""

def is_text_file(file_path: str) -> bool:
    """Check if file is a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1024)  # Try to read first 1KB
        return True
    except Exception:
        return False

def get_supported_formats() -> List[str]:
    """Get list of supported text file formats."""
    return SUPPORTED_TEXT_FORMATS

def validate_project_name(project_name: str) -> tuple[bool, str]:
    """Validate project name."""
    if not project_name:
        return False, "Project name cannot be empty"

    rules = VALIDATION_RULES['project_name']

    if len(project_name) < rules['min_length']:
        return False, f"Project name must be at least {rules['min_length']} characters"

    if len(project_name) > rules['max_length']:
        return False, f"Project name cannot exceed {rules['max_length']} characters"

    for char in rules['forbidden_chars']:
        if char in project_name:
            return False, f"Project name cannot contain '{char}'"

    return True, ""

def validate_chapter_name(chapter_name: str) -> tuple[bool, str]:
    """Validate chapter name."""
    if not chapter_name:
        return False, "Chapter name cannot be empty"

    rules = VALIDATION_RULES['chapter_name']

    if len(chapter_name) < rules['min_length']:
        return False, f"Chapter name must be at least {rules['min_length']} characters"

    if len(chapter_name) > rules['max_length']:
        return False, f"Chapter name cannot exceed {rules['max_length']} characters"

    for char in rules['forbidden_chars']:
        if char in chapter_name:
            return False, f"Chapter name cannot contain '{char}'"

    return True, ""

def validate_api_key(api_key: str) -> tuple[bool, str]:
    """Validate API key."""
    if not api_key:
        return False, "API key cannot be empty"

    rules = VALIDATION_RULES['api_key']

    if len(api_key) < rules['min_length']:
        return False, f"API key must be at least {rules['min_length']} characters"

    if len(api_key) > rules['max_length']:
        return False, f"API key cannot exceed {rules['max_length']} characters"

    return True, ""

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"

    units = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    while size_bytes >= 1024 and i < len(units) - 1:
        size_bytes /= 1024
        i += 1

    return f"{size_bytes:.1f} {units[i]}"

def format_time_duration(seconds: int) -> str:
    """Format time duration in human readable format."""
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        return f"{seconds // 60} minutes"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours} hours, {minutes} minutes"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days} days, {hours} hours"

def format_number(number: int) -> str:
    """Format number with thousands separators."""
    return f"{number:,}"

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length."""
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix

def count_words(text: str) -> int:
    """Count words in text."""
    if not text:
        return 0

    # Split by whitespace and filter out empty strings
    words = [word for word in text.split() if word.strip()]
    return len(words)

def count_characters(text: str, include_spaces: bool = True) -> int:
    """Count characters in text."""
    if not text:
        return 0

    if include_spaces:
        return len(text)
    else:
        return len(text.replace(' ', ''))

def count_sentences(text: str) -> int:
    """Count sentences in text."""
    if not text:
        return 0

    # Simple sentence counting using common sentence endings
    sentences = re.split(r'[.!?]+', text)
    return len([s for s in sentences if s.strip()])

def count_paragraphs(text: str) -> int:
    """Count paragraphs in text."""
    if not text:
        return 0

    # Split by double newlines (common paragraph separator)
    paragraphs = re.split(r'\n\s*\n', text)
    return len([p for p in paragraphs if p.strip()])

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text."""
    if not text:
        return []

    # Simple keyword extraction
    # Remove punctuation and convert to lowercase
    cleaned_text = re.sub(r'[^\w\s]', '', text.lower())

    # Split into words
    words = cleaned_text.split()

    # Remove common stop words
    stop_words = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
        'will', 'would', 'could', 'should', 'may', 'might', 'can', 'do', 'does',
        'did', 'a', 'an', 'as', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
        'this', 'that', 'these', 'those', 'my', 'your', 'his', 'her', 'its',
        'our', 'their', 'me', 'him', 'us', 'them', 'myself', 'yourself',
        'himself', 'herself', 'itself', 'ourselves', 'yourselves', 'themselves'
    }

    # Filter out stop words and short words
    keywords = [word for word in words if word not in stop_words and len(word) > 2]

    # Count frequency
    from collections import Counter
    word_counts = Counter(keywords)

    # Return most common words
    return [word for word, count in word_counts.most_common(max_keywords)]

def backup_file(file_path: str, backup_dir: str = None) -> str:
    """Create backup of file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if backup_dir is None:
        backup_dir = os.path.join(os.path.dirname(file_path), "backups")

    ensure_directory(backup_dir)

    # Generate backup filename with timestamp
    filename = os.path.basename(file_path)
    name, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{name}_{timestamp}{ext}"
    backup_path = os.path.join(backup_dir, backup_filename)

    # Copy file
    shutil.copy2(file_path, backup_path)

    return backup_path

def cleanup_old_backups(backup_dir: str, max_backups: int = 10):
    """Clean up old backup files."""
    if not os.path.exists(backup_dir):
        return

    try:
        # Get all backup files
        backup_files = []
        for filename in os.listdir(backup_dir):
            file_path = os.path.join(backup_dir, filename)
            if os.path.isfile(file_path):
                backup_files.append((file_path, os.path.getmtime(file_path)))

        # Sort by modification time (newest first)
        backup_files.sort(key=lambda x: x[1], reverse=True)

        # Remove old backups
        for file_path, _ in backup_files[max_backups:]:
            os.remove(file_path)
            logging.info(f"Removed old backup: {file_path}")

    except Exception as e:
        logging.error(f"Failed to cleanup old backups: {str(e)}")

def get_available_space(path: str) -> int:
    """Get available disk space in bytes."""
    try:
        statvfs = os.statvfs(path)
        return statvfs.f_frsize * statvfs.f_bavail
    except Exception:
        try:
            # Windows alternative
            import ctypes
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p(path),
                ctypes.pointer(free_bytes),
                None,
                None
            )
            return free_bytes.value
        except Exception:
            return 0

def is_low_disk_space(path: str, threshold_mb: int = 100) -> bool:
    """Check if disk space is low."""
    available_bytes = get_available_space(path)
    threshold_bytes = threshold_mb * 1024 * 1024
    return available_bytes < threshold_bytes

def merge_dictionaries(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two dictionaries recursively."""
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dictionaries(result[key], value)
        else:
            result[key] = value

    return result

def load_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """Load JSON file safely."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load JSON file {file_path}: {str(e)}")
        return None

def save_json_file(file_path: str, data: Dict[str, Any]) -> bool:
    """Save JSON file safely."""
    try:
        ensure_directory(os.path.dirname(file_path))
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logging.error(f"Failed to save JSON file {file_path}: {str(e)}")
        return False

def normalize_path(path: str) -> str:
    """Normalize file path for current operating system."""
    return os.path.normpath(os.path.expanduser(path))

def get_relative_path(file_path: str, base_path: str) -> str:
    """Get relative path from base path."""
    try:
        return os.path.relpath(file_path, base_path)
    except ValueError:
        return file_path

def is_within_directory(file_path: str, directory: str) -> bool:
    """Check if file is within directory."""
    try:
        abs_file_path = os.path.abspath(file_path)
        abs_directory = os.path.abspath(directory)
        return abs_file_path.startswith(abs_directory)
    except Exception:
        return False

def create_unique_filename(base_path: str, filename: str) -> str:
    """Create unique filename by adding number suffix if needed."""
    full_path = os.path.join(base_path, filename)

    if not os.path.exists(full_path):
        return filename

    name, ext = os.path.splitext(filename)
    counter = 1

    while True:
        new_filename = f"{name}_{counter}{ext}"
        new_path = os.path.join(base_path, new_filename)

        if not os.path.exists(new_path):
            return new_filename

        counter += 1

def get_project_names() -> List[str]:
    """Get list of existing project names."""
    projects_dir = DEFAULT_PROJECT_DIR
    if not os.path.exists(projects_dir):
        return []

    project_names = []
    for item in os.listdir(projects_dir):
        project_path = os.path.join(projects_dir, item)
        if os.path.isdir(project_path):
            project_names.append(item)

    return sorted(project_names)

def get_recent_projects(max_projects: int = 10) -> List[Dict[str, Any]]:
    """Get list of recent projects with metadata."""
    projects_dir = DEFAULT_PROJECT_DIR
    if not os.path.exists(projects_dir):
        return []

    projects = []
    for project_name in os.listdir(projects_dir):
        project_path = os.path.join(projects_dir, project_name)
        if os.path.isdir(project_path):
            try:
                modified_time = get_file_modified_time(project_path)
                projects.append({
                    'name': project_name,
                    'path': project_path,
                    'modified': modified_time,
                    'modified_str': modified_time.strftime("%Y-%m-%d %H:%M:%S")
                })
            except Exception as e:
                logging.error(f"Error getting project info for {project_name}: {str(e)}")

    # Sort by modification time (newest first)
    projects.sort(key=lambda x: x['modified'], reverse=True)

    return projects[:max_projects]

def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace and normalizing."""
    if not text:
        return ""

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text

def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences."""
    if not text:
        return []

    # Simple sentence splitting
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip()]

def generate_uuid() -> str:
    """Generate UUID string."""
    import uuid
    return str(uuid.uuid4())

def get_timestamp() -> str:
    """Get current timestamp string."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse timestamp string to datetime."""
    try:
        return datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
    except ValueError:
        return datetime.now()
