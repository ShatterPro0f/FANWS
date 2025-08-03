"""
Comprehensive FANWS Testing Launcher
Starts FANWS with full user testing monitoring and automated validation
"""

import sys
import os
import time
import subprocess
import traceback
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fanws_testing_integration import start_fanws_testing, get_testing_status
from user_testing_monitor import get_user_monitor

def run_pre_launch_validation():
    """Run validation checks before launching FANWS."""
    print("🔍 Running pre-launch validation...")

    validation_results = []

    # Check core files exist
    required_files = [
        'fanws.py',
        'src/memory_manager.py',
        'src/file_operations.py',
        'src/per_project_config_manager.py',
        'requirements.txt'
    ]

    for file_path in required_files:
        if os.path.exists(file_path):
            validation_results.append(f"✅ {file_path}")
        else:
            validation_results.append(f"❌ {file_path} - MISSING")

    # Check directories exist
    required_dirs = [
        'src',
        'projects',
        'templates',
        'config',
        'metadata'
    ]

    for dir_path in required_dirs:
        if os.path.isdir(dir_path):
            validation_results.append(f"✅ {dir_path}/")
        else:
            validation_results.append(f"❌ {dir_path}/ - MISSING")

    # Check Python environment
    try:
        import PyQt5
        validation_results.append("✅ PyQt5 available")
    except ImportError:
        validation_results.append("❌ PyQt5 not available")

    try:
        import sqlite3
        validation_results.append("✅ SQLite3 available")
    except ImportError:
        validation_results.append("❌ SQLite3 not available")

    # Print results
    print("\nValidation Results:")
    for result in validation_results:
        print(f"  {result}")

    # Check if any critical issues
    critical_issues = [r for r in validation_results if r.startswith("❌")]
    if critical_issues:
        print(f"\n⚠️  {len(critical_issues)} critical issues found!")
        return False

    print("\n✅ All validation checks passed!")
    return True

def run_automated_tests():
    """Run automated test suite before user testing."""
    print("\n🤖 Running automated test suite...")

    test_scripts = [
        'quick_test_runner.py',
        'fanws_state_tester.py'
    ]

    results = []

    for script in test_scripts:
        if os.path.exists(script):
            print(f"\n📋 Running {script}...")
            try:
                # Run test script
                result = subprocess.run([
                    sys.executable, script
                ], text=True, timeout=60)

                if result.returncode == 0:
                    print(f"✅ {script} - PASSED")
                    results.append((script, True, "Test passed"))
                else:
                    print(f"❌ {script} - FAILED (exit code: {result.returncode})")
                    results.append((script, False, f"Exit code: {result.returncode}"))

            except subprocess.TimeoutExpired:
                print(f"⏰ {script} - TIMEOUT")
                results.append((script, False, "Test timed out"))
            except Exception as e:
                print(f"💥 {script} - ERROR: {e}")
                results.append((script, False, str(e)))
        else:
            print(f"⚠️  {script} not found, skipping...")

    # Summary
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)

    print(f"\n📊 Automated Tests: {passed}/{total} passed")

    if passed == total:
        print("✅ All automated tests passed!")
        return True
    else:
        print("⚠️  Some automated tests failed. Proceed with caution.")
        return False

