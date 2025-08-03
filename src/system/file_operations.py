"""
File operations module for FANWS application.
Handles all file I/O operations, project management, and data persistence.
Includes memory management for large files and optimized operations.
"""

import os
import json
import shutil
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Generator
from pathlib import Path
from ..core.utils import project_file_path
from ..core.error_handling_system import ErrorHandler, FileOperationError
from ..database.database_manager import DatabaseManager
from .module_compatibility import safe_load_dotenv, safe_set_key

# Try to import memory manager, fallback to basic operations if not available
try:
    from .memory_manager import (
        get_memory_manager,
        read_file_memory_safe,
        process_large_file,
        analyze_file_memory_safe,
        LazyTextLoader
    )
    MEMORY_MANAGER_AVAILABLE = True
except ImportError:
    MEMORY_MANAGER_AVAILABLE = False
    logging.warning("Memory manager not available, using basic file operations")

class FileOperations:
    """File operations with memory management and optimization."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.memory_manager = None
        if MEMORY_MANAGER_AVAILABLE:
            self.memory_manager = get_memory_manager()

    def read_file_smart(self, filepath: str, encoding: str = 'utf-8') -> Optional[Union[str, 'LazyTextLoader']]:
        """Smart file reading with automatic memory optimization."""
        try:
            if not os.path.exists(filepath):
                self.logger.warning(f"File not found: {filepath}")
                return None

            # Use memory-safe reading if available
            if self.memory_manager and MEMORY_MANAGER_AVAILABLE:
                if self.memory_manager.should_use_lazy_loading(filepath):
                    self.logger.info(f"Using lazy loading for large file: {filepath}")
                    return read_file_memory_safe(filepath)

            # Standard file reading
            with open(filepath, 'r', encoding=encoding) as f:
                content = f.read()

            self.logger.info(f"Successfully read content from {filepath}")
            return content

        except Exception as e:
            self.logger.error(f"Failed to read from {filepath}: {str(e)}")
            return None

    def read_file_chunked(self, filepath: str, chunk_size: int = 1024*1024,
                         encoding: str = 'utf-8') -> Generator[str, None, None]:
        """Read file in chunks for memory efficiency."""
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
        except Exception as e:
            self.logger.error(f"Error reading file chunks {filepath}: {e}")
            return

    def write_file_chunked(self, filepath: str, content_generator: Generator[str, None, None],
                          encoding: str = 'utf-8') -> bool:
        """Write content from generator to manage memory usage."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            with open(filepath, 'w', encoding=encoding) as f:
                for chunk in content_generator:
                    f.write(chunk)

            self.logger.info(f"Successfully wrote chunked content to {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Error writing file chunks {filepath}: {e}")
            return False

    def analyze_file_smart(self, filepath: str) -> Dict[str, Any]:
        """Analyze file content without loading entire file into memory."""
        try:
            if self.memory_manager and MEMORY_MANAGER_AVAILABLE:
                return analyze_file_memory_safe(filepath)

            # Fallback analysis
            size = os.path.getsize(filepath)
            lines = 0
            words = 0
            chars = 0

            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    lines += 1
                    chars += len(line)
                    words += len(line.split())

            return {
                'size_bytes': size,
                'line_count': lines,
                'word_count': words,
                'char_count': chars,
                'avg_line_length': chars / max(lines, 1)
            }

        except Exception as e:
            self.logger.error(f"Failed to analyze file {filepath}: {e}")
            return {}

    def process_large_file_smart(self, input_path: str, output_path: str,
                               processor: callable) -> bool:
        """Process large files with memory-safe streaming."""
        try:
            if self.memory_manager and MEMORY_MANAGER_AVAILABLE:
                return process_large_file(input_path, processor, output_path)

            # Fallback processing
            with open(input_path, 'r', encoding='utf-8') as infile:
                with open(output_path, 'w', encoding='utf-8') as outfile:
                    chunk_size = 1024 * 1024  # 1MB chunks
                    while True:
                        chunk = infile.read(chunk_size)
                        if not chunk:
                            break
                        processed_chunk = processor(chunk)
                        outfile.write(processed_chunk)

            return True

        except Exception as e:
            self.logger.error(f"Failed to process large file {input_path}: {e}")
            return False

