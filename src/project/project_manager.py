"""
Project Manager Module
Handles project operations and management for FANWS
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Any

class ProjectManager:
    """Main project management class."""

    def __init__(self, projects_dir: str = "projects"):
        self.projects_dir = Path(projects_dir)
        self.projects_dir.mkdir(exist_ok=True)

    def list_projects(self) -> List[Dict[str, Any]]:
        """List all available projects."""
        projects = []

        if not self.projects_dir.exists():
            return projects

        for project_path in self.projects_dir.iterdir():
            if project_path.is_dir():
                project_info = self.get_project_info(project_path.name)
                if project_info:
                    projects.append(project_info)

        return projects

    def get_project_info(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific project."""
        project_path = self.projects_dir / project_name

        if not project_path.exists():
            return None

        # Try to load project metadata
        metadata_file = project_path / "metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            except (json.JSONDecodeError, IOError):
                metadata = {}
        else:
            metadata = {}

        return {
            'name': project_name,
            'path': str(project_path),
            'metadata': metadata,
            'exists': True
        }

    def create_project(self, project_name: str, metadata: Optional[Dict] = None) -> bool:
        """Create a new project."""
        try:
            project_path = self.projects_dir / project_name
            project_path.mkdir(exist_ok=True)

            # Create basic project structure
            (project_path / "documents").mkdir(exist_ok=True)
            (project_path / "research").mkdir(exist_ok=True)
            (project_path / "exports").mkdir(exist_ok=True)

            # Save metadata
            if metadata is None:
                metadata = {
                    'name': project_name,
                    'created': str(Path.ctime(project_path)),
                    'description': f'Project: {project_name}',
                    'type': 'general'
                }

            metadata_file = project_path / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"Error creating project {project_name}: {e}")
            return False

    def delete_project(self, project_name: str) -> bool:
        """Delete a project."""
        try:
            project_path = self.projects_dir / project_name
            if project_path.exists():
                import shutil
                shutil.rmtree(project_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting project {project_name}: {e}")
            return False

    def validate_project_name(self, name: str) -> bool:
        """Validate project name."""
        if not name or len(name.strip()) == 0:
            return False

        # Check for invalid characters
        invalid_chars = '<>:"/\\|?*'
        if any(char in name for char in invalid_chars):
            return False

        return True

# Global project manager instance
_project_manager = None

def get_project_manager() -> ProjectManager:
    """Get the global project manager instance."""
    global _project_manager
    if _project_manager is None:
        _project_manager = ProjectManager()
    return _project_manager

def list_projects() -> List[Dict[str, Any]]:
    """Convenience function to list projects."""
    return get_project_manager().list_projects()

def create_project(name: str, metadata: Optional[Dict] = None) -> bool:
    """Convenience function to create a project."""
    return get_project_manager().create_project(name, metadata)

def get_project_info(name: str) -> Optional[Dict[str, Any]]:
    """Convenience function to get project info."""
    return get_project_manager().get_project_info(name)

def validate_project_name(name: str) -> bool:
    """Convenience function to validate project name."""
    return get_project_manager().validate_project_name(name)
