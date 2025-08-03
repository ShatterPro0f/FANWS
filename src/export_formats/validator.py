"""
Export format validation and integrity checking for FANWS.

Provides validation for DOCX, EPUB, and PDF files to ensure
they are properly formatted and readable.
"""

import os
import zipfile
import logging
import mimetypes
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

class ExportValidationResult:
    """Result of export validation."""

    def __init__(self, is_valid: bool, format_type: str, file_path: str,
                 message: str = "", warnings: List[str] = None,
                 metadata: Dict[str, Any] = None):
        self.is_valid = is_valid
        self.format_type = format_type
        self.file_path = file_path
        self.message = message
        self.warnings = warnings or []
        self.metadata = metadata or {}

    def __bool__(self):
        return self.is_valid

class DOCXValidator:
    """Validator for DOCX files."""

    @staticmethod
    def validate(file_path: str) -> ExportValidationResult:
        """Validate a DOCX file."""
        try:
            if not os.path.exists(file_path):
                return ExportValidationResult(
                    False, "DOCX", file_path,
                    "File does not exist"
                )

            # Check file extension
            if not file_path.lower().endswith('.docx'):
                return ExportValidationResult(
                    False, "DOCX", file_path,
                    "File does not have .docx extension"
                )

            warnings = []
            metadata = {}

            # Try to open as zip file (DOCX is essentially a ZIP)
            try:
                with zipfile.ZipFile(file_path, 'r') as docx_zip:
                    # Check for required DOCX structure
                    required_files = [
                        '[Content_Types].xml',
                        '_rels/.rels',
                        'word/document.xml'
                    ]

                    zip_contents = docx_zip.namelist()
                    metadata['file_count'] = len(zip_contents)

                    missing_files = []
                    for required_file in required_files:
                        if required_file not in zip_contents:
                            missing_files.append(required_file)

                    if missing_files:
                        return ExportValidationResult(
                            False, "DOCX", file_path,
                            f"Missing required files: {', '.join(missing_files)}"
                        )

                    # Validate document.xml structure
                    try:
                        document_xml = docx_zip.read('word/document.xml')
                        root = ET.fromstring(document_xml)

                        # Check for basic document structure
                        body = root.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}body')
                        if body is None:
                            warnings.append("Document body not found or malformed")
                        else:
                            # Count paragraphs
                            paragraphs = body.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p')
                            metadata['paragraph_count'] = len(paragraphs)

                            # Check for text content
                            text_elements = body.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')
                            total_text = ''.join(elem.text or '' for elem in text_elements)
                            metadata['character_count'] = len(total_text)
                            metadata['word_count'] = len(total_text.split())

                            if len(total_text.strip()) == 0:
                                warnings.append("Document appears to be empty")

                    except ET.ParseError as e:
                        return ExportValidationResult(
                            False, "DOCX", file_path,
                            f"Invalid XML structure in document.xml: {e}"
                        )

                    # Check core properties if available
                    if 'docProps/core.xml' in zip_contents:
                        try:
                            core_xml = docx_zip.read('docProps/core.xml')
                            core_root = ET.fromstring(core_xml)

                            # Extract metadata
                            title_elem = core_root.find('.//{http://purl.org/dc/elements/1.1/}title')
                            if title_elem is not None and title_elem.text:
                                metadata['title'] = title_elem.text

                            creator_elem = core_root.find('.//{http://purl.org/dc/elements/1.1/}creator')
                            if creator_elem is not None and creator_elem.text:
                                metadata['creator'] = creator_elem.text

                        except ET.ParseError:
                            warnings.append("Could not parse document properties")

            except zipfile.BadZipFile:
                return ExportValidationResult(
                    False, "DOCX", file_path,
                    "File is not a valid ZIP archive"
                )

            # Check file size
            file_size = os.path.getsize(file_path)
            metadata['file_size'] = file_size

            if file_size == 0:
                return ExportValidationResult(
                    False, "DOCX", file_path,
                    "File is empty"
                )

            if file_size < 1000:  # Less than 1KB
                warnings.append("File size is very small, may be corrupted")

            # Try to validate with python-docx if available
            try:
                from docx import Document
                doc = Document(file_path)

                # Additional validation using python-docx
                if len(doc.paragraphs) == 0:
                    warnings.append("No paragraphs found in document")

                metadata['docx_paragraphs'] = len(doc.paragraphs)

            except ImportError:
                warnings.append("python-docx not available for advanced validation")
            except Exception as e:
                warnings.append(f"python-docx validation failed: {e}")

            return ExportValidationResult(
                True, "DOCX", file_path,
                "DOCX file is valid",
                warnings, metadata
            )

        except Exception as e:
            logger.error(f"Error validating DOCX file {file_path}: {e}")
            return ExportValidationResult(
                False, "DOCX", file_path,
                f"Validation error: {e}"
            )

