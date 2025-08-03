"""
Comprehensive pytest tests for src/template_manager.py
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from template_manager import (
    TemplateManager, CustomTemplateCreator, TemplateType, TemplateCategory,
    TemplateMetadata, ProjectTemplate, PromptTemplate, WorkflowContext,
    get_template_manager, get_custom_template_creator
)


class TestTemplateMetadata:
    """Test TemplateMetadata dataclass"""

    def test_template_metadata_creation(self):
        """Test creating TemplateMetadata instance"""
        metadata = TemplateMetadata(
            id="test_id",
            name="Test Template",
            description="A test template",
            category=TemplateCategory.FICTION,
            template_type=TemplateType.PROJECT
        )

        assert metadata.id == "test_id"
        assert metadata.name == "Test Template"
        assert metadata.description == "A test template"
        assert metadata.category == TemplateCategory.FICTION
        assert metadata.template_type == TemplateType.PROJECT
        assert metadata.version == "1.0"
        assert metadata.author == "FANWS"
        assert isinstance(metadata.tags, list)

    def test_template_metadata_with_custom_values(self):
        """Test TemplateMetadata with custom values"""
        metadata = TemplateMetadata(
            id="custom_id",
            name="Custom Template",
            description="Custom description",
            category=TemplateCategory.ACADEMIC,
            template_type=TemplateType.PROMPT,
            version="2.0",
            author="Custom Author",
            created_at="2024-01-01T00:00:00",
            tags=["tag1", "tag2"]
        )

        assert metadata.version == "2.0"
        assert metadata.author == "Custom Author"
        assert metadata.created_at == "2024-01-01T00:00:00"
        assert metadata.tags == ["tag1", "tag2"]


class TestWorkflowContext:
    """Test WorkflowContext dataclass"""

    def test_workflow_context_creation(self):
        """Test creating WorkflowContext instance"""
        context = WorkflowContext(
            project_name="Test Project",
            config={"key": "value"},
            file_cache=Mock()
        )

        assert context.project_name == "Test Project"
        assert context.config == {"key": "value"}
        assert context.file_cache is not None
        assert context.chapter is None
        assert context.section is None
        assert context.user_feedback == ""
        assert context.context_summary == ""
        assert context.chapter_word_count == 1000

    def test_workflow_context_with_all_fields(self):
        """Test WorkflowContext with all fields populated"""
        context = WorkflowContext(
            project_name="Full Project",
            config={"setting": "value"},
            file_cache=Mock(),
            chapter=5,
            section=2,
            user_feedback="Great work!",
            context_summary="Chapter summary",
            chapter_word_count=1500
        )

        assert context.chapter == 5
        assert context.section == 2
        assert context.user_feedback == "Great work!"
        assert context.context_summary == "Chapter summary"
        assert context.chapter_word_count == 1500


class TestTemplateManager:
    """Test TemplateManager class"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def template_manager(self, temp_dir):
        """Create TemplateManager instance with temporary directory"""
        return TemplateManager(temp_dir)

    def test_template_manager_initialization(self, temp_dir):
        """Test TemplateManager initialization"""
        manager = TemplateManager(temp_dir)

        assert manager.templates_dir == Path(temp_dir)
        assert manager.templates_dir.exists()
        assert isinstance(manager.project_templates, dict)
        assert isinstance(manager.prompt_templates, dict)
        assert isinstance(manager.custom_templates, dict)

    def test_create_project_template(self, template_manager):
        """Test creating a project template"""
        structure = {
            "chapters": {"type": "directory"},
            "characters": {"type": "directory"},
            "outline.txt": {"type": "file", "content": "Story outline"}
        }

        template_id = template_manager.create_project_template(
            name="Fantasy Novel",
            description="Template for fantasy novels",
            category=TemplateCategory.FICTION,
            structure=structure
        )

        assert template_id.startswith("proj_")
        assert template_id in template_manager.project_templates

        template = template_manager.project_templates[template_id]
        assert template['metadata']['name'] == "Fantasy Novel"
        assert template['metadata']['description'] == "Template for fantasy novels"
        assert template['metadata']['category'] == TemplateCategory.FICTION.value
        assert template['structure'] == structure

    def test_create_prompt_template(self, template_manager):
        """Test creating a prompt template"""
        template_text = "Write a {genre} story about {character} in {setting}"
        variables = ["genre", "character", "setting"]

        template_id = template_manager.create_prompt_template(
            name="Story Prompt",
            description="General story writing prompt",
            template_text=template_text,
            variables=variables
        )

        assert template_id.startswith("prompt_")
        assert template_id in template_manager.prompt_templates

        template = template_manager.prompt_templates[template_id]
        assert template['metadata']['name'] == "Story Prompt"
        assert template['template_text'] == template_text
        assert template['variables'] == variables

    def test_get_template(self, template_manager):
        """Test retrieving templates"""
        # Create templates first
        proj_id = template_manager.create_project_template(
            "Test Project", "Test description", TemplateCategory.FICTION, {}
        )
        prompt_id = template_manager.create_prompt_template(
            "Test Prompt", "Test description", "Test template", ["var1"]
        )

        # Test retrieval
        proj_template = template_manager.get_template(proj_id)
        prompt_template = template_manager.get_template(prompt_id)
        non_existent = template_manager.get_template("non_existent")

        assert proj_template is not None
        assert prompt_template is not None
        assert non_existent is None

        assert proj_template['metadata']['name'] == "Test Project"
        assert prompt_template['metadata']['name'] == "Test Prompt"

    def test_list_templates(self, template_manager):
        """Test listing templates with filters"""
        # Create different types of templates
        proj_id = template_manager.create_project_template(
            "Fiction Project", "Fiction template", TemplateCategory.FICTION, {}
        )
        prompt_id = template_manager.create_prompt_template(
            "Creative Prompt", "Creative prompt template", "Template text", ["var"]
        )

        # Test listing all templates
        all_templates = template_manager.list_templates()
        assert len(all_templates) == 2

        # Test filtering by type
        project_templates = template_manager.list_templates(
            template_type=TemplateType.PROJECT
        )
        assert len(project_templates) == 1
        assert project_templates[0]['name'] == "Fiction Project"

        prompt_templates = template_manager.list_templates(
            template_type=TemplateType.PROMPT
        )
        assert len(prompt_templates) == 1
        assert prompt_templates[0]['name'] == "Creative Prompt"

        # Test filtering by category
        fiction_templates = template_manager.list_templates(
            category=TemplateCategory.FICTION
        )
        assert len(fiction_templates) == 1
        assert fiction_templates[0]['name'] == "Fiction Project"

    def test_delete_template(self, template_manager):
        """Test deleting templates"""
        # Create template
        template_id = template_manager.create_project_template(
            "Delete Me", "Template to delete", TemplateCategory.FICTION, {}
        )

        # Verify it exists
        assert template_id in template_manager.project_templates
        assert template_manager.get_template(template_id) is not None

        # Delete template
        result = template_manager.delete_template(template_id)
        assert result is True

        # Verify it's gone
        assert template_id not in template_manager.project_templates
        assert template_manager.get_template(template_id) is None

        # Test deleting non-existent template
        result = template_manager.delete_template("non_existent")
        assert result is False

    def test_recommend_templates(self, template_manager):
        """Test template recommendations"""
        # Create templates with different characteristics
        template_manager.create_project_template(
            "Fantasy Novel", "Fantasy story template", TemplateCategory.FICTION, {}
        )
        template_manager.create_project_template(
            "Academic Paper", "Research paper template", TemplateCategory.ACADEMIC, {}
        )
        template_manager.create_project_template(
            "Short Story", "Short fiction template", TemplateCategory.FICTION, {}
        )

        # Test recommendations by genre
        fiction_recs = template_manager.recommend_templates("fiction", "fiction")
        assert len(fiction_recs) >= 2  # Should find Fiction templates

        # Test recommendations by project type
        story_recs = template_manager.recommend_templates("story")
        assert len(story_recs) >= 1  # Should find templates with "story" in description

    def test_export_template(self, template_manager, temp_dir):
        """Test exporting templates"""
        # Create template
        template_id = template_manager.create_project_template(
            "Export Test", "Template for export test", TemplateCategory.FICTION, {}
        )

        # Export template
        export_path = os.path.join(temp_dir, "exported_template.json")
        result = template_manager.export_template(template_id, export_path)

        assert result is True
        assert os.path.exists(export_path)

        # Verify exported content
        with open(export_path, 'r', encoding='utf-8') as f:
            exported_data = json.load(f)

        assert exported_data['metadata']['name'] == "Export Test"

        # Test exporting non-existent template
        result = template_manager.export_template("non_existent", export_path)
        assert result is False

    def test_import_template(self, template_manager, temp_dir):
        """Test importing templates"""
        # Create test template file
        template_data = {
            "metadata": {
                "id": "imported_template",
                "name": "Imported Template",
                "description": "Template imported from file",
                "category": "fiction",
                "template_type": "project",
                "version": "1.0",
                "author": "Test Author",
                "created_at": "2024-01-01T00:00:00",
                "tags": []
            },
            "structure": {"test": "structure"},
            "files": {},
            "settings": {}
        }

        import_path = os.path.join(temp_dir, "import_template.json")
        with open(import_path, 'w', encoding='utf-8') as f:
            json.dump(template_data, f)

        # Import template
        template_id = template_manager.import_template(import_path)

        assert template_id is not None
        assert template_id in template_manager.project_templates

        imported_template = template_manager.get_template(template_id)
        assert imported_template['metadata']['name'] == "Imported Template"

    def test_save_and_load_templates(self, template_manager):
        """Test saving and loading templates from disk"""
        # Create templates
        proj_id = template_manager.create_project_template(
            "Persistent Project", "Saved project template", TemplateCategory.FICTION,
            {"chapters": {"type": "directory"}}
        )
        prompt_id = template_manager.create_prompt_template(
            "Persistent Prompt", "Saved prompt template", "Template {var}", ["var"]
        )

        # Create new manager instance (simulates app restart)
        new_manager = TemplateManager(str(template_manager.templates_dir))

        # Verify templates were loaded
        assert proj_id in new_manager.project_templates
        assert prompt_id in new_manager.prompt_templates

        loaded_proj = new_manager.get_template(proj_id)
        loaded_prompt = new_manager.get_template(prompt_id)

        assert loaded_proj['metadata']['name'] == "Persistent Project"
        assert loaded_prompt['metadata']['name'] == "Persistent Prompt"

    @patch('template_manager.logger')
    def test_error_handling(self, mock_logger, temp_dir):
        """Test error handling in various scenarios"""
        manager = TemplateManager(temp_dir)

        # Test with invalid template directory
        with patch('pathlib.Path.mkdir', side_effect=OSError("Permission denied")):
            # This should not crash the initialization
            manager._load_templates()

        # Test with corrupted JSON file
        corrupted_file = Path(temp_dir) / "projects" / "corrupted.json"
        corrupted_file.parent.mkdir(exist_ok=True)
        corrupted_file.write_text("invalid json content")

        manager._load_templates()
        # Should log error but not crash
        assert mock_logger.error.called


