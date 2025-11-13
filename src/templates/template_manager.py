#!/usr/bin/env python3
"""
FANWS Template Manager - Unified Template System
Consolidates all template-related functionality including project templates,
custom templates, template creation, and template recommendations.

Consolidates:
- advanced_project_templates.py
- custom_template_creator.py
- template_project_creator.py
- prompt_template_manager.py
- template_recommendation_engine.py
"""

import os
import json
import sqlite3
import logging
import uuid
import copy
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Core Enums and Data Classes
class TemplateType(Enum):
    PROJECT = "project"
    PROMPT = "prompt"
    CUSTOM = "custom"
    WORKFLOW = "workflow"

class TemplateCategory(Enum):
    FICTION = "fiction"
    NON_FICTION = "non_fiction"
    ACADEMIC = "academic"
    BUSINESS = "business"
    CREATIVE = "creative"
    CUSTOM = "custom"

class WorkflowPromptType(Enum):
    """Specific prompt types for FANWS workflow steps"""
    SYNOPSIS_GENERATION = "synopsis_generation"
    OUTLINE_CREATION = "outline_creation"
    CHARACTER_PROFILES = "character_profiles"
    WORLD_BUILDING = "world_building"
    TIMELINE_GENERATION = "timeline_generation"
    CHAPTER_WRITING = "chapter_writing"
    DRAFT_POLISHING = "draft_polishing"
    CONTENT_ENHANCEMENT = "content_enhancement"
    CONSISTENCY_CHECK = "consistency_check"
    READING_LEVEL = "reading_level"
    # Additional templates for ContentGenerator
    STANDALONE_SYNOPSIS = "standalone_synopsis"
    STANDALONE_CHARACTER = "standalone_character"
    STANDALONE_WORLD = "standalone_world"

@dataclass
class TemplateMetadata:
    id: str
    name: str
    description: str
    category: TemplateCategory
    template_type: TemplateType
    version: str = "1.0"
    author: str = "FANWS"
    created_at: str = ""
    tags: List[str] = field(default_factory=list)

@dataclass
class WorkflowContext:
    """Context data for workflow-specific prompt generation"""
    project_name: str
    config: Dict[str, Any]
    file_cache: Any  # FileCache instance
    chapter: Optional[int] = None
    section: Optional[int] = None
    user_feedback: str = ""
    context_summary: str = ""
    chapter_word_count: int = 1000

@dataclass
class ProjectTemplate:
    metadata: TemplateMetadata
    structure: Dict[str, Any]
    files: Dict[str, str]
    settings: Dict[str, Any]

@dataclass
class PromptTemplate:
    metadata: TemplateMetadata
    template_text: str
    variables: List[str]
    examples: List[str] = field(default_factory=list)

