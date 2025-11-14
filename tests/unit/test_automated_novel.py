"""
Unit tests for Automated Novel Writing System
Tests the GUI and workflow components without requiring a display
"""

import pytest
import os
import sys
import tempfile
import shutil
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAutomatedNovelWorkflow:
    """Test the automated novel workflow backend"""
    
    def test_workflow_import(self):
        """Test that workflow module imports correctly"""
        from src.workflow.automated_novel_workflow import AutomatedNovelWorkflowThread
        assert AutomatedNovelWorkflowThread is not None
    
    def test_workflow_initialization(self):
        """Test workflow thread initialization"""
        from src.workflow.automated_novel_workflow import AutomatedNovelWorkflowThread
        
        with tempfile.TemporaryDirectory() as tmpdir:
            workflow = AutomatedNovelWorkflowThread(
                project_dir=tmpdir,
                idea="Test novel idea",
                tone="dark and tense",
                target_words=250000
            )
            
            assert workflow.project_dir == tmpdir
            assert workflow.idea == "Test novel idea"
            assert workflow.tone == "dark and tense"
            assert workflow.target_words == 250000
            assert workflow.current_step == "initialization"
            assert workflow.total_chapters == 25
    
    def test_file_operations(self):
        """Test workflow file creation and management"""
        from src.workflow.automated_novel_workflow import AutomatedNovelWorkflowThread
        
        with tempfile.TemporaryDirectory() as tmpdir:
            workflow = AutomatedNovelWorkflowThread(
                project_dir=tmpdir,
                idea="Test",
                tone="test",
                target_words=100000
            )
            
            # Test save_to_file
            test_content = "Test content"
            workflow.save_to_file("test.txt", test_content)
            
            test_file = os.path.join(tmpdir, "test.txt")
            assert os.path.exists(test_file)
            
            with open(test_file, 'r') as f:
                assert f.read() == test_content
            
            # Test append_to_story
            workflow.append_to_story("Story content")
            story_file = os.path.join(tmpdir, "story.txt")
            assert os.path.exists(story_file)
            
            with open(story_file, 'r') as f:
                assert "Story content" in f.read()
    
    def test_config_update(self):
        """Test config file updates"""
        from src.workflow.automated_novel_workflow import AutomatedNovelWorkflowThread
        
        with tempfile.TemporaryDirectory() as tmpdir:
            workflow = AutomatedNovelWorkflowThread(
                project_dir=tmpdir,
                idea="Test",
                tone="test",
                target_words=100000
            )
            
            # Update config
            workflow.update_config("TestKey", "TestValue")
            
            config_file = os.path.join(tmpdir, "config.txt")
            assert os.path.exists(config_file)
            
            with open(config_file, 'r') as f:
                content = f.read()
                assert "TestKey: TestValue" in content
            
            # Update existing key
            workflow.update_config("TestKey", "NewValue")
            
            with open(config_file, 'r') as f:
                content = f.read()
                assert "TestKey: NewValue" in content
                # Should not have duplicate keys
                assert content.count("TestKey:") == 1


class TestAutomatedNovelGUI:
    """Test the automated novel GUI (without display)"""
    
    def test_gui_import(self):
        """Test that GUI module imports correctly"""
        from src.ui.automated_novel_gui import AutomatedNovelGUI
        assert AutomatedNovelGUI is not None
    
    def test_factory_function(self):
        """Test factory function"""
        from src.ui.automated_novel_gui import create_automated_novel_gui
        assert create_automated_novel_gui is not None
    
    def test_log_highlighter(self):
        """Test log syntax highlighter"""
        from src.ui.automated_novel_gui import LogHighlighter
        assert LogHighlighter is not None
        
        highlighter = LogHighlighter()
        assert highlighter is not None
        assert hasattr(highlighter, 'highlightBlock')


class TestIntegration:
    """Integration tests for the automated novel system"""
    
    @pytest.mark.requires_pyqt
    @pytest.mark.skipif(
        os.environ.get('DISPLAY') is None,
        reason="Requires display for GUI creation"
    )
    def test_project_structure(self):
        """Test that project structure is created correctly"""
        from src.ui.automated_novel_gui import AutomatedNovelGUI
        from PyQt5.QtWidgets import QApplication
        import sys
        
        # Create application (required for Qt widgets)
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        gui = AutomatedNovelGUI()
        
        # Test project initialization
        with tempfile.TemporaryDirectory() as tmpdir:
            gui.current_project_dir = tmpdir
            gui.initialize_project_files(
                idea="Test idea",
                tone="test tone",
                target=100000
            )
            
            # Check that all files are created
            expected_files = [
                "story.txt",
                "log.txt",
                "config.txt",
                "context.txt",
                "characters.txt",
                "world.txt",
                "summaries.txt",
                "weights.txt",
                "buffer_backup.txt",
                "story_backup.txt",
                "log_backup.txt"
            ]
            
            for filename in expected_files:
                filepath = os.path.join(tmpdir, filename)
                assert os.path.exists(filepath), f"File {filename} was not created"
            
            # Check drafts directory
            drafts_dir = os.path.join(tmpdir, "drafts")
            assert os.path.exists(drafts_dir)
            assert os.path.isdir(drafts_dir)
            
            # Verify config content
            config_file = os.path.join(tmpdir, "config.txt")
            with open(config_file, 'r') as f:
                content = f.read()
                assert "Idea: Test idea" in content
                assert "Tone: test tone" in content
                assert "SoftTarget: 100000" in content


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