# Global file operations instance
_file_ops = FileOperations()

def read_file_smart(filepath: str, encoding: str = 'utf-8') -> Optional[Union[str, 'LazyTextLoader']]:
    """Smart file reading with memory optimization."""
    return _file_ops.read_file_smart(filepath, encoding)

def read_file(filepath: str, encoding: str = 'utf-8') -> Optional[str]:
    """Simple file reading that returns string content."""
    result = _file_ops.read_file_smart(filepath, encoding)
    # If it's a LazyTextLoader, convert to string
    if hasattr(result, 'get_content'):
        return result.get_content()
    return result

def analyze_file_smart(filepath: str) -> Dict[str, Any]:
    """Smart file analysis without loading entire file."""
    return _file_ops.analyze_file_smart(filepath)

def process_large_file_smart(input_path: str, output_path: str, processor: callable) -> bool:
    """Smart large file processing with memory safety."""
    return _file_ops.process_large_file_smart(input_path, output_path, processor)

class FileCache:
    """Simple file cache for async operations."""

    def __init__(self, cache_dir: str = "cache"):
        """Initialize file cache."""
        self.cache_dir = cache_dir
        self.cache_data = {}
        os.makedirs(cache_dir, exist_ok=True)

    def get(self, key: str) -> Optional[Any]:
        """Get cached data."""
        return self.cache_data.get(key)

    def set(self, key: str, value: Any) -> None:
        """Set cached data."""
        self.cache_data[key] = value

    def clear(self) -> None:
        """Clear all cached data."""
        self.cache_data.clear()

    def has(self, key: str) -> bool:
        """Check if key exists in cache."""
        return key in self.cache_data

def save_to_file(filepath: str, content: str, encoding: str = 'utf-8') -> bool:
    """Save content to a file with error handling."""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'w', encoding=encoding) as f:
            f.write(content)

        logging.info(f"Successfully saved content to {filepath}")
        return True
    except Exception as e:
        logging.error(f"Failed to save to {filepath}: {str(e)}")
        return False

def load_project_env(project_name: str) -> Dict[str, Any]:
    """Load project environment variables and settings."""
    try:
        env_path = project_file_path(project_name, '.env')
        config_path = project_file_path(project_name, 'config.json')

        env_data = {}
        if os.path.exists(env_path):
            safe_load_dotenv(env_path)
            # Load common environment variables
            env_data.update({
                'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
                'WORDSAPI_KEY': os.getenv('WORDSAPI_KEY', ''),
            })

        config_data = {}
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_data = json.load(f)

        return {**env_data, **config_data}
    except Exception as e:
        logging.error(f"Failed to load project environment for {project_name}: {str(e)}")
        return {}

def save_project_env(project_name: str, openai_key: str = None, thesaurus_key: str = None) -> bool:
    """Save API keys to project environment (legacy compatibility function)."""
    if isinstance(openai_key, dict):
        # New style: single dict parameter
        return save_project_env_dict(project_name, openai_key)
    elif openai_key is not None and thesaurus_key is not None:
        # Legacy style: two string parameters
        env_data = {
            'OPENAI_API_KEY': openai_key,
            'WORDSAPI_KEY': thesaurus_key
        }
        return save_project_env_dict(project_name, env_data)
    else:
        logging.error(f"Invalid parameters for save_project_env: {openai_key}, {thesaurus_key}")
        return False

