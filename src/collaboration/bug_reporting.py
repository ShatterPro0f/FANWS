"""
Bug Reporting System
Handles bug report collection, validation, and storage
"""

import os
import sys
import json
import shutil
import logging
import zipfile
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class BugReportManager:
    """
    Manages bug report collection and storage
    """

    def __init__(self, app_data_dir: str = None):
        """
        Initialize bug report manager

        Args:
            app_data_dir: Directory for storing application data
        """
        self.app_data_dir = app_data_dir or os.path.join(os.getcwd(), "bug_reports")
        self.reports_dir = os.path.join(self.app_data_dir, "reports")
        self.logs_dir = os.path.join(self.app_data_dir, "logs")

        # Create directories
        os.makedirs(self.reports_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)

        # Settings
        self.max_reports = 100
        self.max_log_size_mb = 10
        self.include_system_info = True

        logger.info(f"Bug report manager initialized: {self.reports_dir}")

    def create_bug_report(self, report_data: Dict[str, Any],
                         include_logs: bool = True) -> str:
        """
        Create a comprehensive bug report

        Args:
            report_data: Bug report data from user
            include_logs: Whether to include system logs

        Returns:
            Bug report ID
        """
        try:
            # Generate report ID
            timestamp = datetime.utcnow()
            report_id = f"bug_{timestamp.strftime('%Y%m%d_%H%M%S')}_{hash(report_data.get('title', ''))}"

            # Prepare report structure
            bug_report = {
                'id': report_id,
                'timestamp': timestamp.isoformat(),
                'version': self._get_app_version(),
                'user_data': report_data,
                'system_info': self._collect_system_info() if self.include_system_info else {},
                'environment': self._collect_environment_info(),
                'logs': []
            }

            # Collect logs if requested
            if include_logs:
                bug_report['logs'] = self._collect_logs()

            # Save main report
            report_file = os.path.join(self.reports_dir, f"{report_id}.json")
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(bug_report, f, indent=2, default=str)

            # Create attachment package
            if include_logs:
                self._create_attachment_package(report_id, bug_report)

            # Clean up old reports
            self._cleanup_old_reports()

            logger.info(f"Bug report created: {report_id}")
            return report_id

        except Exception as e:
            logger.error(f"Error creating bug report: {e}")
            logger.error(traceback.format_exc())
            raise

    def _get_app_version(self) -> str:
        """Get application version"""
        try:
            # Try to read version from various sources
            version_files = [
                "version.txt",
                "src/version.py",
                "setup.py",
                "pyproject.toml"
            ]

            for version_file in version_files:
                if os.path.exists(version_file):
                    with open(version_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Simple version extraction
                        for line in content.split('\n'):
                            if 'version' in line.lower() and ('=' in line or ':' in line):
                                return line.strip()

            return "unknown"

        except Exception as e:
            logger.error(f"Error getting app version: {e}")
            return "error"

    def _collect_system_info(self) -> Dict[str, Any]:
        """Collect system information"""
        try:
            import platform
            import sys
            import psutil

            system_info = {
                'platform': {
                    'system': platform.system(),
                    'release': platform.release(),
                    'version': platform.version(),
                    'machine': platform.machine(),
                    'processor': platform.processor(),
                },
                'python': {
                    'version': sys.version,
                    'executable': sys.executable,
                    'platform': sys.platform,
                },
                'memory': {
                    'total': psutil.virtual_memory().total,
                    'available': psutil.virtual_memory().available,
                    'used': psutil.virtual_memory().used,
                    'percent': psutil.virtual_memory().percent,
                },
                'disk': {
                    'total': psutil.disk_usage('.').total,
                    'free': psutil.disk_usage('.').free,
                    'used': psutil.disk_usage('.').used,
                },
                'cpu': {
                    'count': psutil.cpu_count(),
                    'percent': psutil.cpu_percent(interval=1),
                }
            }

            return system_info

        except Exception as e:
            logger.error(f"Error collecting system info: {e}")
            return {'error': str(e)}

    def _collect_environment_info(self) -> Dict[str, Any]:
        """Collect environment information"""
        try:
            import subprocess

            env_info = {
                'python_packages': self._get_installed_packages(),
                'environment_vars': {
                    'PATH': os.environ.get('PATH', ''),
                    'PYTHONPATH': os.environ.get('PYTHONPATH', ''),
                    'HOME': os.environ.get('HOME', ''),
                    'USER': os.environ.get('USER', ''),
                },
                'working_directory': os.getcwd(),
                'command_line': ' '.join(sys.argv) if 'sys' in globals() else 'unknown'
            }

            # Get git info if available
            try:
                git_branch = subprocess.check_output(
                    ['git', 'branch', '--show-current'],
                    cwd=os.getcwd(),
                    stderr=subprocess.DEVNULL
                ).decode().strip()

                git_commit = subprocess.check_output(
                    ['git', 'rev-parse', 'HEAD'],
                    cwd=os.getcwd(),
                    stderr=subprocess.DEVNULL
                ).decode().strip()

                env_info['git'] = {
                    'branch': git_branch,
                    'commit': git_commit[:8]
                }

            except (subprocess.CalledProcessError, FileNotFoundError):
                env_info['git'] = 'not available'

            return env_info

        except Exception as e:
            logger.error(f"Error collecting environment info: {e}")
            return {'error': str(e)}

    def _get_installed_packages(self) -> List[str]:
        """Get list of installed Python packages"""
        try:
            import subprocess

            result = subprocess.run(
                ['pip', 'list', '--format=freeze'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return result.stdout.strip().split('\n')
            else:
                return ['pip list failed']

        except Exception as e:
            logger.error(f"Error getting installed packages: {e}")
            return [f'error: {e}']

    def _collect_logs(self) -> List[Dict[str, Any]]:
        """Collect relevant log files"""
        try:
            logs = []

            # Define log file patterns to collect
            log_patterns = [
                "*.log",
                "logs/*.log",
                "logs/*/*.log",
                "*.error",
                "errors.log",
                "debug.log",
                "application.log"
            ]

            # Search for log files
            for pattern in log_patterns:
                try:
                    from glob import glob
                    log_files = glob(pattern, recursive=True)

                    for log_file in log_files:
                        if os.path.exists(log_file):
                            logs.append(self._process_log_file(log_file))

                except Exception as e:
                    logger.error(f"Error processing log pattern {pattern}: {e}")

            return logs

        except Exception as e:
            logger.error(f"Error collecting logs: {e}")
            return [{'error': str(e)}]

    def _process_log_file(self, log_file: str) -> Dict[str, Any]:
        """Process a single log file"""
        try:
            file_size = os.path.getsize(log_file)

            # Skip very large files
            if file_size > self.max_log_size_mb * 1024 * 1024:
                return {
                    'file': log_file,
                    'size': file_size,
                    'content': f'File too large ({file_size / 1024 / 1024:.1f} MB), skipped',
                    'truncated': True
                }

            # Read log content
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Get recent lines (last 1000 lines)
            lines = content.split('\n')
            if len(lines) > 1000:
                content = '\n'.join(lines[-1000:])
                truncated = True
            else:
                truncated = False

            return {
                'file': log_file,
                'size': file_size,
                'content': content,
                'truncated': truncated,
                'line_count': len(lines)
            }

        except Exception as e:
            logger.error(f"Error processing log file {log_file}: {e}")
            return {
                'file': log_file,
                'error': str(e)
            }

    def _create_attachment_package(self, report_id: str, bug_report: Dict[str, Any]):
        """Create a zip package with all attachments"""
        try:
            package_path = os.path.join(self.reports_dir, f"{report_id}_attachments.zip")

            with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add main report
                report_file = os.path.join(self.reports_dir, f"{report_id}.json")
                zipf.write(report_file, f"{report_id}.json")

                # Add log files
                for log_info in bug_report.get('logs', []):
                    if 'file' in log_info and os.path.exists(log_info['file']):
                        try:
                            zipf.write(log_info['file'], f"logs/{os.path.basename(log_info['file'])}")
                        except Exception as e:
                            logger.error(f"Error adding log file to package: {e}")

                # Add config files if they exist
                config_files = [
                    'config/app_config.json',
                    'requirements.txt',
                    'pyproject.toml',
                    'setup.py'
                ]

                for config_file in config_files:
                    if os.path.exists(config_file):
                        try:
                            zipf.write(config_file, f"config/{os.path.basename(config_file)}")
                        except Exception as e:
                            logger.error(f"Error adding config file to package: {e}")

            logger.info(f"Created attachment package: {package_path}")

        except Exception as e:
            logger.error(f"Error creating attachment package: {e}")

    def _cleanup_old_reports(self):
        """Clean up old bug reports to limit disk usage"""
        try:
            # Get all report files
            report_files = []
            for file in os.listdir(self.reports_dir):
                if file.endswith('.json') and file.startswith('bug_'):
                    file_path = os.path.join(self.reports_dir, file)
                    stat = os.stat(file_path)
                    report_files.append((file_path, stat.st_mtime))

            # Sort by modification time (newest first)
            report_files.sort(key=lambda x: x[1], reverse=True)

            # Remove excess reports
            if len(report_files) > self.max_reports:
                for file_path, _ in report_files[self.max_reports:]:
                    try:
                        os.remove(file_path)

                        # Also remove corresponding attachment package
                        base_name = os.path.splitext(os.path.basename(file_path))[0]
                        attachment_file = os.path.join(self.reports_dir, f"{base_name}_attachments.zip")
                        if os.path.exists(attachment_file):
                            os.remove(attachment_file)

                        logger.info(f"Removed old bug report: {file_path}")

                    except Exception as e:
                        logger.error(f"Error removing old report {file_path}: {e}")

        except Exception as e:
            logger.error(f"Error cleaning up old reports: {e}")

    def get_bug_reports(self) -> List[Dict[str, Any]]:
        """Get list of all bug reports"""
        try:
            reports = []

            if not os.path.exists(self.reports_dir):
                return reports

            for file in os.listdir(self.reports_dir):
                if file.endswith('.json') and file.startswith('bug_'):
                    file_path = os.path.join(self.reports_dir, file)

                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            report = json.load(f)

                        # Add file info
                        stat = os.stat(file_path)
                        report['file_size'] = stat.st_size
                        report['file_path'] = file_path

                        reports.append(report)

                    except Exception as e:
                        logger.error(f"Error reading bug report {file}: {e}")

            # Sort by timestamp (newest first)
            reports.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

            return reports

        except Exception as e:
            logger.error(f"Error getting bug reports: {e}")
            return []

    def export_bug_report(self, report_id: str, export_path: str) -> bool:
        """
        Export a bug report to specified location

        Args:
            report_id: ID of the bug report to export
            export_path: Path where to export the report

        Returns:
            True if successful, False otherwise
        """
        try:
            # Find the report files
            report_file = os.path.join(self.reports_dir, f"{report_id}.json")
            attachment_file = os.path.join(self.reports_dir, f"{report_id}_attachments.zip")

            if not os.path.exists(report_file):
                logger.error(f"Bug report not found: {report_id}")
                return False

            # Create export directory
            export_dir = os.path.join(export_path, f"bug_report_{report_id}")
            os.makedirs(export_dir, exist_ok=True)

            # Copy main report
            shutil.copy2(report_file, export_dir)

            # Copy attachment package if it exists
            if os.path.exists(attachment_file):
                shutil.copy2(attachment_file, export_dir)

            logger.info(f"Bug report exported to: {export_dir}")
            return True

        except Exception as e:
            logger.error(f"Error exporting bug report {report_id}: {e}")
            return False

# Global bug report manager instance
_bug_report_manager = None

def get_bug_report_manager() -> BugReportManager:
    """Get the global bug report manager instance"""
    global _bug_report_manager
    if _bug_report_manager is None:
        _bug_report_manager = BugReportManager()
    return _bug_report_manager

def submit_bug_report(title: str, description: str, category: str = "General",
                     priority: str = "Medium", include_logs: bool = True) -> str:
    """
    Convenience function to submit a bug report

    Args:
        title: Bug report title
        description: Detailed description
        category: Bug category
        priority: Bug priority
        include_logs: Whether to include system logs

    Returns:
        Bug report ID
    """
    report_data = {
        'title': title,
        'description': description,
        'category': category,
        'priority': priority,
    }

    manager = get_bug_report_manager()
    return manager.create_bug_report(report_data, include_logs)

def report_exception(exception: Exception, context: str = "") -> str:
    """
    Report an exception as a bug report

    Args:
        exception: The exception that occurred
        context: Additional context about when/where it happened

    Returns:
        Bug report ID
    """
    report_data = {
        'title': f"Exception: {type(exception).__name__}",
        'description': f"Exception occurred: {str(exception)}\n\nContext: {context}\n\nTraceback:\n{traceback.format_exc()}",
        'category': "Exception",
        'priority': "High",
        'automatic': True
    }

    manager = get_bug_report_manager()
    return manager.create_bug_report(report_data, include_logs=True)
