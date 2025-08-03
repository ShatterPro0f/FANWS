"""
Project Management Utilities
High-level utilities for managing FANWS projects using the existing PerProjectConfigManager
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from src.per_project_config_manager import PerProjectConfigManager

def list_projects() -> List[Dict[str, Any]]:
    """List all available projects."""
    projects = []
    projects_dir = Path("projects")

    if not projects_dir.exists():
        return projects

    for project_path in projects_dir.iterdir():
        if project_path.is_dir():
            project_info = get_project_info(project_path.name)
            if project_info:
                projects.append(project_info)

    return projects

def get_project_info(project_name: str) -> Optional[Dict[str, Any]]:
    """Get information about a specific project."""
    project_path = Path("projects") / project_name

    if not project_path.exists():
        return None

    # Try to load project configuration
    config_manager = PerProjectConfigManager(project_name)
    try:
        config_manager.load_config()
        project_config = config_manager.get_all_settings()
    except:
        project_config = {}

    return {
        'name': project_name,
        'path': str(project_path),
        'config': project_config,
        'exists': True,
        'has_config': bool(project_config)
    }

def create_project(project_name: str, description: str = None) -> bool:
    """Create a new project using the existing PerProjectConfigManager."""
    try:
        if not validate_project_name(project_name):
            return False

        # Use the existing PerProjectConfigManager to create and initialize the project
        config_manager = PerProjectConfigManager(project_name)
        config_manager.initialize_project_config()

        # Update the description if provided
        if description:
            config_manager.set('description', description)

        return True

    except Exception as e:
        print(f"Error creating project {project_name}: {e}")
        return False

def delete_project(project_name: str) -> bool:
    """Delete a project."""
    try:
        project_path = Path("projects") / project_name
        if project_path.exists():
            import shutil
            shutil.rmtree(project_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting project {project_name}: {e}")
        return False

def validate_project_name(name: str) -> bool:
    """Validate project name."""
    if not name or len(name.strip()) == 0:
        return False

    # Check for invalid characters
    invalid_chars = '<>:"/\\|?*'
    if any(char in name for char in invalid_chars):
        return False

    return True

def get_project_manager(project_name: str) -> PerProjectConfigManager:
    """Get a configured PerProjectConfigManager instance for a project."""
    return PerProjectConfigManager(project_name)

def migrate_all_projects():
    """Migrate all existing projects to use proper configuration."""
    from src.per_project_config_manager import migrate_all_projects_to_isolation
    migrate_all_projects_to_isolation()

# Aliases for backward compatibility
list_all_projects = list_projects
create_new_project = create_project
remove_project = delete_project
check_project_name = validate_project_name
