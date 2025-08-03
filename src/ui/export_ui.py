"""
Export UI Components for FANWS

Provides UI components for document export including progress tracking,
format selection, and export validation display.
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton,
    QProgressBar, QComboBox, QCheckBox, QTextEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QSplitter, QFormLayout, QSpinBox, QDoubleSpinBox, QLineEdit,
    QFileDialog, QMessageBox, QTabWidget, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette

logger = logging.getLogger(__name__)

class ExportProgressWidget(QWidget):
    """Widget showing export progress with detailed status."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Set up the export progress UI."""
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Export Progress")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title_label)

        # Overall progress
        progress_group = QGroupBox("Overall Progress")
        progress_layout = QVBoxLayout(progress_group)

        self.overall_progress = QProgressBar()
        self.overall_progress.setRange(0, 100)
        self.overall_progress.setValue(0)
        self.overall_progress.setTextVisible(True)
        progress_layout.addWidget(self.overall_progress)

        self.overall_status_label = QLabel("Ready to export")
        progress_layout.addWidget(self.overall_status_label)

        layout.addWidget(progress_group)

        # Current operation details
        details_group = QGroupBox("Current Operation")
        details_layout = QVBoxLayout(details_group)

        self.current_operation_label = QLabel("No operation in progress")
        details_layout.addWidget(self.current_operation_label)

        self.current_progress = QProgressBar()
        self.current_progress.setRange(0, 100)
        self.current_progress.setValue(0)
        details_layout.addWidget(self.current_progress)

        self.time_elapsed_label = QLabel("Time elapsed: 0s")
        details_layout.addWidget(self.time_elapsed_label)

        self.estimated_time_label = QLabel("Estimated time remaining: Unknown")
        details_layout.addWidget(self.estimated_time_label)

        layout.addWidget(details_group)

        # Export log
        log_group = QGroupBox("Export Log")
        log_layout = QVBoxLayout(log_group)

        self.export_log = QTextEdit()
        self.export_log.setMaximumHeight(150)
        self.export_log.setReadOnly(True)
        log_layout.addWidget(self.export_log)

        layout.addWidget(log_group)

        # Initialize timer for time tracking
        self.start_time = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time_display)

    def start_export(self, total_steps: int = 100):
        """Start export progress tracking."""
        self.overall_progress.setValue(0)
        self.overall_progress.setRange(0, total_steps)
        self.current_progress.setValue(0)
        self.overall_status_label.setText("Export in progress...")
        self.export_log.clear()
        self.add_log_entry("Export started")

        # Start timing
        import time
        self.start_time = time.time()
        self.timer.start(1000)  # Update every second

    def update_overall_progress(self, value: int, status: str = ""):
        """Update overall progress."""
        self.overall_progress.setValue(value)
        if status:
            self.overall_status_label.setText(status)

    def update_current_operation(self, operation: str, progress: int = 0):
        """Update current operation details."""
        self.current_operation_label.setText(operation)
        self.current_progress.setValue(progress)
        self.add_log_entry(f"Starting: {operation}")

    def update_current_progress(self, value: int):
        """Update current operation progress."""
        self.current_progress.setValue(value)

    def add_log_entry(self, message: str):
        """Add entry to export log."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.export_log.append(f"[{timestamp}] {message}")

    def finish_export(self, success: bool = True, message: str = ""):
        """Finish export tracking."""
        self.timer.stop()

        if success:
            self.overall_progress.setValue(self.overall_progress.maximum())
            self.overall_status_label.setText("Export completed successfully")
            self.add_log_entry("Export completed successfully")
        else:
            self.overall_status_label.setText(f"Export failed: {message}")
            self.add_log_entry(f"Export failed: {message}")

        self.current_operation_label.setText("Export finished")
        self.current_progress.setValue(100)

    def update_time_display(self):
        """Update time elapsed and estimated remaining time."""
        if self.start_time:
            import time
            elapsed = time.time() - self.start_time
            self.time_elapsed_label.setText(f"Time elapsed: {int(elapsed)}s")

            # Estimate remaining time based on progress
            if self.overall_progress.value() > 0:
                progress_ratio = self.overall_progress.value() / self.overall_progress.maximum()
                estimated_total = elapsed / progress_ratio
                remaining = estimated_total - elapsed
                if remaining > 0:
                    self.estimated_time_label.setText(f"Estimated time remaining: {int(remaining)}s")
                else:
                    self.estimated_time_label.setText("Almost finished...")
            else:
                self.estimated_time_label.setText("Calculating...")

class ExportFormatSelector(QWidget):
    """Widget for selecting export formats and options."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.format_options = {}
        self.setup_ui()

    def setup_ui(self):
        """Set up the format selector UI."""
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Export Format Selection")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title_label)

        # Format selection
        format_group = QGroupBox("Export Formats")
        format_layout = QFormLayout(format_group)

        self.docx_checkbox = QCheckBox("Microsoft Word (.docx)")
        self.docx_checkbox.setChecked(True)
        format_layout.addRow(self.docx_checkbox)

        self.pdf_checkbox = QCheckBox("PDF Document (.pdf)")
        format_layout.addRow(self.pdf_checkbox)

        self.epub_checkbox = QCheckBox("EPUB E-book (.epub)")
        format_layout.addRow(self.epub_checkbox)

        self.txt_checkbox = QCheckBox("Plain Text (.txt)")
        format_layout.addRow(self.txt_checkbox)

        layout.addWidget(format_group)

        # Options for each format
        options_group = QGroupBox("Format Options")
        options_layout = QVBoxLayout(options_group)

        # DOCX options
        docx_options = QGroupBox("DOCX Options")
        docx_options_layout = QFormLayout(docx_options)

        self.docx_include_images = QCheckBox("Include images")
        self.docx_include_images.setChecked(True)
        docx_options_layout.addRow(self.docx_include_images)

        self.docx_page_breaks = QCheckBox("Insert page breaks between chapters")
        self.docx_page_breaks.setChecked(True)
        docx_options_layout.addRow(self.docx_page_breaks)

        options_layout.addWidget(docx_options)

        # PDF options
        pdf_options = QGroupBox("PDF Options")
        pdf_options_layout = QFormLayout(pdf_options)

        self.pdf_quality_combo = QComboBox()
        self.pdf_quality_combo.addItems(["High Quality", "Medium Quality", "Low Quality (Small Size)"])
        self.pdf_quality_combo.setCurrentText("High Quality")
        pdf_options_layout.addRow("Quality:", self.pdf_quality_combo)

        self.pdf_include_bookmarks = QCheckBox("Include chapter bookmarks")
        self.pdf_include_bookmarks.setChecked(True)
        pdf_options_layout.addRow(self.pdf_include_bookmarks)

        options_layout.addWidget(pdf_options)

        # EPUB options
        epub_options = QGroupBox("EPUB Options")
        epub_options_layout = QFormLayout(epub_options)

        self.epub_include_toc = QCheckBox("Include table of contents")
        self.epub_include_toc.setChecked(True)
        epub_options_layout.addRow(self.epub_include_toc)

        self.epub_split_chapters = QCheckBox("Split into separate chapter files")
        self.epub_split_chapters.setChecked(True)
        epub_options_layout.addRow(self.epub_split_chapters)

        options_layout.addWidget(epub_options)

        layout.addWidget(options_group)

        # Output settings
        output_group = QGroupBox("Output Settings")
        output_layout = QFormLayout(output_group)

        self.output_directory = QLineEdit()
        self.output_directory.setPlaceholderText("Choose output directory...")
        output_dir_layout = QHBoxLayout()
        output_dir_layout.addWidget(self.output_directory)

        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_output_directory)
        output_dir_layout.addWidget(self.browse_button)

        output_layout.addRow("Output Directory:", output_dir_layout)

        self.filename_prefix = QLineEdit()
        self.filename_prefix.setPlaceholderText("Optional filename prefix...")
        output_layout.addRow("Filename Prefix:", self.filename_prefix)

        layout.addWidget(output_group)

    def browse_output_directory(self):
        """Open directory browser."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            self.output_directory.text() or "."
        )

        if directory:
            self.output_directory.setText(directory)

    def get_selected_formats(self) -> List[str]:
        """Get list of selected export formats."""
        formats = []

        if self.docx_checkbox.isChecked():
            formats.append('docx')
        if self.pdf_checkbox.isChecked():
            formats.append('pdf')
        if self.epub_checkbox.isChecked():
            formats.append('epub')
        if self.txt_checkbox.isChecked():
            formats.append('txt')

        return formats

    def get_format_options(self) -> Dict[str, Dict[str, Any]]:
        """Get options for each format."""
        return {
            'docx': {
                'include_images': self.docx_include_images.isChecked(),
                'page_breaks': self.docx_page_breaks.isChecked()
            },
            'pdf': {
                'quality': self.pdf_quality_combo.currentText(),
                'include_bookmarks': self.pdf_include_bookmarks.isChecked()
            },
            'epub': {
                'include_toc': self.epub_include_toc.isChecked(),
                'split_chapters': self.epub_split_chapters.isChecked()
            }
        }

    def get_output_settings(self) -> Dict[str, str]:
        """Get output settings."""
        return {
            'directory': self.output_directory.text(),
            'filename_prefix': self.filename_prefix.text()
        }

class ExportValidationDisplay(QWidget):
    """Widget for displaying export validation results."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Set up the validation display UI."""
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Export Validation Results")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title_label)

        # Summary
        self.summary_label = QLabel("No validation results yet")
        layout.addWidget(self.summary_label)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels([
            "File", "Format", "Status", "Warnings", "Size"
        ])

        # Make table fill available width
        header = self.results_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        layout.addWidget(self.results_table)

        # Details area
        details_group = QGroupBox("Validation Details")
        details_layout = QVBoxLayout(details_group)

        self.details_text = QTextEdit()
        self.details_text.setMaximumHeight(150)
        self.details_text.setReadOnly(True)
        details_layout.addWidget(self.details_text)

        layout.addWidget(details_group)

        # Connect table selection to details
        self.results_table.itemSelectionChanged.connect(self.show_selected_details)

    def display_validation_results(self, results: Dict[str, Any]):
        """Display validation results."""
        if not results:
            self.summary_label.setText("No validation results to display")
            return

        # Update summary
        total_files = len(results)
        valid_files = sum(1 for result in results.values() if result.is_valid)

        self.summary_label.setText(
            f"Validated {total_files} files: {valid_files} valid, {total_files - valid_files} invalid"
        )

        # Update table
        self.results_table.setRowCount(total_files)

        for row, (file_path, result) in enumerate(results.items()):
            # File name (just basename)
            import os
            filename = os.path.basename(file_path)
            self.results_table.setItem(row, 0, QTableWidgetItem(filename))

            # Format
            self.results_table.setItem(row, 1, QTableWidgetItem(result.format_type))

            # Status
            status_item = QTableWidgetItem("✓ Valid" if result.is_valid else "✗ Invalid")
            if result.is_valid:
                status_item.setBackground(QColor(200, 255, 200))  # Light green
            else:
                status_item.setBackground(QColor(255, 200, 200))  # Light red
            self.results_table.setItem(row, 2, status_item)

            # Warnings count
            warning_count = len(result.warnings) if result.warnings else 0
            warning_item = QTableWidgetItem(str(warning_count))
            if warning_count > 0:
                warning_item.setBackground(QColor(255, 255, 200))  # Light yellow
            self.results_table.setItem(row, 3, warning_item)

            # File size
            file_size = result.metadata.get('file_size', 0) if result.metadata else 0
            size_str = self.format_file_size(file_size)
            self.results_table.setItem(row, 4, QTableWidgetItem(size_str))

        # Store results for details display
        self.validation_results = results

    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB"]
        i = 0

        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024
            i += 1

        return f"{size_bytes:.1f} {size_names[i]}"

    def show_selected_details(self):
        """Show details for selected validation result."""
        current_row = self.results_table.currentRow()

        if current_row < 0 or not hasattr(self, 'validation_results'):
            self.details_text.clear()
            return

        # Get the file path for this row
        filename_item = self.results_table.item(current_row, 0)
        if not filename_item:
            return

        filename = filename_item.text()

        # Find the full result
        result = None
        for file_path, res in self.validation_results.items():
            import os
            if os.path.basename(file_path) == filename:
                result = res
                break

        if not result:
            return

        # Build details text
        details = [f"File: {filename}"]
        details.append(f"Format: {result.format_type}")
        details.append(f"Status: {'Valid' if result.is_valid else 'Invalid'}")

        if not result.is_valid:
            details.append(f"Error: {result.message}")

        if result.warnings:
            details.append(f"\nWarnings ({len(result.warnings)}):")
            for warning in result.warnings:
                details.append(f"  • {warning}")

        if result.metadata:
            details.append(f"\nMetadata:")
            for key, value in result.metadata.items():
                if key == 'file_size':
                    value = self.format_file_size(value)
                details.append(f"  {key}: {value}")

        self.details_text.setText("\n".join(details))