def save_project_env_dict(project_name: str, env_data: Dict[str, Any]) -> bool:
    """Save project environment variables and settings."""
    try:
        env_path = project_file_path(project_name, '.env')
        config_path = project_file_path(project_name, 'config.json')

        # Save API keys to .env file
        env_vars = {
            'OPENAI_API_KEY': env_data.get('OPENAI_API_KEY', ''),
            'WORDSAPI_KEY': env_data.get('WORDSAPI_KEY', ''),
        }

        # Create .env file content
        env_content = '\n'.join([f"{key}={value}" for key, value in env_vars.items() if value])
        save_to_file(env_path, env_content)

        # Save other config data to JSON
        config_data = {k: v for k, v in env_data.items() if k not in env_vars}
        if config_data:
            save_to_file(config_path, json.dumps(config_data, indent=2))

        return True
    except Exception as e:
        logging.error(f"Failed to save project environment for {project_name}: {str(e)}")
        return False

def get_project_list() -> List[str]:
    """Get list of all available projects."""
    try:
        projects_dir = os.path.join(os.getcwd(), 'projects')
        if not os.path.exists(projects_dir):
            os.makedirs(projects_dir, exist_ok=True)
            return []

        projects = [
            name for name in os.listdir(projects_dir)
            if os.path.isdir(os.path.join(projects_dir, name))
        ]

        return sorted(projects)
    except Exception as e:
        logging.error(f"Failed to get project list: {str(e)}")
        return []

def create_backup(project_name: str) -> bool:
    """Create a backup of the project."""
    try:
        project_dir = project_file_path(project_name, '')
        backup_dir = project_file_path(project_name, f'backups/{datetime.now().strftime("%Y%m%d_%H%M%S")}')

        if os.path.exists(project_dir):
            shutil.copytree(project_dir, backup_dir)
            logging.info(f"Created backup for project {project_name}")
            return True
        else:
            logging.warning(f"Project directory not found: {project_dir}")
            return False
    except Exception as e:
        logging.error(f"Failed to create backup for {project_name}: {str(e)}")
        return False

def load_synonym_cache(project_name: str) -> Dict[str, List[str]]:
    """Load synonym cache for a project."""
    try:
        cache_path = project_file_path(project_name, 'cache/synonyms.json')
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logging.error(f"Failed to load synonym cache for {project_name}: {str(e)}")
        return {}

def save_synonym_cache(project_name: str, cache_data: Dict[str, List[str]]) -> bool:
    """Save synonym cache for a project."""
    try:
        cache_path = project_file_path(project_name, 'cache/synonyms.json')
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)

        with open(cache_path, 'w') as f:
            json.dump(cache_data, f, indent=2)

        return True
    except Exception as e:
        logging.error(f"Failed to save synonym cache for {project_name}: {str(e)}")
        return False

def load_wordsapi_log(project_name: str) -> List[Dict[str, Any]]:
    """Load WordsAPI call log for a project."""
    try:
        log_path = project_file_path(project_name, 'logs/wordsapi.json')
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        logging.error(f"Failed to load WordsAPI log for {project_name}: {str(e)}")
        return []

def save_wordsapi_log(project_name: str, log_data: List[Dict[str, Any]]) -> bool:
    """Save WordsAPI call log for a project."""
    try:
        log_path = project_file_path(project_name, 'logs/wordsapi.json')
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)

        return True
    except Exception as e:
        logging.error(f"Failed to save WordsAPI log for {project_name}: {str(e)}")
        return False

def log_wordsapi_call(project_name: str, word: str, response: Dict[str, Any]) -> bool:
    """Log a WordsAPI call."""
    try:
        log_data = load_wordsapi_log(project_name)
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'word': word,
            'response': response
        }
        log_data.append(log_entry)

        # Keep only last 1000 entries
        if len(log_data) > 1000:
            log_data = log_data[-1000:]

        return save_wordsapi_log(project_name, log_data)
    except Exception as e:
        logging.error(f"Failed to log WordsAPI call for {project_name}: {str(e)}")
        return False

def get_wordsapi_call_count(project_name: str) -> int:
    """Get count of WordsAPI calls for a project."""
    try:
        log_data = load_wordsapi_log(project_name)
        return len(log_data)
    except Exception as e:
        logging.error(f"Failed to get WordsAPI call count for {project_name}: {str(e)}")
        return 0

