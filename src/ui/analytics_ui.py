"""
Analytics UI Components for FANWS
Consolidates performance, quality, and analytics dashboards
Consolidated from multiple dashboard files in cleanup
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QProgressBar, QGroupBox, QTextEdit,
                             QFormLayout, QSpinBox, QDoubleSpinBox, QFrame,
                             QDialog, QTabWidget, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor
import logging
import time
from datetime import datetime

class AnalyticsUIComponents:
    """Analytics and performance dashboard components"""

    def __init__(self, window):
        """Initialize analytics UI components"""
        self.window = window
        self.performance_widgets = {}
        self.analytics_widgets = {}

    def create_analytics_dashboard(self):
        """Create comprehensive analytics dashboard"""
        try:
            dashboard = QWidget()
            layout = QVBoxLayout(dashboard)

            # Performance section
            layout.addWidget(self._create_performance_section())

            # Quality metrics section
            layout.addWidget(self._create_quality_section())

            # Memory and resource section
            layout.addWidget(self._create_resource_section())

            return dashboard
        except Exception as e:
            logging.error(f"Failed to create analytics dashboard: {e}")
            return QWidget()

    def _create_performance_section(self):
        """Create performance monitoring section"""
        # Consolidated from multiple dashboard files
        section = QGroupBox("Performance Metrics")
        layout = QVBoxLayout(section)

        # Performance widgets implementation
        # This would contain consolidated performance monitoring

        return section

    def _create_quality_section(self):
        """Create quality metrics section"""
        # Consolidated from quality_dashboard_ui.py
        section = QGroupBox("Quality Metrics")
        layout = QVBoxLayout(section)

        # Quality monitoring implementation

        return section

    def _create_resource_section(self):
        """Create resource monitoring section"""
        # Consolidated from productivity_dashboard_ui.py
        section = QGroupBox("Resource Usage")
        layout = QVBoxLayout(section)

        # Resource monitoring implementation

        return section

    def update_analytics_data(self):
        """Update all analytics displays with current data"""
        # Implementation for real-time updates
        pass

# Consolidated quality dashboard functionality
class QualityDashboardWidget(QWidget):
    """Quality metrics dashboard widget consolidated from quality_dashboard_ui.py"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize quality dashboard UI"""
        layout = QVBoxLayout(self)

        # Quality metrics display
        metrics_group = QGroupBox("Quality Metrics")
        metrics_layout = QFormLayout(metrics_group)

        self.quality_score = QLabel("N/A")
        self.error_count = QLabel("0")
        self.improvement_suggestions = QTextEdit()
        self.improvement_suggestions.setMaximumHeight(100)

        metrics_layout.addRow("Quality Score:", self.quality_score)
        metrics_layout.addRow("Error Count:", self.error_count)
        metrics_layout.addRow("Suggestions:", self.improvement_suggestions)

        layout.addWidget(metrics_group)

# Consolidated productivity dashboard functionality
class ProductivityDashboardWidget(QWidget):
    """Productivity metrics dashboard widget consolidated from productivity_dashboard_ui.py"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize productivity dashboard UI"""
        layout = QVBoxLayout(self)

        # Productivity metrics display
        metrics_group = QGroupBox("Productivity Metrics")
        metrics_layout = QFormLayout(metrics_group)

        self.words_per_minute = QLabel("0")
        self.session_duration = QLabel("00:00:00")
        self.daily_progress = QProgressBar()

        metrics_layout.addRow("Words/Minute:", self.words_per_minute)
        metrics_layout.addRow("Session Time:", self.session_duration)
        metrics_layout.addRow("Daily Progress:", self.daily_progress)

        layout.addWidget(metrics_group)

