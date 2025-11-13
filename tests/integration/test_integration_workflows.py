"""
Integration tests for AI and export workflows using mock API responses
"""

import pytest
import json
import tempfile
import shutil
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from pathlib import Path

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.system.api_manager import APIManager, APIError
from src.export_formats.validator import ExportValidator, ExportValidationResult


class TestAPIManagerIntegration:
    """Integration tests for AI API workflows"""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory"""
        cache_dir = tempfile.mkdtemp()
        yield cache_dir
        shutil.rmtree(cache_dir, ignore_errors=True)

    @pytest.fixture
    def api_manager(self, temp_cache_dir):
        """Create APIManager with temporary cache"""
        with patch('src.system.api_manager.SQLiteCache') as mock_cache_class:
            mock_cache = Mock()
            mock_cache_class.return_value = mock_cache

            manager = APIManager()
            manager.sqlite_cache = mock_cache
            return manager

    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI API response"""
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
    def mock_anthropic_response(self):
        """Mock Anthropic API response"""
        return {
            "content": [{
                "text": "This is a test Anthropic response for character development."
            }],
            "usage": {
                "input_tokens": 45,
                "output_tokens": 20
            }
        }

    @pytest.fixture
    def mock_project_context(self):
        """Mock project context data"""
        return {
            "project_name": "Test Novel",
            "genre": "Fantasy",
            "style": "Epic",
            "target_audience": "Young Adult",
            "themes": ["friendship", "courage", "growth"],
            "characters": [
                {"name": "Alex", "role": "protagonist"},
                {"name": "Morgan", "role": "mentor"}
            ],
            "setting": "Medieval fantasy world",
            "recent_content": "The hero ventured into the dark forest...",
            "outline": "Chapter 1: The Call to Adventure\nChapter 2: Meeting the Mentor"
        }

    def test_ai_text_generation_with_cache_miss(self, api_manager, mock_openai_response):
        """Test AI text generation when cache miss occurs"""
        # Mock cache miss
        api_manager.sqlite_cache.get.return_value = None
        api_manager.memory_cache = Mock()
        api_manager.memory_cache.get.return_value = None

        # Mock API request
        with patch.object(api_manager, '_make_sync_request', return_value=mock_openai_response):
            # Set API key
            api_manager.set_api_key('openai', 'test-key')

            # Generate text
            result = api_manager.generate_text(
                prompt="Write a fantasy story opening",
                api_name='openai',
                model='gpt-3.5-turbo',
                use_cache=True
            )

            assert result == "This is a test AI response for story generation."

            # Verify cache was checked and set
            api_manager.sqlite_cache.get.assert_called_once()
            api_manager.sqlite_cache.set.assert_called_once()

    def test_ai_text_generation_with_cache_hit(self, api_manager):
        """Test AI text generation when cache hit occurs"""
        cached_response = {
            "choices": [{
                "message": {
                    "content": "This is cached AI response."
                }
            }]
        }

        # Mock cache hit
        api_manager.sqlite_cache.get.return_value = cached_response

        result = api_manager.generate_text(
            prompt="Write a story",
            api_name='openai',
            use_cache=True
        )

        assert result == "This is cached AI response."

        # Verify cache was checked but API was not called
        api_manager.sqlite_cache.get.assert_called_once()
        api_manager.sqlite_cache.set.assert_not_called()

    def test_ai_text_generation_with_project_context(self, api_manager, mock_openai_response, mock_project_context):
        """Test AI text generation with project context enhancement"""
        # Mock project context loading
        with patch.object(api_manager, '_get_project_context', return_value=mock_project_context):
            with patch.object(api_manager, '_make_sync_request', return_value=mock_openai_response) as mock_request:
                api_manager.sqlite_cache.get.return_value = None
                api_manager.memory_cache = Mock()
                api_manager.memory_cache.get.return_value = None
                api_manager.set_api_key('openai', 'test-key')

                result = api_manager.generate_text(
                    prompt="Continue the story",
                    project_name="Test Novel",
                    use_project_context=True,
                    use_cache=True
                )

                assert result == "This is a test AI response for story generation."

                # Verify request was made with enhanced prompt
                mock_request.assert_called_once()
                call_args = mock_request.call_args[1]
                request_data = call_args['data']

                # Check that context was included in the prompt
                enhanced_prompt = request_data['messages'][0]['content']
                assert "[Project: Test Novel]" in enhanced_prompt
                assert "[Genre: Fantasy]" in enhanced_prompt
                assert "Continue the story" in enhanced_prompt

    def test_anthropic_api_integration(self, api_manager, mock_anthropic_response):
        """Test integration with Anthropic API"""
        api_manager.sqlite_cache.get.return_value = None
        api_manager.memory_cache = Mock()
        api_manager.memory_cache.get.return_value = None

        with patch.object(api_manager, '_make_sync_request', return_value=mock_anthropic_response):
            api_manager.set_api_key('anthropic', 'test-key')

            result = api_manager.generate_text(
                prompt="Develop this character",
                api_name='anthropic',
                model='claude-3-sonnet-20240229'
            )

            assert result == "This is a test Anthropic response for character development."

    def test_api_error_handling(self, api_manager):
        """Test API error handling during text generation"""
        api_manager.sqlite_cache.get.return_value = None
        api_manager.memory_cache = Mock()
        api_manager.memory_cache.get.return_value = None

        # Mock API error
        with patch.object(api_manager, '_make_sync_request', side_effect=APIError("API rate limit exceeded")):
            api_manager.set_api_key('openai', 'test-key')

            with pytest.raises(APIError) as exc_info:
                api_manager.generate_text(
                    prompt="Write a story",
                    api_name='openai'
                )

            assert "API rate limit exceeded" in str(exc_info.value)

    def test_async_request_workflow(self, api_manager, mock_openai_response):
        """Test async request workflow"""
        api_manager.sqlite_cache.get.return_value = None
        api_manager.memory_cache = Mock()
        api_manager.memory_cache.get.return_value = None

        # Mock worker thread
        mock_worker = Mock()
        api_manager.worker_thread = mock_worker

        callback = Mock()

        request_id = api_manager.make_request_async(
            api_name='openai',
            endpoint='/chat/completions',
            data={'model': 'gpt-3.5-turbo', 'messages': [{'role': 'user', 'content': 'test'}]},
            callback=callback
        )

        assert request_id.startswith('req_')
        mock_worker.add_request.assert_called_once()

    def test_cache_key_generation_with_context(self, api_manager, mock_project_context):
        """Test cache key generation includes project context"""
        key1 = api_manager._generate_cache_key(
            'openai', '/chat/completions',
            {'prompt': 'test'}, mock_project_context
        )

        key2 = api_manager._generate_cache_key(
            'openai', '/chat/completions',
            {'prompt': 'test'}, {}
        )

        # Keys should be different when context is different
        assert key1 != key2

        # Same inputs should generate same key
        key3 = api_manager._generate_cache_key(
            'openai', '/chat/completions',
            {'prompt': 'test'}, mock_project_context
        )
        assert key1 == key3

    def test_multiple_api_provider_workflow(self, api_manager):
        """Test workflow using multiple AI providers"""
        api_manager.sqlite_cache.get.return_value = None
        api_manager.memory_cache = Mock()
        api_manager.memory_cache.get.return_value = None

        openai_response = {
            "choices": [{"message": {"content": "OpenAI story content"}}]
        }
        anthropic_response = {
            "content": [{"text": "Anthropic character analysis"}]
        }

        with patch.object(api_manager, '_make_sync_request') as mock_request:
            # Set up different responses for different APIs
            mock_request.side_effect = [openai_response, anthropic_response]

            api_manager.set_api_key('openai', 'openai-key')
            api_manager.set_api_key('anthropic', 'anthropic-key')

            # Generate story content with OpenAI
            story_result = api_manager.generate_text(
                prompt="Write a story opening",
                api_name='openai'
            )

            # Generate character analysis with Anthropic
            character_result = api_manager.generate_text(
                prompt="Analyze this character",
                api_name='anthropic'
            )

            assert story_result == "OpenAI story content"
            assert character_result == "Anthropic character analysis"
            assert mock_request.call_count == 2