class TestCustomTemplateCreator:
    """Test CustomTemplateCreator class"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def template_manager(self, temp_dir):
        """Create TemplateManager instance"""
        return TemplateManager(temp_dir)

    @pytest.fixture
    def creator(self, template_manager):
        """Create CustomTemplateCreator instance"""
        return CustomTemplateCreator(template_manager)

    def test_creator_initialization(self, creator, template_manager):
        """Test CustomTemplateCreator initialization"""
        assert creator.template_manager is template_manager

    def test_analyze_project_structure(self, creator, temp_dir):
        """Test project structure analysis"""
        # Create test project structure
        project_dir = os.path.join(temp_dir, "test_project")
        os.makedirs(os.path.join(project_dir, "chapters"))
        os.makedirs(os.path.join(project_dir, "characters"))

        with open(os.path.join(project_dir, "outline.txt"), 'w') as f:
            f.write("Story outline")
        with open(os.path.join(project_dir, "chapters", "chapter1.txt"), 'w') as f:
            f.write("Chapter 1 content")

        # Analyze structure
        structure = creator._analyze_project_structure(project_dir)

        assert isinstance(structure, dict)
        assert '' in structure  # Root directory
        assert 'chapters' in structure['']['directories']
        assert 'characters' in structure['']['directories']
        assert 'outline.txt' in structure['']['files']

    def test_create_from_project(self, creator, temp_dir):
        """Test creating template from existing project"""
        # Create test project
        project_dir = os.path.join(temp_dir, "test_project")
        os.makedirs(os.path.join(project_dir, "chapters"))

        with open(os.path.join(project_dir, "outline.txt"), 'w') as f:
            f.write("Story outline")

        # Create template from project
        template_id = creator.create_from_project(
            project_dir, "Project Template", "Template from test project"
        )

        assert template_id is not None
        assert template_id.startswith("proj_")

        template = creator.template_manager.get_template(template_id)
        assert template is not None
        assert template['metadata']['name'] == "Project Template"
        assert template['metadata']['description'] == "Template from test project"

    @patch('template_manager.logger')
    def test_create_from_project_error_handling(self, mock_logger, creator):
        """Test error handling when creating template from project"""
        # Test with non-existent project directory
        template_id = creator.create_from_project(
            "/non/existent/path", "Error Template"
        )

        assert template_id is None
        assert mock_logger.error.called


class TestFactoryFunctions:
    """Test factory functions and compatibility functions"""

    def test_get_template_manager(self):
        """Test get_template_manager factory function"""
        manager = get_template_manager()
        assert isinstance(manager, TemplateManager)
        assert manager.templates_dir.name == "templates"

    def test_get_template_manager_with_custom_dir(self):
        """Test get_template_manager with custom directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = get_template_manager(temp_dir)
            assert isinstance(manager, TemplateManager)
            assert str(manager.templates_dir) == temp_dir

    def test_get_custom_template_creator(self):
        """Test get_custom_template_creator factory function"""
        creator = get_custom_template_creator()
        assert isinstance(creator, CustomTemplateCreator)
        assert isinstance(creator.template_manager, TemplateManager)

    def test_get_custom_template_creator_with_manager(self):
        """Test get_custom_template_creator with existing manager"""
        manager = get_template_manager()
        creator = get_custom_template_creator(manager)
        assert isinstance(creator, CustomTemplateCreator)
        assert creator.template_manager is manager