class EPUBValidator:
    """Validator for EPUB files."""

    @staticmethod
    def validate(file_path: str) -> ExportValidationResult:
        """Validate an EPUB file."""
        try:
            if not os.path.exists(file_path):
                return ExportValidationResult(
                    False, "EPUB", file_path,
                    "File does not exist"
                )

            # Check file extension
            if not file_path.lower().endswith('.epub'):
                return ExportValidationResult(
                    False, "EPUB", file_path,
                    "File does not have .epub extension"
                )

            warnings = []
            metadata = {}

            # EPUB is a ZIP file
            try:
                with zipfile.ZipFile(file_path, 'r') as epub_zip:
                    zip_contents = epub_zip.namelist()
                    metadata['file_count'] = len(zip_contents)

                    # Check for required EPUB structure
                    required_files = ['mimetype', 'META-INF/container.xml']
                    missing_files = []

                    for required_file in required_files:
                        if required_file not in zip_contents:
                            missing_files.append(required_file)

                    if missing_files:
                        return ExportValidationResult(
                            False, "EPUB", file_path,
                            f"Missing required EPUB files: {', '.join(missing_files)}"
                        )

                    # Validate mimetype
                    try:
                        mimetype_content = epub_zip.read('mimetype').decode('utf-8').strip()
                        if mimetype_content != 'application/epub+zip':
                            warnings.append(f"Unexpected mimetype: {mimetype_content}")
                    except Exception as e:
                        warnings.append(f"Could not read mimetype: {e}")

                    # Validate container.xml
                    try:
                        container_xml = epub_zip.read('META-INF/container.xml')
                        container_root = ET.fromstring(container_xml)

                        # Find the OPF file
                        rootfiles = container_root.findall('.//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile')
                        if not rootfiles:
                            warnings.append("No rootfile found in container.xml")
                        else:
                            opf_path = rootfiles[0].get('full-path')
                            if opf_path and opf_path in zip_contents:
                                metadata['opf_file'] = opf_path

                                # Validate OPF file
                                try:
                                    opf_xml = epub_zip.read(opf_path)
                                    opf_root = ET.fromstring(opf_xml)

                                    # Check for required OPF elements
                                    metadata_elem = opf_root.find('.//{http://www.idpf.org/2007/opf}metadata')
                                    if metadata_elem is not None:
                                        title_elem = metadata_elem.find('.//{http://purl.org/dc/elements/1.1/}title')
                                        if title_elem is not None and title_elem.text:
                                            metadata['title'] = title_elem.text

                                        creator_elem = metadata_elem.find('.//{http://purl.org/dc/elements/1.1/}creator')
                                        if creator_elem is not None and creator_elem.text:
                                            metadata['creator'] = creator_elem.text

                                    # Check manifest
                                    manifest = opf_root.find('.//{http://www.idpf.org/2007/opf}manifest')
                                    if manifest is not None:
                                        items = manifest.findall('.//{http://www.idpf.org/2007/opf}item')
                                        metadata['manifest_items'] = len(items)

                                        # Check if referenced files exist
                                        missing_manifest_files = []
                                        for item in items:
                                            href = item.get('href')
                                            if href:
                                                # Resolve relative path from OPF location
                                                opf_dir = os.path.dirname(opf_path)
                                                full_href = os.path.join(opf_dir, href).replace('\\', '/')
                                                if full_href not in zip_contents:
                                                    missing_manifest_files.append(href)

                                        if missing_manifest_files:
                                            warnings.append(f"Missing manifest files: {', '.join(missing_manifest_files[:5])}")

                                except ET.ParseError as e:
                                    warnings.append(f"Invalid OPF XML: {e}")
                            else:
                                warnings.append(f"OPF file not found: {opf_path}")

                    except ET.ParseError as e:
                        warnings.append(f"Invalid container.xml: {e}")

            except zipfile.BadZipFile:
                return ExportValidationResult(
                    False, "EPUB", file_path,
                    "File is not a valid ZIP archive"
                )

            # Check file size
            file_size = os.path.getsize(file_path)
            metadata['file_size'] = file_size

            if file_size == 0:
                return ExportValidationResult(
                    False, "EPUB", file_path,
                    "File is empty"
                )

            return ExportValidationResult(
                True, "EPUB", file_path,
                "EPUB file is valid",
                warnings, metadata
            )

        except Exception as e:
            logger.error(f"Error validating EPUB file {file_path}: {e}")
            return ExportValidationResult(
                False, "EPUB", file_path,
                f"Validation error: {e}"
            )

