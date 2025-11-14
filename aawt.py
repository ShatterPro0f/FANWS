#!/usr/bin/env python3
"""
FANWS - Fiction AI Novel Writing Suite
Simplified entry point following AAWT architecture.

A comprehensive desktop application for writers with real-time analysis,
project management, AI integration, and multi-format export capabilities.
"""

import sys
import logging
from pathlib import Path

# Setup logging
Path('logs').mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/fanws.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main application entry point."""
    try:
        logger.info("="*60)
        logger.info("Starting FANWS - Fiction AI Novel Writing Suite")
        logger.info("="*60)
        
        # Import PyQt5
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        
        # Initialize application
        app = QApplication(sys.argv)
        app.setApplicationName("FANWS")
        app.setOrganizationName("FANWS")
        app.setApplicationVersion("1.0")
        
        # Enable high DPI scaling
        try:
            app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
            app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        except:
            pass
        
        logger.info("Initializing application components...")
        
        # Import required AAWT-style components
        from src.system.settings_manager import SettingsManager
        from src.database.database_manager import DatabaseManager
        from src.text.text_processing import TextAnalyzer, get_text_analyzer
        from src.system.export_manager import ExportManager
        from src.system.file_operations import FileOperations
        from src.system.api_manager import APIManager, get_api_manager
        
        # Initialize managers
        logger.info("Creating settings manager...")
        settings_manager = SettingsManager('config/user_settings.json')
        
        logger.info("Creating database manager...")
        database_path = settings_manager.get('advanced.database_path', 'config/fanws.db')
        pool_size = settings_manager.get('performance.connection_pool_size', 5)
        database_manager = DatabaseManager(database_path, pool_size)
        
        logger.info("Creating text analyzer...")
        text_analyzer = get_text_analyzer() if callable(get_text_analyzer) else TextAnalyzer()
        
        logger.info("Creating export manager...")
        export_manager = ExportManager(settings_manager)
        
        logger.info("Creating file operations...")
        file_operations = FileOperations()
        
        logger.info("Creating API manager...")
        try:
            from src.system.api_manager import get_api_manager
            api_manager = get_api_manager()
        except:
            api_manager = APIManager()
        
        logger.info("All components initialized successfully")
        
        # Import and create AAWT-style main window
        from src.ui.aawt_main_window import MainWindow
        
        window = MainWindow(
            settings_manager,
            database_manager,
            api_manager,
            text_analyzer,
            export_manager,
            file_operations
        )
        
        window.show()
        
        logger.info("Application window displayed")
        logger.info("Application ready")
        
        # Run application
        exit_code = app.exec_()
        
        logger.info("Application closing...")
        logger.info(f"Exit code: {exit_code}")
        
        return exit_code
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        
        # Try to show error dialog
        try:
            from PyQt5.QtWidgets import QApplication, QMessageBox
            if not QApplication.instance():
                app = QApplication(sys.argv)
            
            QMessageBox.critical(
                None,
                "Fatal Error",
                f"FANWS encountered a fatal error and must close:\n\n{str(e)}\n\nPlease check the log file for details."
            )
        except:
            print(f"Fatal error: {e}")
        
        return 1


if __name__ == '__main__':
    sys.exit(main())