# Simplified Template Manager
class TemplateManager:
    """Unified template management system"""

    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(exist_ok=True)

        # Template storage
        self.project_templates = {}
        self.prompt_templates = {}
        self.custom_templates = {}

        # Load existing templates
        self._load_templates()

        logger.info("Template Manager initialized")

    def _load_templates(self):
        """Load templates from storage"""
        try:
            # Load project templates
            project_dir = self.templates_dir / "projects"
            if project_dir.exists():
                for template_file in project_dir.glob("*.json"):
                    with open(template_file, 'r', encoding='utf-8') as f:
                        template_data = json.load(f)
                        template_id = template_data.get('metadata', {}).get('id')
                        if template_id:
                            self.project_templates[template_id] = template_data

            # Load prompt templates
            prompt_dir = self.templates_dir / "prompts"
            if prompt_dir.exists():
                for template_file in prompt_dir.glob("*.json"):
                    with open(template_file, 'r', encoding='utf-8') as f:
                        template_data = json.load(f)
                        template_id = template_data.get('metadata', {}).get('id')
                        if template_id:
                            self.prompt_templates[template_id] = template_data

        except Exception as e:
            logger.error(f"Error loading templates: {e}")

    def create_project_template(self, name: str, description: str,
                              category: TemplateCategory,
                              structure: Dict[str, Any]) -> str:
        """Create a new project template"""
        template_id = f"proj_{uuid.uuid4().hex[:8]}"

        metadata = TemplateMetadata(
            id=template_id,
            name=name,
            description=description,
            category=category,
            template_type=TemplateType.PROJECT,
            created_at=datetime.now().isoformat()
        )

        template = ProjectTemplate(
            metadata=metadata,
            structure=structure,
            files={},
            settings={}
        )

        # Store metadata values as JSON-serializable primitives (strings)
        self.project_templates[template_id] = {
            'metadata': {
                'id': metadata.id,
                'name': metadata.name,
                'description': metadata.description,
                'category': metadata.category.value if hasattr(metadata.category, 'value') else str(metadata.category),
                'template_type': metadata.template_type.value if hasattr(metadata.template_type, 'value') else str(metadata.template_type),
                'version': metadata.version,
                'author': metadata.author,
                'created_at': metadata.created_at,
                'tags': metadata.tags
            },
            'structure': structure,
            'files': {},
            'settings': {}
        }

        self._save_template(template_id, TemplateType.PROJECT)
        return template_id

    def create_prompt_template(self, name: str, description: str,
                             template_text: str, variables: List[str]) -> str:
        """Create a new prompt template"""
        template_id = f"prompt_{uuid.uuid4().hex[:8]}"

        metadata = TemplateMetadata(
            id=template_id,
            name=name,
            description=description,
            category=TemplateCategory.CREATIVE,
            template_type=TemplateType.PROMPT,
            created_at=datetime.now().isoformat()
        )

        template = PromptTemplate(
            metadata=metadata,
            template_text=template_text,
            variables=variables
        )

        self.prompt_templates[template_id] = {
            'metadata': {
                'id': metadata.id,
                'name': metadata.name,
                'description': metadata.description,
                'category': metadata.category.value if hasattr(metadata.category, 'value') else str(metadata.category),
                'template_type': metadata.template_type.value if hasattr(metadata.template_type, 'value') else str(metadata.template_type),
                'version': metadata.version,
                'author': metadata.author,
                'created_at': metadata.created_at,
                'tags': metadata.tags
            },
            'template_text': template_text,
            'variables': variables,
            'examples': []
        }

        self._save_template(template_id, TemplateType.PROMPT)
        return template_id

    def _save_template(self, template_id: str, template_type: TemplateType):
        """Save template to storage"""
        try:
            if template_type == TemplateType.PROJECT:
                save_dir = self.templates_dir / "projects"
                template_data = self.project_templates[template_id]
            elif template_type == TemplateType.PROMPT:
                save_dir = self.templates_dir / "prompts"
                template_data = self.prompt_templates[template_id]
            else:
                return

            save_dir.mkdir(exist_ok=True)

            # Sanitize template_data for JSON serialization: convert Enum objects to their values
            sanitized = copy.deepcopy(template_data)
            metadata = sanitized.get('metadata')
            if isinstance(metadata, dict):
                # Convert TemplateCategory and TemplateType enums to strings when present
                cat = metadata.get('category')
                if hasattr(cat, 'value'):
                    try:
                        metadata['category'] = cat.value
                    except Exception:
                        metadata['category'] = str(cat)

                ttype = metadata.get('template_type')
                if hasattr(ttype, 'value'):
                    try:
                        metadata['template_type'] = ttype.value
                    except Exception:
                        metadata['template_type'] = str(ttype)

            with open(save_dir / f"{template_id}.json", 'w', encoding='utf-8') as f:
                json.dump(sanitized, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Error saving template {template_id}: {e}")

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get template by ID"""
        if template_id in self.project_templates:
            return self.project_templates[template_id]
        elif template_id in self.prompt_templates:
            return self.prompt_templates[template_id]
        elif template_id in self.custom_templates:
            return self.custom_templates[template_id]
        return None

    def list_templates(self, template_type: Optional[TemplateType] = None,
                      category: Optional[TemplateCategory] = None) -> List[Dict[str, Any]]:
        """List templates with optional filtering"""
        templates = []

        # Collect all templates
        all_templates = {**self.project_templates, **self.prompt_templates, **self.custom_templates}

        for template_id, template_data in all_templates.items():
            metadata = template_data.get('metadata', {})

            # Apply filters
            if template_type and metadata.get('template_type') != template_type.value:
                continue
            if category and metadata.get('category') != category.value:
                continue

            templates.append({
                'id': template_id,
                'name': metadata.get('name', ''),
                'description': metadata.get('description', ''),
                'type': metadata.get('template_type', ''),
                'category': metadata.get('category', ''),
                'created_at': metadata.get('created_at', '')
            })

        return templates

    def delete_template(self, template_id: str) -> bool:
        """Delete a template"""
        try:
            # Remove from memory
            if template_id in self.project_templates:
                del self.project_templates[template_id]
                template_file = self.templates_dir / "projects" / f"{template_id}.json"
            elif template_id in self.prompt_templates:
                del self.prompt_templates[template_id]
                template_file = self.templates_dir / "prompts" / f"{template_id}.json"
            elif template_id in self.custom_templates:
                del self.custom_templates[template_id]
                template_file = self.templates_dir / "custom" / f"{template_id}.json"
            else:
                return False

            # Remove file if exists
            if template_file.exists():
                template_file.unlink()

            return True

        except Exception as e:
            logger.error(f"Error deleting template {template_id}: {e}")
            return False

    def recommend_templates(self, project_type: str, genre: str = None) -> List[str]:
        """Get template recommendations based on project requirements"""
        recommendations = []

        # Simple recommendation logic
        for template_id, template_data in self.project_templates.items():
            metadata = template_data.get('metadata', {})

            # Match by category
            if genre and metadata.get('category') == genre.lower():
                recommendations.append(template_id)
            elif project_type.lower() in metadata.get('description', '').lower():
                recommendations.append(template_id)

        # Limit to top 5 recommendations
        return recommendations[:5]

    def export_template(self, template_id: str, export_path: str) -> bool:
        """Export template to file"""
        try:
            template_data = self.get_template(template_id)
            if not template_data:
                return False

            # Sanitize template_data for JSON serialization
            sanitized = copy.deepcopy(template_data)
            meta = sanitized.get('metadata', {})
            if isinstance(meta, dict):
                cat = meta.get('category')
                if hasattr(cat, 'value'):
                    meta['category'] = cat.value
                meta_type = meta.get('template_type')
                if hasattr(meta_type, 'value'):
                    meta['template_type'] = meta_type.value

            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(sanitized, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            logger.error(f"Error exporting template {template_id}: {e}")
            return False

    def import_template(self, import_path: str) -> Optional[str]:
        """Import template from file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)

            metadata = template_data.get('metadata', {})
            template_type = metadata.get('template_type')

            if template_type == 'project':
                template_id = metadata.get('id', f"proj_{uuid.uuid4().hex[:8]}")
                self.project_templates[template_id] = template_data
                self._save_template(template_id, TemplateType.PROJECT)
            elif template_type == 'prompt':
                template_id = metadata.get('id', f"prompt_{uuid.uuid4().hex[:8]}")
                self.prompt_templates[template_id] = template_data
                self._save_template(template_id, TemplateType.PROMPT)
            else:
                return None

            return template_id

        except Exception as e:
            logger.error(f"Error importing template from {import_path}: {e}")
            return None