class PDFValidator:
    """Validator for PDF files."""

    @staticmethod
    def validate(file_path: str) -> ExportValidationResult:
        """Validate a PDF file."""
        try:
            if not os.path.exists(file_path):
                return ExportValidationResult(
                    False, "PDF", file_path,
                    "File does not exist"
                )

            # Check file extension
            if not file_path.lower().endswith('.pdf'):
                return ExportValidationResult(
                    False, "PDF", file_path,
                    "File does not have .pdf extension"
                )

            warnings = []
            metadata = {}

            # Check file size
            file_size = os.path.getsize(file_path)
            metadata['file_size'] = file_size

            if file_size == 0:
                return ExportValidationResult(
                    False, "PDF", file_path,
                    "File is empty"
                )

            # Basic PDF validation - check PDF header
            try:
                with open(file_path, 'rb') as pdf_file:
                    header = pdf_file.read(8)

                    if not header.startswith(b'%PDF-'):
                        return ExportValidationResult(
                            False, "PDF", file_path,
                            "File does not have a valid PDF header"
                        )

                    # Extract PDF version
                    try:
                        version_part = header[5:8].decode('ascii')
                        metadata['pdf_version'] = version_part
                    except:
                        warnings.append("Could not determine PDF version")

                    # Read a bit more to check for basic structure
                    pdf_file.seek(0)
                    content = pdf_file.read(1024)

                    if b'%%EOF' not in content:
                        # Check end of file for %%EOF
                        pdf_file.seek(-512, 2)  # Read last 512 bytes
                        end_content = pdf_file.read()
                        if b'%%EOF' not in end_content:
                            warnings.append("PDF may be truncated (no %%EOF found)")

                    # Look for basic PDF objects
                    pdf_file.seek(0)
                    full_content = pdf_file.read()

                    if b'/Type /Catalog' not in full_content:
                        warnings.append("No document catalog found")

                    if b'/Type /Page' not in full_content:
                        warnings.append("No pages found in document")

                    # Count approximate number of pages (very rough)
                    page_count = full_content.count(b'/Type /Page')
                    if page_count > 0:
                        metadata['estimated_pages'] = page_count
                    else:
                        warnings.append("Could not estimate page count")

            except Exception as e:
                warnings.append(f"Could not read PDF file: {e}")

            # Try advanced validation with PyPDF2 if available
            try:
                import PyPDF2

                with open(file_path, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)

                    metadata['page_count'] = len(pdf_reader.pages)

                    if len(pdf_reader.pages) == 0:
                        warnings.append("PDF contains no pages")

                    # Check for encryption
                    if pdf_reader.is_encrypted:
                        metadata['encrypted'] = True
                        warnings.append("PDF is encrypted")

                    # Try to extract text from first page
                    if len(pdf_reader.pages) > 0:
                        try:
                            first_page = pdf_reader.pages[0]
                            text = first_page.extract_text()
                            metadata['has_text'] = len(text.strip()) > 0
                            if not metadata['has_text']:
                                warnings.append("First page contains no extractable text")
                        except:
                            warnings.append("Could not extract text from first page")

                    # Check metadata
                    if pdf_reader.metadata:
                        if pdf_reader.metadata.title:
                            metadata['title'] = pdf_reader.metadata.title
                        if pdf_reader.metadata.author:
                            metadata['author'] = pdf_reader.metadata.author
                        if pdf_reader.metadata.creator:
                            metadata['creator'] = pdf_reader.metadata.creator

            except ImportError:
                warnings.append("PyPDF2 not available for advanced PDF validation")
            except Exception as e:
                warnings.append(f"Advanced PDF validation failed: {e}")

            return ExportValidationResult(
                True, "PDF", file_path,
                "PDF file is valid",
                warnings, metadata
            )

        except Exception as e:
            logger.error(f"Error validating PDF file {file_path}: {e}")
            return ExportValidationResult(
                False, "PDF", file_path,
                f"Validation error: {e}"
            )