class TestIntegrationScenarios:
    """Test realistic integration scenarios"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_complete_template_workflow(self, temp_dir):
        """Test complete template creation and usage workflow"""
        # Initialize manager
        manager = TemplateManager(temp_dir)

        # Create project template
        structure = {
            "chapters": {"type": "directory"},
            "characters": {"type": "directory"},
            "research": {"type": "directory"},
            "outline.txt": {"type": "file", "content": "Story outline template"},
            "characters.json": {"type": "file", "content": "{}"}
        }

        proj_id = manager.create_project_template(
            name="Novel Template",
            description="Complete novel writing template",
            category=TemplateCategory.FICTION,
            structure=structure
        )

        # Create related prompt templates
        char_prompt_id = manager.create_prompt_template(
            name="Character Development",
            description="Prompt for developing character profiles",
            template_text="Create a detailed character profile for {character_name}, a {character_role} in a {genre} story set in {setting}.",
            variables=["character_name", "character_role", "genre", "setting"]
        )

        plot_prompt_id = manager.create_prompt_template(
            name="Plot Development",
            description="Prompt for plot development",
            template_text="Develop a compelling plot for chapter {chapter_number} where {main_event} happens to {character}.",
            variables=["chapter_number", "main_event", "character"]
        )

        # Test template discovery and recommendations
        templates = manager.list_templates()
        assert len(templates) == 3

        fiction_templates = manager.list_templates(category=TemplateCategory.FICTION)
        assert len(fiction_templates) == 1

        prompt_templates = manager.list_templates(template_type=TemplateType.PROMPT)
        assert len(prompt_templates) == 2

        # Test recommendations
        recommendations = manager.recommend_templates("novel", "fiction")
        assert proj_id in recommendations

        # Test export/import cycle
        export_path = os.path.join(temp_dir, "exported_novel_template.json")
        assert manager.export_template(proj_id, export_path)

        # Delete original and import
        assert manager.delete_template(proj_id)
        imported_id = manager.import_template(export_path)
        assert imported_id is not None

        imported_template = manager.get_template(imported_id)
        assert imported_template['metadata']['name'] == "Novel Template"
        assert imported_template['structure'] == structure

    def test_custom_template_creation_workflow(self, temp_dir):
        """Test creating custom templates from existing projects"""
        # Create sample project structure
        project_dir = os.path.join(temp_dir, "sample_novel")
        os.makedirs(os.path.join(project_dir, "chapters"))
        os.makedirs(os.path.join(project_dir, "characters"))
        os.makedirs(os.path.join(project_dir, "world_building"))

        # Create sample files
        files_to_create = [
            ("outline.txt", "Main story outline"),
            ("characters/protagonist.txt", "Main character profile"),
            ("characters/antagonist.txt", "Villain profile"),
            ("world_building/setting.txt", "World description"),
            ("chapters/chapter_01.txt", "First chapter content")
        ]

        for file_path, content in files_to_create:
            full_path = os.path.join(project_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

        # Create template manager and custom creator
        manager = TemplateManager(temp_dir)
        creator = CustomTemplateCreator(manager)

        # Create template from project
        template_id = creator.create_from_project(
            project_dir,
            "Sample Novel Template",
            "Template created from completed sample novel project"
        )

        assert template_id is not None

        # Verify template structure
        template = manager.get_template(template_id)
        assert template is not None
        assert template['metadata']['name'] == "Sample Novel Template"
        assert template['metadata']['category'] == TemplateCategory.CUSTOM.value

        # Verify structure includes all directories and files
        structure = template['structure']
        assert 'chapters' in structure['']['directories']
        assert 'characters' in structure['']['directories']
        assert 'world_building' in structure['']['directories']
        assert 'outline.txt' in structure['']['files']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