def validate_project_name(project_name: str) -> bool:
    """Validate project name format."""
    if not project_name or not project_name.strip():
        return False

    # Check for invalid characters
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    if any(char in project_name for char in invalid_chars):
        return False

    # Check length
    if len(project_name) > 255:
        return False

    return True

def initialize_project_files(project_name: str) -> bool:
    """Initialize comprehensive project file structure with all necessary files."""
    try:
        project_dir = project_file_path(project_name, '')

        # Create comprehensive directory structure
        directories = [
            'config',           # Configuration files
            'drafts',          # Draft versions
            'exports',         # Export outputs
            'cache',           # Cached data
            'logs',            # Project logs
            'backups',         # Backup files
            'research',        # Research materials
            'characters',      # Character development files
            'world_building',  # World building files
            'timeline',        # Timeline and chronology
            'chapters',        # Individual chapter files
            'notes',           # General notes
            'templates',       # Project-specific templates
            'collaboration',   # Collaboration files
            'analytics',       # Writing analytics data
            'metadata',        # Project metadata
            'assets'           # Images, references, etc.
        ]

        for dir_name in directories:
            dir_path = os.path.join(project_dir, dir_name)
            os.makedirs(dir_path, exist_ok=True)

        # Create comprehensive initial files with meaningful defaults
        initial_files = {
            # Core writing files
            'synopsis.txt': '# Project Synopsis\n\nProvide a brief overview of your story here.\n\n## Main Plot\n\n## Key Themes\n\n## Target Audience\n',
            'outline.txt': '# Story Outline\n\n## Act 1 - Setup\n\n## Act 2 - Confrontation\n\n## Act 3 - Resolution\n',
            'characters.txt': '# Main Characters\n\n## Protagonist\n- Name:\n- Age:\n- Background:\n- Motivation:\n- Character Arc:\n\n## Antagonist\n- Name:\n- Age:\n- Background:\n- Motivation:\n- Goals:\n\n## Supporting Characters\n',
            'world_building.txt': '# World Building\n\n## Setting\n- Time Period:\n- Location:\n- Society/Culture:\n\n## Rules and Logic\n- Magic System (if applicable):\n- Technology Level:\n- Social Structure:\n\n## Important Locations\n',
            'timeline.txt': '# Story Timeline\n\n## Backstory Events\n\n## Main Story Events\n\n## Future Events (if relevant)\n',
            'story.txt': '# Main Story\n\n## Chapter 1\n\nBegin your story here...\n',

            # Planning and organization files
            'plot_points.txt': '# Plot Points\n\n## Key Events\n- [ ] Inciting Incident\n- [ ] Plot Point 1\n- [ ] Midpoint\n- [ ] Plot Point 2\n- [ ] Climax\n- [ ] Resolution\n\n## Subplots\n',
            'continuity_rules.txt': '# Continuity Rules\n\nMaintain consistency in:\n- Character traits and behaviors\n- World building elements\n- Timeline of events\n- Previously established facts\n',
            'themes.txt': '# Themes and Messages\n\n## Primary Theme\n\n## Secondary Themes\n\n## Symbolic Elements\n\n## Character Growth Themes\n',
            'research_notes.txt': '# Research Notes\n\n## Historical Research\n\n## Technical Research\n\n## Cultural Research\n\n## Other References\n',
            'chapter_summaries.txt': '# Chapter Summaries\n\n## Chapter 1\nSummary:\nKey Events:\nCharacter Development:\n\n## Chapter 2\n(Continue for each chapter...)\n',

            # Configuration files
            'config/project_settings.json': json.dumps({
                'project_name': project_name,
                'created': datetime.now().isoformat(),
                'last_modified': datetime.now().isoformat(),
                'version': '1.0',
                'author': '',
                'genre': '',
                'target_word_count': 50000,
                'current_word_count': 0,
                'completion_percentage': 0,
                'status': 'active',
                'tags': [],
                'language': 'en',
                'writing_goals': {
                    'daily_word_target': 500,
                    'weekly_word_target': 3500,
                    'estimated_completion_date': None
                }
            }, indent=2),

            'config/writing_style.json': json.dumps({
                'tone': 'neutral',
                'sub_tone': 'descriptive',
                'reading_level': 'adult',
                'perspective': 'third_person',
                'tense': 'past',
                'style_preferences': {
                    'show_vs_tell_ratio': 0.7,
                    'dialogue_frequency': 'moderate',
                    'description_detail': 'moderate',
                    'pacing': 'moderate'
                }
            }, indent=2),

            'config/character_config.json': json.dumps({
                'main_characters': [],
                'character_development_tracking': True,
                'character_voice_consistency': True,
                'relationship_mapping': {}
            }, indent=2),

            # Analytics and tracking files
            'analytics/writing_sessions.json': json.dumps({
                'sessions': [],
                'total_writing_time': 0,
                'average_words_per_minute': 0,
                'productive_hours': []
            }, indent=2),

            'analytics/progress_tracking.json': json.dumps({
                'daily_word_counts': {},
                'chapter_completion_dates': {},
                'revision_history': [],
                'milestone_dates': {}
            }, indent=2),

            # Collaboration files
            'collaboration/sharing_settings.json': json.dumps({
                'shared_with': [],
                'permissions': {},
                'collaboration_notes': [],
                'review_requests': []
            }, indent=2),

            # Metadata files
            'metadata/file_index.json': json.dumps({
                'files': {},
                'last_updated': datetime.now().isoformat(),
                'file_relationships': {}
            }, indent=2),

            'metadata/backup_info.json': json.dumps({
                'last_backup': None,
                'backup_frequency': 'daily',
                'backup_retention': 30,
                'auto_backup_enabled': True
            }, indent=2),

            # Template files
            'templates/chapter_template.txt': '# Chapter [NUMBER]: [TITLE]\n\n## Chapter Goals\n- \n\n## Key Events\n- \n\n## Character Development\n- \n\n---\n\n[Chapter content goes here...]\n',

            'templates/character_template.txt': '# Character Profile: [NAME]\n\n## Basic Information\n- Full Name:\n- Age:\n- Occupation:\n- Location:\n\n## Physical Description\n- Height:\n- Build:\n- Hair:\n- Eyes:\n- Notable Features:\n\n## Personality\n- Core Traits:\n- Strengths:\n- Flaws:\n- Fears:\n- Desires:\n\n## Background\n- Childhood:\n- Education:\n- Family:\n- Significant Events:\n\n## Role in Story\n- Character Arc:\n- Relationships:\n- Conflicts:\n- Growth:\n',

            # Notes and development files
            'notes/ideas.txt': '# Story Ideas and Inspiration\n\n## Random Ideas\n\n## "What If" Questions\n\n## Inspiration Sources\n\n## Future Story Possibilities\n',

            'notes/revision_notes.txt': '# Revision Notes\n\n## First Draft Issues\n\n## Plot Holes to Fix\n\n## Character Inconsistencies\n\n## Pacing Issues\n\n## Feedback to Address\n',

            'notes/worldbuilding_details.txt': '# Detailed World Building\n\n## Geography\n\n## Climate and Weather\n\n## Flora and Fauna\n\n## Resources and Economy\n\n## Politics and Government\n\n## Religion and Beliefs\n\n## Technology and Magic\n\n## Social Customs\n',

            # Legacy compatibility
            'config.json': json.dumps({
                'created': datetime.now().isoformat(),
                'last_modified': datetime.now().isoformat(),
                'version': '1.0'
            }, indent=2)
        }

        for filename, content in initial_files.items():
            filepath = project_file_path(project_name, filename)
            if not os.path.exists(filepath):
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                save_to_file(filepath, content)

        logging.info(f"Initialized comprehensive project structure for {project_name}")
        return True
    except Exception as e:
        logging.error(f"Failed to initialize project files for {project_name}: {str(e)}")
        return False