class ExportValidator:
    """Main export validation class."""

    def __init__(self):
        self.validators = {
            'docx': DOCXValidator,
            'epub': EPUBValidator,
            'pdf': PDFValidator
        }

    def validate_file(self, file_path: str, format_type: str = None) -> ExportValidationResult:
        """Validate an exported file."""

        if not format_type:
            # Determine format from file extension
            ext = Path(file_path).suffix.lower().lstrip('.')
            format_type = ext

        format_type = format_type.lower()

        if format_type not in self.validators:
            return ExportValidationResult(
                False, format_type.upper(), file_path,
                f"Unsupported format: {format_type}"
            )

        validator_class = self.validators[format_type]
        return validator_class.validate(file_path)

    def validate_multiple_files(self, file_paths: List[str]) -> Dict[str, ExportValidationResult]:
        """Validate multiple exported files."""
        results = {}

        for file_path in file_paths:
            try:
                result = self.validate_file(file_path)
                results[file_path] = result
            except Exception as e:
                logger.error(f"Error validating {file_path}: {e}")
                results[file_path] = ExportValidationResult(
                    False, "UNKNOWN", file_path,
                    f"Validation failed: {e}"
                )

        return results

    def get_validation_summary(self, results: Dict[str, ExportValidationResult]) -> Dict[str, Any]:
        """Get a summary of validation results."""
        summary = {
            'total_files': len(results),
            'valid_files': 0,
            'invalid_files': 0,
            'files_with_warnings': 0,
            'formats': {},
            'total_warnings': 0
        }

        for file_path, result in results.items():
            if result.is_valid:
                summary['valid_files'] += 1
            else:
                summary['invalid_files'] += 1

            if result.warnings:
                summary['files_with_warnings'] += 1
                summary['total_warnings'] += len(result.warnings)

            format_type = result.format_type
            if format_type not in summary['formats']:
                summary['formats'][format_type] = {'valid': 0, 'invalid': 0}

            if result.is_valid:
                summary['formats'][format_type]['valid'] += 1
            else:
                summary['formats'][format_type]['invalid'] += 1

        return summary

# Global validator instance
export_validator = ExportValidator()

def validate_export_file(file_path: str, format_type: str = None) -> ExportValidationResult:
    """Convenience function to validate a single export file."""
    return export_validator.validate_file(file_path, format_type)

def validate_export_files(file_paths: List[str]) -> Dict[str, ExportValidationResult]:
    """Convenience function to validate multiple export files."""
    return export_validator.validate_multiple_files(file_paths)