# Simplified Custom Template Creator
class CustomTemplateCreator:
    """Create custom templates based on user specifications"""

    def __init__(self, template_manager: TemplateManager):
        self.template_manager = template_manager

    def create_from_project(self, project_path: str, template_name: str,
                          description: str = "") -> Optional[str]:
        """Create template from existing project structure"""
        try:
            # Verify project path exists
            if not os.path.exists(project_path):
                logger.error(f"Project path does not exist: {project_path}")
                return None

            project_structure = self._analyze_project_structure(project_path)

            template_id = self.template_manager.create_project_template(
                name=template_name,
                description=description or f"Template created from {project_path}",
                category=TemplateCategory.CUSTOM,
                structure=project_structure
            )

            return template_id

        except Exception as e:
            logger.error(f"Error creating template from project: {e}")
            return None

    def _analyze_project_structure(self, project_path: str) -> Dict[str, Any]:
        """Analyze project directory structure"""
        structure = {}

        try:
            for root, dirs, files in os.walk(project_path):
                rel_path = os.path.relpath(root, project_path)
                if rel_path == '.':
                    rel_path = ''

                structure[rel_path] = {
                    'directories': dirs,
                    'files': files
                }

        except Exception as e:
            logger.error(f"Error analyzing project structure: {e}")

        return structure

# Factory functions for backward compatibility
def get_template_manager(templates_dir: str = "templates") -> TemplateManager:
    """Get template manager instance"""
    return TemplateManager(templates_dir)

def get_custom_template_creator(template_manager: TemplateManager = None) -> CustomTemplateCreator:
    """Get custom template creator instance"""
    if template_manager is None:
        template_manager = get_template_manager()
    return CustomTemplateCreator(template_manager)

# Legacy compatibility functions
def get_project_templates():
    """Legacy compatibility function"""
    return get_template_manager()

def get_template_recommendation_engine():
    """Legacy compatibility function"""
    return get_template_manager()

# Export main classes for external use
__all__ = [
    'TemplateManager',
    'CustomTemplateCreator',
    'TemplateType',
    'TemplateCategory',
    'TemplateMetadata',
    'ProjectTemplate',
    'PromptTemplate',
    'get_template_manager',
    'get_custom_template_creator',
    'get_project_templates',
    'get_template_recommendation_engine'
]

class TemplateSystem:
    """Main template system class."""

    def __init__(self):
        self.templates = {}
        self.manager = TemplateManager()

    def register_template(self, name: str, template: Dict[str, Any]):
        """Register a template."""
        self.templates[name] = template

    def get_template(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a template by name."""
        return self.templates.get(name)

class TemplateCollection:
    """Collection of templates."""

    def __init__(self, name: str):
        self.name = name
        self.templates = []

    def add_template(self, template):
        """Add a template to the collection."""
        self.templates.append(template)

class TemplateRecommendationEngine:
    """Template recommendation engine."""

    def __init__(self):
        self.recommendations = []

    def get_recommendations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get template recommendations based on context."""
        return self.recommendations

class TemplateVersionManager:
    """Manages template versions."""

    def __init__(self):
        self.versions = {}

    def create_version(self, template_id: str, version_data: Dict[str, Any]):
        """Create a new template version."""
        if template_id not in self.versions:
            self.versions[template_id] = []
        self.versions[template_id].append(version_data)

def create_template_manager() -> TemplateManager:
    """Create and return a template manager instance."""
    return TemplateManager()

class TemplateIntegration:
    """Integration layer for templates."""

    def __init__(self, template_manager):
        self.template_manager = template_manager