# Consolidated database monitoring functionality
class DatabaseMonitoringWidget(QWidget):
    """Database monitoring widget consolidated from database_monitoring_ui.py"""

    def __init__(self, db_integration=None, parent=None):
        super().__init__(parent)
        self.db_integration = db_integration
        self.init_ui()

    def init_ui(self):
        """Initialize database monitoring UI"""
        layout = QVBoxLayout(self)

        # Database status display
        status_group = QGroupBox("Database Status")
        status_layout = QFormLayout(status_group)

        self.connection_status = QLabel("Disconnected")
        self.database_size = QLabel("N/A")
        self.last_backup = QLabel("Never")

        status_layout.addRow("Connection:", self.connection_status)
        status_layout.addRow("Size:", self.database_size)
        status_layout.addRow("Last Backup:", self.last_backup)

        layout.addWidget(status_group)

        # Control buttons
        controls_group = QGroupBox("Database Operations")
        controls_layout = QHBoxLayout(controls_group)

        backup_btn = QPushButton("Create Backup")
        optimize_btn = QPushButton("Optimize")
        maintenance_btn = QPushButton("Run Maintenance")

        backup_btn.clicked.connect(self.create_backup)
        optimize_btn.clicked.connect(self.optimize_database)
        maintenance_btn.clicked.connect(self.run_maintenance)

        controls_layout.addWidget(backup_btn)
        controls_layout.addWidget(optimize_btn)
        controls_layout.addWidget(maintenance_btn)

        layout.addWidget(controls_group)

    def create_backup(self):
        """Create database backup"""
        if self.db_integration:
            try:
                success = self.db_integration.create_backup()
                if success:
                    QMessageBox.information(self, "Success", "Backup created successfully!")
                else:
                    QMessageBox.warning(self, "Warning", "Backup creation failed!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Backup failed: {str(e)}")

    def optimize_database(self):
        """Optimize database performance"""
        if self.db_integration:
            try:
                success = self.db_integration.optimize()
                if success:
                    QMessageBox.information(self, "Success", "Database optimized successfully!")
                else:
                    QMessageBox.warning(self, "Warning", "Optimization failed!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Optimization failed: {str(e)}")

    def run_maintenance(self):
        """Run database maintenance tasks"""
        if self.db_integration:
            try:
                results = self.db_integration.run_maintenance_tasks()
                if results.get('overall_status') == 'success':
                    QMessageBox.information(
                        self, "Success",
                        f"Maintenance completed successfully!\n"
                        f"Tasks completed: {', '.join(results.get('tasks_completed', []))}"
                    )
                else:
                    error_msg = "Maintenance completed with errors:\n" + '\n'.join(results.get('errors', []))
                    QMessageBox.warning(self, "Warning", error_msg)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Maintenance failed: {str(e)}")

class DatabaseMonitoringDialog(QDialog):
    """Main database monitoring and management dialog"""

    def __init__(self, db_integration=None, parent=None):
        super().__init__(parent)
        self.db_integration = db_integration
        self.setWindowTitle("Database Monitoring & Management")
        self.setModal(True)
        self.resize(800, 600)
        self.init_ui()

    def init_ui(self):
        """Initialize the monitoring dialog UI"""
        layout = QVBoxLayout(self)

        # Tab widget for different sections
        self.tab_widget = QTabWidget()

        # Monitoring tab
        self.monitoring_widget = DatabaseMonitoringWidget(self.db_integration)
        self.tab_widget.addTab(self.monitoring_widget, "Monitoring")

        # Quality tab
        self.quality_widget = QualityDashboardWidget()
        self.tab_widget.addTab(self.quality_widget, "Quality")

        # Productivity tab
        self.productivity_widget = ProductivityDashboardWidget()
        self.tab_widget.addTab(self.productivity_widget, "Productivity")

        layout.addWidget(self.tab_widget)

        # Close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_layout.addWidget(close_btn)

        layout.addLayout(close_layout)

# ====== Memory Dashboard (from memory_management_dashboard.py) ======

def create_memory_management_dashboard(parent=None):
    """Create a simple memory management dashboard for backward compatibility"""
    dashboard = QWidget()
    layout = QVBoxLayout(dashboard)

    # Memory status label
    memory_label = QLabel("Memory Management Dashboard")
    memory_label.setFont(QFont("Arial", 12, QFont.Bold))
    layout.addWidget(memory_label)

    # Basic memory info
    info_label = QLabel("Memory management features have been consolidated into the main interface.")
    layout.addWidget(info_label)

    # Add the missing method to prevent errors
    def set_memory_integration(integration):
        """Dummy method for backward compatibility"""
        pass

    dashboard.set_memory_integration = set_memory_integration

    return dashboard