class ExportManagerWidget(QWidget):
    """Main export manager widget combining all export functionality."""

    # Signals
    export_started = pyqtSignal()
    export_finished = pyqtSignal(bool, str)  # success, message

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Set up the main export manager UI."""
        layout = QVBoxLayout(self)

        # Create tab widget for different export aspects
        self.tab_widget = QTabWidget()

        # Format selection tab
        self.format_selector = ExportFormatSelector()
        self.tab_widget.addTab(self.format_selector, "Format Selection")

        # Progress tracking tab
        self.progress_widget = ExportProgressWidget()
        self.tab_widget.addTab(self.progress_widget, "Export Progress")

        # Validation results tab
        self.validation_widget = ExportValidationDisplay()
        self.tab_widget.addTab(self.validation_widget, "Validation Results")

        layout.addWidget(self.tab_widget)

        # Control buttons
        button_layout = QHBoxLayout()

        self.start_export_button = QPushButton("Start Export")
        self.start_export_button.clicked.connect(self.start_export)
        button_layout.addWidget(self.start_export_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        button_layout.addWidget(self.cancel_button)

        button_layout.addStretch()

        self.validate_button = QPushButton("Validate Exported Files")
        self.validate_button.clicked.connect(self.validate_exports)
        button_layout.addWidget(self.validate_button)

        layout.addWidget(button_layout)

    def start_export(self):
        """Start the export process."""
        formats = self.format_selector.get_selected_formats()

        if not formats:
            QMessageBox.warning(self, "No Formats Selected",
                              "Please select at least one export format.")
            return

        output_settings = self.format_selector.get_output_settings()
        if not output_settings['directory']:
            QMessageBox.warning(self, "No Output Directory",
                              "Please select an output directory.")
            return

        # Switch to progress tab
        self.tab_widget.setCurrentWidget(self.progress_widget)

        # Start progress tracking
        self.progress_widget.start_export(len(formats) * 100)

        # Enable/disable buttons
        self.start_export_button.setEnabled(False)
        self.cancel_button.setEnabled(True)

        # Emit signal
        self.export_started.emit()

    def update_export_progress(self, operation: str, current_progress: int, overall_progress: int):
        """Update export progress."""
        self.progress_widget.update_current_operation(operation, current_progress)
        self.progress_widget.update_overall_progress(overall_progress)

    def finish_export(self, success: bool, message: str = "", validation_results: Dict = None):
        """Finish the export process."""
        self.progress_widget.finish_export(success, message)

        # Enable/disable buttons
        self.start_export_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

        # Show validation results if available
        if validation_results:
            self.validation_widget.display_validation_results(validation_results)
            self.tab_widget.setCurrentWidget(self.validation_widget)

        # Emit signal
        self.export_finished.emit(success, message)

    def validate_exports(self):
        """Validate existing export files."""
        output_settings = self.format_selector.get_output_settings()
        directory = output_settings.get('directory', '')

        if not directory:
            QMessageBox.warning(self, "No Directory",
                              "Please select an output directory first.")
            return

        # Find export files in directory
        import os
        import glob

        export_files = []
        patterns = ['*.docx', '*.pdf', '*.epub', '*.txt']

        for pattern in patterns:
            export_files.extend(glob.glob(os.path.join(directory, pattern)))

        if not export_files:
            QMessageBox.information(self, "No Files Found",
                                   "No export files found in the selected directory.")
            return

        # Validate files
        try:
            from src.export_formats import validate_export_files
            results = validate_export_files(export_files)

            # Display results
            self.validation_widget.display_validation_results(results)
            self.tab_widget.setCurrentWidget(self.validation_widget)

        except Exception as e:
            QMessageBox.critical(self, "Validation Error",
                                f"Error validating files: {str(e)}")

# Convenience function to create export manager
def create_export_manager(parent=None) -> ExportManagerWidget:
    """Create an export manager widget."""
    return ExportManagerWidget(parent)