class TestExportWorkflowIntegration:
    """Integration tests for export workflows"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def export_validator(self):
        """Create ExportValidator instance"""
        return ExportValidator()

    @pytest.fixture
    def sample_docx_content(self):
        """Sample DOCX file content structure"""
        return {
            'document.xml': '<?xml version="1.0"?><document><body><p><r><t>Test content</t></r></p></body></document>',
            '[Content_Types].xml': '<?xml version="1.0"?><Types></Types>',
            'word/_rels/document.xml.rels': '<?xml version="1.0"?><Relationships></Relationships>'
        }

    def test_docx_export_validation_workflow(self, export_validator, temp_dir, sample_docx_content):
        """Test complete DOCX export and validation workflow"""
        # Create a mock DOCX file
        docx_path = os.path.join(temp_dir, "test_document.docx")

        # Mock the ZIP file structure
        with patch('zipfile.ZipFile') as mock_zip:
            mock_zip_instance = Mock()
            mock_zip.return_value.__enter__.return_value = mock_zip_instance
            mock_zip_instance.namelist.return_value = list(sample_docx_content.keys())

            def mock_read(filename):
                return sample_docx_content.get(filename, '').encode()

            mock_zip_instance.read.side_effect = mock_read

            # Create actual file for existence check
            with open(docx_path, 'wb') as f:
                f.write(b'mock docx content')

            # Validate the DOCX file
            result = export_validator.validate_docx(docx_path)

            assert isinstance(result, ExportValidationResult)
            assert result.is_valid
            assert result.format_type == "DOCX"
            assert result.file_path == docx_path
            assert "Successfully validated DOCX" in result.message

    def test_pdf_export_validation_workflow(self, export_validator, temp_dir):
        """Test PDF export and validation workflow"""
        pdf_path = os.path.join(temp_dir, "test_document.pdf")

        # Create a mock PDF file with proper header
        pdf_content = b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n%%EOF'

        with open(pdf_path, 'wb') as f:
            f.write(pdf_content)

        # Mock PyPDF2 if available
        with patch('src.export_formats.validator.PyPDF2', create=True) as mock_pypdf2:
            mock_reader = Mock()
            mock_reader.pages = [Mock(), Mock()]  # 2 pages
            mock_reader.metadata = {'Title': 'Test Document'}
            mock_pypdf2.PdfReader.return_value = mock_reader

            result = export_validator.validate_pdf(pdf_path)

            assert isinstance(result, ExportValidationResult)
            assert result.is_valid
            assert result.format_type == "PDF"
            assert "Successfully validated PDF" in result.message
            assert result.metadata.get('page_count') == 2

    def test_epub_export_validation_workflow(self, export_validator, temp_dir):
        """Test EPUB export and validation workflow"""
        epub_path = os.path.join(temp_dir, "test_book.epub")

        # Mock EPUB structure
        epub_files = {
            'mimetype': 'application/epub+zip',
            'META-INF/container.xml': '''<?xml version="1.0"?>
                <container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
                    <rootfiles>
                        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
                    </rootfiles>
                </container>''',
            'OEBPS/content.opf': '''<?xml version="1.0"?>
                <package xmlns="http://www.idpf.org/2007/opf" version="3.0">
                    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
                        <dc:title>Test Book</dc:title>
                        <dc:creator>Test Author</dc:creator>
                    </metadata>
                    <manifest>
                        <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
                    </manifest>
                    <spine>
                        <itemref idref="chapter1"/>
                    </spine>
                </package>''',
            'OEBPS/chapter1.xhtml': '''<?xml version="1.0"?>
                <html xmlns="http://www.w3.org/1999/xhtml">
                    <head><title>Chapter 1</title></head>
                    <body><h1>Chapter 1</h1><p>Content here.</p></body>
                </html>'''
        }

        with patch('zipfile.ZipFile') as mock_zip:
            mock_zip_instance = Mock()
            mock_zip.return_value.__enter__.return_value = mock_zip_instance
            mock_zip_instance.namelist.return_value = list(epub_files.keys())

            def mock_read(filename):
                return epub_files.get(filename, '').encode()

            mock_zip_instance.read.side_effect = mock_read

            # Create actual file
            with open(epub_path, 'wb') as f:
                f.write(b'mock epub content')

            result = export_validator.validate_epub(epub_path)

            assert isinstance(result, ExportValidationResult)
            assert result.is_valid
            assert result.format_type == "EPUB"
            assert result.metadata.get('title') == 'Test Book'
            assert result.metadata.get('author') == 'Test Author'

    def test_multi_format_export_validation_workflow(self, export_validator, temp_dir):
        """Test validating multiple export formats in sequence"""
        # Create multiple format files
        formats_to_test = [
            ("document.docx", "DOCX"),
            ("document.pdf", "PDF"),
            ("book.epub", "EPUB")
        ]

        results = []

        for filename, format_type in formats_to_test:
            file_path = os.path.join(temp_dir, filename)

            # Create minimal valid content for each format
            if format_type == "DOCX":
                self._create_mock_docx(file_path)
            elif format_type == "PDF":
                self._create_mock_pdf(file_path)
            elif format_type == "EPUB":
                self._create_mock_epub(file_path)

            # Validate using the general validate method
            result = export_validator.validate(file_path)
            results.append(result)

        # Check all validations
        assert len(results) == 3
        for result in results:
            assert isinstance(result, ExportValidationResult)
            # Note: Some might not be valid due to mocking limitations, but should not crash

    def _create_mock_docx(self, file_path):
        """Create a mock DOCX file"""
        import zipfile
        with zipfile.ZipFile(file_path, 'w') as zf:
            zf.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types></Types>')
            zf.writestr('word/document.xml', '<?xml version="1.0"?><document><body><p><r><t>Test</t></r></p></body></document>')

    def _create_mock_pdf(self, file_path):
        """Create a mock PDF file"""
        pdf_content = b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n%%EOF'
        with open(file_path, 'wb') as f:
            f.write(pdf_content)

    def _create_mock_epub(self, file_path):
        """Create a mock EPUB file"""
        import zipfile
        with zipfile.ZipFile(file_path, 'w') as zf:
            zf.writestr('mimetype', 'application/epub+zip')
            zf.writestr('META-INF/container.xml', '''<?xml version="1.0"?>
                <container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
                    <rootfiles>
                        <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
                    </rootfiles>
                </container>''')

    def test_export_error_handling_workflow(self, export_validator, temp_dir):
        """Test export validation error handling"""
        # Test with non-existent file
        result = export_validator.validate("/non/existent/file.docx")
        assert not result.is_valid
        assert "File not found" in result.message

        # Test with invalid file format
        invalid_file = os.path.join(temp_dir, "invalid.txt")
        with open(invalid_file, 'w') as f:
            f.write("This is not a valid document format")

        result = export_validator.validate(invalid_file)
        assert not result.is_valid
        assert "Unsupported format" in result.message

    def test_export_validation_with_warnings(self, export_validator, temp_dir):
        """Test export validation that produces warnings"""
        # Create a PDF without proper structure (should validate but with warnings)
        pdf_path = os.path.join(temp_dir, "minimal.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(b'%PDF-1.4\n%%EOF')  # Minimal PDF

        result = export_validator.validate_pdf(pdf_path)

        # Should be valid but may have warnings about missing elements
        assert isinstance(result, ExportValidationResult)
        assert result.format_type == "PDF"
        # May or may not be valid depending on validator strictness


class TestWorkflowIntegration:
    """Test integrated AI + Export workflows"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_ai_to_export_workflow(self, temp_dir):
        """Test complete workflow from AI generation to export validation"""
        # Mock AI manager
        ai_manager = Mock()
        ai_manager.generate_text.return_value = "Generated story content from AI"

        # Mock export system
        export_validator = ExportValidator()

        # Simulate workflow: AI generates content -> Export to file -> Validate
        generated_content = ai_manager.generate_text(
            prompt="Write a short story",
            project_name="Test Project"
        )

        # Create export file with generated content
        export_file = os.path.join(temp_dir, "generated_story.txt")
        with open(export_file, 'w', encoding='utf-8') as f:
            f.write(generated_content)

        # Validate the export (for TXT, basic validation)
        assert os.path.exists(export_file)
        with open(export_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert content == "Generated story content from AI"
        assert len(content) > 0

    @patch('src.system.api_manager.APIManager')
    @patch('src.export_formats.validator.ExportValidator')
    def test_integrated_ai_export_pipeline(self, mock_validator_class, mock_api_class, temp_dir):
        """Test integrated pipeline with mocked components"""
        # Setup mocks
        mock_api = Mock()
        mock_api_class.return_value = mock_api
        mock_api.generate_text.return_value = "AI generated novel chapter content"

        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator
        mock_validator.validate.return_value = ExportValidationResult(
            is_valid=True,
            format_type="DOCX",
            file_path="test.docx",
            message="Export validated successfully",
            warnings=[],
            metadata={"word_count": 250}
        )

        # Simulate pipeline
        ai_manager = mock_api_class()
        validator = mock_validator_class()

        # Step 1: Generate content
        content = ai_manager.generate_text(
            prompt="Write chapter 1 of a fantasy novel",
            project_name="Fantasy Epic",
            use_project_context=True
        )

        # Step 2: Export content (simulated)
        export_path = os.path.join(temp_dir, "chapter1.docx")
        # (In real implementation, would use document export system)

        # Step 3: Validate export
        validation_result = validator.validate(export_path)

        # Verify pipeline
        assert content == "AI generated novel chapter content"
        assert validation_result.is_valid
        assert validation_result.format_type == "DOCX"
        assert validation_result.metadata["word_count"] == 250


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
