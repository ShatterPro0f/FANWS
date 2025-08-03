"""
Test Integration of Advanced Features
Verifies workflow management, notifications, and bug reporting work together
"""

import sys
import os
import logging
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_database_integration():
    """Test SQLAlchemy database integration"""
    try:
        from src.database import get_database_manager

        print("🔧 Testing database integration...")

        db_manager = get_database_manager()

        # Test connection
        with db_manager.get_session() as session:
            print("✅ Database connection successful")

        # Test workflow version creation
        version_number = db_manager.create_workflow_version(
            workflow_id="test_workflow",
            project_name="test_project",
            workflow_data={"test": "data"},
            created_by="test_user"
        )

        print(f"✅ Created workflow version: {version_number}")

        # Test version retrieval
        versions = db_manager.get_workflow_versions("test_workflow", "test_project")
        print(f"✅ Retrieved {len(versions)} workflow versions")

        return True

    except Exception as e:
        print(f"❌ Database integration failed: {e}")
        return False

def test_workflow_manager():
    """Test workflow manager with version conflicts"""
    try:
        from src.workflow_manager import WorkflowManager

        print("\n🔄 Testing workflow manager...")

        manager = WorkflowManager("test_project", "test_user")

        # Create workflow version
        workflow_data = {
            "steps": [
                {"id": "step1", "type": "input", "config": {}},
                {"id": "step2", "type": "process", "config": {}}
            ],
            "metadata": {"created": datetime.utcnow().isoformat()}
        }

        version_number, conflict_info = manager.create_workflow_version(
            "test_workflow",
            workflow_data
        )

        print(f"✅ Created workflow version: {version_number}")

        if conflict_info:
            print(f"⚠️ Conflict detected: {conflict_info.conflict_type}")
        else:
            print("✅ No conflicts detected")

        # Test version retrieval
        versions = manager.get_workflow_versions("test_workflow")
        print(f"✅ Retrieved {len(versions)} versions")

        # Test active users
        active_users = manager.get_active_users()
        print(f"✅ Active users: {active_users}")

        manager.cleanup()
        return True

    except Exception as e:
        print(f"❌ Workflow manager test failed: {e}")
        return False

def test_bug_reporting():
    """Test bug reporting system"""
    try:
        from src.bug_report_system import get_bug_report_manager, submit_bug_report

        print("\n🐛 Testing bug reporting system...")

        # Test bug report creation
        report_id = submit_bug_report(
            title="Test Bug Report",
            description="This is a test bug report to verify the system works correctly.",
            category="Testing",
            priority="Low",
            include_logs=False  # Skip logs for faster testing
        )

        print(f"✅ Created bug report: {report_id}")

        # Test bug report retrieval
        manager = get_bug_report_manager()
        reports = manager.get_bug_reports()
        print(f"✅ Retrieved {len(reports)} bug reports")

        # Test exception reporting
        try:
            raise ValueError("Test exception for bug reporting")
        except Exception as e:
            from src.bug_report_system import report_exception
            exception_report_id = report_exception(e, "Test context")
            print(f"✅ Exception reported: {exception_report_id}")

        return True

    except Exception as e:
        print(f"❌ Bug reporting test failed: {e}")
        return False

def test_collaboration_features():
    """Test collaboration features integration"""
    try:
        from src.collaboration_features import (
            initialize_collaboration_features,
            get_collaboration_manager,
            send_notification,
            create_workflow_version
        )

        print("\n🤝 Testing collaboration features...")

        # Initialize features
        success = initialize_collaboration_features("test_project", "test_user")
        print(f"✅ Collaboration features initialized: {success}")

        # Get manager
        manager = get_collaboration_manager()
        feature_status = manager.get_feature_status()

        print("📊 Feature Status:")
        for feature, enabled in feature_status.items():
            status = "✅" if enabled else "❌"
            print(f"  {status} {feature}: {enabled}")

        # Test workflow creation through collaboration manager
        if feature_status.get('workflow_versioning'):
            version_number, conflict = create_workflow_version(
                "collab_test_workflow",
                {"test": "collaboration_data"}
            )
            print(f"✅ Collaboration workflow created: {version_number}")

        # Test notification sending (may fail if no system tray)
        notification_sent = send_notification(
            'system_message',
            'Test Notification',
            'This is a test notification from the integration test'
        )
        print(f"📢 Notification sent: {notification_sent}")

        manager.cleanup()
        return True

    except Exception as e:
        print(f"❌ Collaboration features test failed: {e}")
        return False

def test_ui_components():
    """Test UI components (requires PyQt5)"""
    try:
        # Only test if PyQt5 is available and we're not in headless mode
        from PyQt5.QtWidgets import QApplication, QSystemTrayIcon
        from PyQt5.QtCore import QTimer

        print("\n🖥️ Testing UI components...")

        # Check if we can create QApplication (may fail in headless environments)
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        # Test system tray availability
        if QSystemTrayIcon.isSystemTrayAvailable():
            print("✅ System tray available")

            from src.ui.collaboration_notifications import CollaborationTrayIcon

            # Create tray icon (but don't show it in test)
            tray = CollaborationTrayIcon()
            print("✅ Collaboration tray icon created")

            # Test notification creation
            from src.ui.collaboration_notifications import (
                create_user_joined_notification,
                create_version_conflict_notification
            )

            notification = create_user_joined_notification("test_project", "test_user")
            print(f"✅ Created notification: {notification.title}")

            # Cleanup
            tray.hide()

        else:
            print("⚠️ System tray not available (headless environment)")

        # Test bug report dialog creation
        from src.ui.collaboration_notifications import BugReportDialog

        dialog = BugReportDialog()
        print("✅ Bug report dialog created")

        return True

    except Exception as e:
        print(f"❌ UI components test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 Starting Advanced Features Integration Test")
    print("=" * 60)

    tests = [
        ("Database Integration", test_database_integration),
        ("Workflow Manager", test_workflow_manager),
        ("Bug Reporting", test_bug_reporting),
        ("Collaboration Features", test_collaboration_features),
        ("UI Components", test_ui_components),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 60)
    print("📋 Test Results Summary:")
    print("-" * 30)

    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1

    print("-" * 30)
    print(f"Tests Passed: {passed}/{total}")

    if passed == total:
        print("🎉 All tests passed! Advanced features are working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