def launch_fanws_with_monitoring(session_id: str = None):
    """Launch FANWS with full monitoring enabled."""
    print("\n🚀 Launching FANWS with User Testing Monitor...")

    # Start monitoring
    monitor = start_fanws_testing(session_id)

    if not monitor:
        print("❌ Failed to start monitoring system!")
        return False

    print(f"✅ Monitoring started - Session: {monitor.session_id}")

    # Set initial testing phase
    monitor.set_test_phase("application_startup")

    # Try to launch FANWS
    try:
        print("\n📱 Starting FANWS application...")

        # Launch FANWS as a subprocess
        fanws_process = subprocess.Popen([
            sys.executable, 'fanws.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print("✅ FANWS launched successfully!")
        print(f"   Process ID: {fanws_process.pid}")

        # Log the launch
        monitor.log_action("system", "application_startup", "FANWS",
                          f"Application launched with PID {fanws_process.pid}")

        return fanws_process, monitor

    except Exception as e:
        print(f"❌ Failed to launch FANWS: {e}")
        monitor.log_error("system", "application_startup",
                         f"Failed to launch FANWS: {e}", "critical",
                         "Application Launch", traceback.format_exc())
        return False

def monitor_testing_session(fanws_process, monitor):
    """Monitor the testing session while FANWS is running."""
    print("\n🔍 Monitoring testing session...")
    print("=" * 50)
    print("📋 Follow the USER_TESTING_GUIDE.md for systematic testing")
    print("🔍 All actions and errors are being automatically logged")
    print("⌨️  Commands:")
    print("   'status' - Show testing status")
    print("   'phase <name>' - Change testing phase")
    print("   'error <component> <message>' - Log manual error")
    print("   'quit' - End testing session")
    print("=" * 50)

    last_status_time = time.time()

    try:
        while True:
            # Check if FANWS is still running
            if fanws_process.poll() is not None:
                print(f"\n📱 FANWS process ended (exit code: {fanws_process.returncode})")
                # GUI applications often exit with code 1 when closed normally
                if fanws_process.returncode != 0 and fanws_process.returncode != 1:
                    monitor.log_error("system", "application_shutdown",
                                     f"FANWS exited with unexpected code {fanws_process.returncode}",
                                     "high", "Application Shutdown")
                else:
                    monitor.log_action("system", "application_shutdown", "FANWS",
                                     f"Application closed normally (exit code: {fanws_process.returncode})")
                break

            # Check for user input (non-blocking)
            try:
                import select
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    command = sys.stdin.readline().strip().lower()

                    if command == 'quit':
                        print("🔚 Ending testing session...")
                        fanws_process.terminate()
                        break
                    elif command == 'status':
                        status = get_testing_status()
                        if status:
                            print(f"\n📊 Testing Status:")
                            print(f"   Session: {status['session_id']}")
                            print(f"   Phase: {status['current_phase']}")
                            print(f"   Actions: {status['actions_logged']}")
                            print(f"   Errors: {status['errors_logged']}")
                            print(f"   Fixes Needed: {status['fixes_needed']}")
                    elif command.startswith('phase '):
                        phase = command[6:]
                        monitor.set_test_phase(phase)
                        print(f"📍 Testing phase set to: {phase}")
                    elif command.startswith('error '):
                        parts = command[6:].split(' ', 1)
                        if len(parts) == 2:
                            component, message = parts
                            monitor.log_error("user_reported", component, message, "medium")
                            print("📝 Error logged")

            except (ImportError, OSError):
                # Fallback for Windows where select might not work
                pass

            # Periodic status update
            if time.time() - last_status_time > 30:  # Every 30 seconds
                status = get_testing_status()
                if status and status['actions_logged'] > 0:
                    print(f"\n📈 {status['actions_logged']} actions logged, "
                          f"{status['errors_logged']} errors, "
                          f"{status['fixes_needed']} fixes needed")
                last_status_time = time.time()

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n⌨️  Interrupted by user")
        fanws_process.terminate()

    # Wait for process to end
    try:
        fanws_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        print("🔪 Force terminating FANWS...")
        fanws_process.kill()

    # Generate final report
    generate_testing_report(monitor)

def generate_testing_report(monitor):
    """Generate final testing report."""
    print("\n📊 Generating final testing report...")

    try:
        # Stop monitoring and generate reports
        monitor.stop_monitoring()

        # Show summary
        status = get_testing_status()
        if status:
            print(f"\n📋 Testing Session Summary:")
            print(f"   Session ID: {status['session_id']}")
            print(f"   Actions Logged: {status['actions_logged']}")
            print(f"   Errors Found: {status['errors_logged']}")
            print(f"   Fixes Needed: {status['fixes_needed']}")

        # Check for generated reports
        log_dir = Path("user_testing_logs")
        if log_dir.exists():
            reports = list(log_dir.glob("*.json")) + list(log_dir.glob("*.md"))
            if reports:
                print(f"\n📁 Generated reports:")
                for report in reports:
                    print(f"   📄 {report}")

        print("\n✅ Testing session completed successfully!")

    except Exception as e:
        print(f"❌ Error generating report: {e}")

def main():
    """Main testing launcher function."""
    print("🧪 FANWS Comprehensive Testing Launcher")
    print("=" * 50)

    # Get session ID
    session_id = input("Enter session ID (or press Enter for auto-generated): ").strip()
    if not session_id:
        session_id = f"comprehensive_{int(time.time())}"

    print(f"\n🏷️  Session ID: {session_id}")

    # Step 1: Pre-launch validation
    if not run_pre_launch_validation():
        print("\n❌ Pre-launch validation failed!")
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            print("🔚 Testing cancelled.")
            return

    # Step 2: Automated tests
    print("\n" + "=" * 50)
    automated_success = run_automated_tests()
    if not automated_success:
        print("\n⚠️  Some automated tests failed!")
        response = input("Continue with user testing? (y/N): ").strip().lower()
        if response != 'y':
            print("🔚 Testing cancelled.")
            return

    # Step 3: Launch FANWS with monitoring
    print("\n" + "=" * 50)
    launch_result = launch_fanws_with_monitoring(session_id)

    if not launch_result:
        print("❌ Failed to launch FANWS with monitoring!")
        return

    fanws_process, monitor = launch_result

    # Step 4: Monitor testing session
    monitor_testing_session(fanws_process, monitor)

    print("\n🎉 Comprehensive testing session completed!")
    print("📋 Review the generated reports for actionable fixes.")

if __name__ == "__main__":
    main()
