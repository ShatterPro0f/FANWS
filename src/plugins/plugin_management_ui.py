"""
Plugin Management UI Component
Provides a comprehensive plugin management interface for FANWS
"""

import sys
import os
from typing import Dict, List, Optional, Any
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Add src to path for imports
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from .plugin_manager import PluginManager
    from .plugin_system import PluginType, PluginInfo
except ImportError:
    # Fallback for when running from different directories
    PluginManager = None
    PluginType = None
    PluginInfo = None

class PluginManagementWidget(QWidget):
    """Widget for managing plugins in FANWS"""

    plugin_enabled = pyqtSignal(str)  # Plugin name
    plugin_disabled = pyqtSignal(str)  # Plugin name
    plugin_configured = pyqtSignal(str, dict)  # Plugin name, config

    def __init__(self, parent=None):
        super().__init__(parent)
        self.plugin_manager = None
        self.setup_ui()
        self.refresh_plugins()

    def setup_ui(self):
        """Set up the plugin management UI"""
        layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Plugin Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px 0;")
        header_layout.addWidget(title)

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_plugins)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        header_layout.addWidget(refresh_btn)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Plugin categories tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
            QTabBar::tab {
                padding: 8px 16px;
                margin-right: 2px;
                background-color: #F5F5F5;
                border: 1px solid #E0E0E0;
                border-bottom: none;
                border-radius: 4px 4px 0 0;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
        """)

        # Create tabs for different plugin types
        self.setup_plugin_tabs()

        layout.addWidget(self.tab_widget)

        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #757575; font-size: 12px; padding: 5px;")
        layout.addWidget(self.status_label)

    def setup_plugin_tabs(self):
        """Set up tabs for different plugin categories"""
        if not PluginType:
            return

        # Define tab configuration
        self.plugin_tabs = {
            "Content Generators": PluginType.CONTENT_GENERATOR,
            "Workflow Steps": PluginType.WORKFLOW_STEP,
            "Export Formats": PluginType.EXPORT_FORMAT,
            "Text Processors": PluginType.TEXT_PROCESSOR,
            "UI Components": PluginType.UI_COMPONENT,
            "Analytics": PluginType.ANALYTICS,
            "Integrations": PluginType.INTEGRATION
        }

        for tab_name, plugin_type in self.plugin_tabs.items():
            tab_widget = self.create_plugin_list_widget(plugin_type)
            self.tab_widget.addTab(tab_widget, tab_name)

    def create_plugin_list_widget(self, plugin_type):
        """Create a widget showing plugins of a specific type"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Scroll area for plugin list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Store reference for updating
        setattr(widget, 'content_layout', content_layout)
        setattr(widget, 'plugin_type', plugin_type)

        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        return widget

    def refresh_plugins(self):
        """Refresh the plugin list"""
        self.status_label.setText("Refreshing plugins...")

        try:
            # Initialize plugin manager if needed
            if not self.plugin_manager:
                if PluginManager:
                    self.plugin_manager = PluginManager()
                    success = self.plugin_manager.initialize()
                    if not success:
                        self.status_label.setText("Failed to initialize plugin manager")
                        return
                else:
                    self.status_label.setText("Plugin system not available")
                    return

            # Update each tab
            for i in range(self.tab_widget.count()):
                tab_widget = self.tab_widget.widget(i)
                if hasattr(tab_widget, 'plugin_type'):
                    self.update_plugin_list(tab_widget)

            # Update status
            available_count = len(self.plugin_manager.get_available_plugins())
            active_count = len(self.plugin_manager.get_active_plugins())
            self.status_label.setText(f"Found {available_count} plugins ({active_count} active)")

        except Exception as e:
            self.status_label.setText(f"Error refreshing plugins: {e}")

    def update_plugin_list(self, tab_widget):
        """Update the plugin list for a specific tab"""
        if not self.plugin_manager or not hasattr(tab_widget, 'content_layout'):
            return

        content_layout = tab_widget.content_layout
        plugin_type = tab_widget.plugin_type

        # Clear existing widgets
        while content_layout.count():
            child = content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Get plugins of this type
        plugins = self.plugin_manager.get_plugins_by_type(plugin_type)

        if not plugins:
            no_plugins_label = QLabel(f"No {plugin_type.value} plugins found")
            no_plugins_label.setStyleSheet("color: #757575; font-style: italic; padding: 20px;")
            no_plugins_label.setAlignment(Qt.AlignCenter)
            content_layout.addWidget(no_plugins_label)
        else:
            for plugin in plugins:
                plugin_widget = self.create_plugin_widget(plugin)
                content_layout.addWidget(plugin_widget)

        content_layout.addStretch()

    def create_plugin_widget(self, plugin_info):
        """Create a widget for a single plugin"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                margin: 5px;
                padding: 10px;
            }
            QFrame:hover {
                border-color: #2196F3;
            }
        """)

        layout = QVBoxLayout(widget)

        # Header with name and version
        header_layout = QHBoxLayout()

        name_label = QLabel(plugin_info.name)
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(name_label)

        version_label = QLabel(f"v{plugin_info.version}")
        version_label.setStyleSheet("color: #757575; font-size: 12px;")
        header_layout.addWidget(version_label)

        header_layout.addStretch()

        # Enable/Disable toggle
        enable_checkbox = QCheckBox("Enabled")
        enable_checkbox.setChecked(plugin_info.name in getattr(self.plugin_manager, 'enabled_plugins', set()))
        enable_checkbox.stateChanged.connect(lambda state, name=plugin_info.name: self.toggle_plugin(name, state == Qt.Checked))
        header_layout.addWidget(enable_checkbox)

        layout.addLayout(header_layout)

        # Description
        if plugin_info.description:
            desc_label = QLabel(plugin_info.description)
            desc_label.setStyleSheet("color: #757575; font-size: 12px;")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        # Author and type info
        info_layout = QHBoxLayout()

        if plugin_info.author:
            author_label = QLabel(f"By: {plugin_info.author}")
            author_label.setStyleSheet("color: #757575; font-size: 11px;")
            info_layout.addWidget(author_label)

        type_label = QLabel(f"Type: {plugin_info.plugin_type.value}")
        type_label.setStyleSheet("color: #757575; font-size: 11px;")
        info_layout.addWidget(type_label)

        info_layout.addStretch()

        # Configure button
        config_btn = QPushButton("Configure")
        config_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFC107;
                color: white;
                border: none;
                padding: 4px 12px;
                border-radius: 3px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #FFB300;
            }
        """)
        config_btn.clicked.connect(lambda: self.configure_plugin(plugin_info.name))
        info_layout.addWidget(config_btn)

        layout.addLayout(info_layout)

        return widget

    def toggle_plugin(self, plugin_name: str, enabled: bool):
        """Toggle plugin enabled/disabled state"""
        if not self.plugin_manager:
            return

        try:
            if enabled:
                success = self.plugin_manager.enable_plugin(plugin_name)
                if success:
                    self.plugin_enabled.emit(plugin_name)
                    self.status_label.setText(f"Enabled plugin: {plugin_name}")
                else:
                    self.status_label.setText(f"Failed to enable plugin: {plugin_name}")
            else:
                success = self.plugin_manager.disable_plugin(plugin_name)
                if success:
                    self.plugin_disabled.emit(plugin_name)
                    self.status_label.setText(f"Disabled plugin: {plugin_name}")
                else:
                    self.status_label.setText(f"Failed to disable plugin: {plugin_name}")

        except Exception as e:
            self.status_label.setText(f"Error toggling plugin {plugin_name}: {e}")

    def configure_plugin(self, plugin_name: str):
        """Open plugin configuration dialog"""
        if not self.plugin_manager:
            return

        try:
            # Get current plugin config
            config = self.plugin_manager.get_plugin_config(plugin_name)

            # Open configuration dialog
            dialog = PluginConfigDialog(plugin_name, config, self)
            if dialog.exec_() == QDialog.Accepted:
                new_config = dialog.get_config()
                success = self.plugin_manager.set_plugin_config(plugin_name, new_config)
                if success:
                    self.plugin_configured.emit(plugin_name, new_config)
                    self.status_label.setText(f"Configured plugin: {plugin_name}")
                else:
                    self.status_label.setText(f"Failed to configure plugin: {plugin_name}")

        except Exception as e:
            self.status_label.setText(f"Error configuring plugin {plugin_name}: {e}")

class PluginConfigDialog(QDialog):
    """Dialog for configuring plugin settings"""

    def __init__(self, plugin_name: str, config: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.plugin_name = plugin_name
        self.config = config.copy()
        self.setup_ui()

    def setup_ui(self):
        """Set up the configuration dialog UI"""
        self.setWindowTitle(f"Configure {self.plugin_name}")
        self.setModal(True)
        self.resize(400, 300)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel(f"Plugin Configuration: {self.plugin_name}")
        title.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(title)

        # Configuration form
        self.form_layout = QFormLayout()
        self.config_widgets = {}

        for key, value in self.config.items():
            widget = self.create_config_widget(key, value)
            self.config_widgets[key] = widget
            self.form_layout.addRow(key.replace('_', ' ').title(), widget)

        layout.addLayout(self.form_layout)

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def create_config_widget(self, key: str, value: Any) -> QWidget:
        """Create appropriate widget for configuration value"""
        if isinstance(value, bool):
            widget = QCheckBox()
            widget.setChecked(value)
            return widget
        elif isinstance(value, int):
            widget = QSpinBox()
            widget.setRange(-999999, 999999)
            widget.setValue(value)
            return widget
        elif isinstance(value, float):
            widget = QDoubleSpinBox()
            widget.setRange(-999999.0, 999999.0)
            widget.setValue(value)
            return widget
        else:
            widget = QLineEdit()
            widget.setText(str(value))
            return widget

    def get_config(self) -> Dict[str, Any]:
        """Get updated configuration from widgets"""
        updated_config = {}

        for key, widget in self.config_widgets.items():
            if isinstance(widget, QCheckBox):
                updated_config[key] = widget.isChecked()
            elif isinstance(widget, QSpinBox):
                updated_config[key] = widget.value()
            elif isinstance(widget, QDoubleSpinBox):
                updated_config[key] = widget.value()
            elif isinstance(widget, QLineEdit):
                text = widget.text()
                # Try to preserve original type
                original_value = self.config.get(key)
                if isinstance(original_value, int):
                    try:
                        updated_config[key] = int(text)
                    except ValueError:
                        updated_config[key] = text
                elif isinstance(original_value, float):
                    try:
                        updated_config[key] = float(text)
                    except ValueError:
                        updated_config[key] = text
                else:
                    updated_config[key] = text

        return updated_config

def create_plugin_management_widget(parent=None) -> PluginManagementWidget:
    """Factory function to create plugin management widget"""
    return PluginManagementWidget(parent)

# Test the widget if run directly
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create and show the plugin management widget
    widget = PluginManagementWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec_())
