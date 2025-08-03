"""
Test runner script for FANWS pytest test suite
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path

def install_test_dependencies():
    """Install required test dependencies"""
    dependencies = [
        'pytest>=7.0.0',
        'pytest-qt>=4.0.0',
        'pytest-mock>=3.0.0',
        'pytest-cov>=4.0.0',
        'pytest-xdist>=2.5.0',  # For parallel testing
        'pytest-timeout>=2.0.0'  # For timeout handling
    ]

    print("Installing test dependencies...")
    for dep in dependencies:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
            print(f"✓ Installed {dep}")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {dep}")

def run_tests(test_type="all", verbose=False, coverage=False, parallel=False):
    """Run pytest tests with specified options"""

    # Base pytest command
    cmd = [sys.executable, '-m', 'pytest']

    # Add verbosity
    if verbose:
        cmd.append('-v')

    # Add coverage
    if coverage:
        cmd.extend(['--cov=src', '--cov-report=html', '--cov-report=term'])

    # Add parallel execution
    if parallel:
        cmd.extend(['-n', 'auto'])

    # Add timeout
    cmd.extend(['--timeout=300'])  # 5 minute timeout per test

    # Test selection
    if test_type == "unit":
        cmd.extend(['-m', 'unit'])
    elif test_type == "integration":
        cmd.extend(['-m', 'integration'])
    elif test_type == "ui":
        cmd.extend(['-m', 'ui'])
    elif test_type == "template":
        cmd.append('tests/test_template_manager.py')
    elif test_type == "plugin":
        cmd.append('tests/test_plugin_system.py')
    elif test_type == "api":
        cmd.append('tests/test_integration_workflows.py')
    elif test_type == "quick":
        cmd.extend(['--maxfail=3', '-x'])  # Stop on first 3 failures

    # Add test directory
    cmd.append('tests/')

    print(f"Running command: {' '.join(cmd)}")
    return subprocess.call(cmd)

def run_linting():
    """Run code linting"""
    print("Running code linting...")

    # Try to run flake8
    try:
        subprocess.check_call([sys.executable, '-m', 'flake8', 'src/', 'tests/'])
        print("✓ Linting passed")
        return True
    except subprocess.CalledProcessError:
        print("✗ Linting failed")
        return False
    except FileNotFoundError:
        print("⚠ flake8 not installed, skipping linting")
        return True

def check_test_environment():
    """Check if test environment is properly set up"""
    print("Checking test environment...")

    issues = []

    # Check Python version
    if sys.version_info < (3, 7):
        issues.append("Python 3.7+ required")

    # Check if pytest is available
    try:
        import pytest
        print(f"✓ pytest {pytest.__version__} available")
    except ImportError:
        issues.append("pytest not installed")

    # Check if PyQt5 is available for UI tests
    try:
        import PyQt5
        print("✓ PyQt5 available for UI tests")
    except ImportError:
        print("⚠ PyQt5 not available - UI tests will be skipped")

    # Check project structure
    project_root = Path(__file__).parent
    required_dirs = ['src', 'tests']

    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"✓ {dir_name}/ directory found")
        else:
            issues.append(f"{dir_name}/ directory missing")

    # Check test files
    test_files = [
        'tests/test_template_manager.py',
        'tests/test_integration_workflows.py',
        'tests/test_ui_components.py',
        'tests/test_plugin_system.py'
    ]

    for test_file in test_files:
        if (project_root / test_file).exists():
            print(f"✓ {test_file} found")
        else:
            print(f"⚠ {test_file} not found")

    if issues:
        print("❌ Test environment issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ Test environment OK")
        return True

def generate_test_report():
    """Generate comprehensive test report"""
    print("Generating test report...")

    cmd = [
        sys.executable, '-m', 'pytest',
        '--html=test_report.html',
        '--self-contained-html',
        '--cov=src',
        '--cov-report=html:htmlcov',
        '--junit-xml=test_results.xml',
        'tests/'
    ]

    return subprocess.call(cmd)

def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description='FANWS Test Runner')
    parser.add_argument(
        '--type',
        choices=['all', 'unit', 'integration', 'ui', 'template', 'plugin', 'api', 'quick'],
        default='all',
        help='Type of tests to run'
    )
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--coverage', '-c', action='store_true', help='Generate coverage report')
    parser.add_argument('--parallel', '-p', action='store_true', help='Run tests in parallel')
    parser.add_argument('--install-deps', action='store_true', help='Install test dependencies')
    parser.add_argument('--check-env', action='store_true', help='Check test environment')
    parser.add_argument('--lint', action='store_true', help='Run linting')
    parser.add_argument('--report', action='store_true', help='Generate HTML test report')

    args = parser.parse_args()

    # Change to project directory
    os.chdir(Path(__file__).parent)

    if args.install_deps:
        install_test_dependencies()
        return

    if args.check_env:
        if not check_test_environment():
            sys.exit(1)
        return

    if args.lint:
        if not run_linting():
            sys.exit(1)
        return

    if args.report:
        return generate_test_report()

    # Check environment before running tests
    if not check_test_environment():
        print("❌ Environment check failed. Run with --check-env for details.")
        sys.exit(1)

    # Run tests
    result = run_tests(
        test_type=args.type,
        verbose=args.verbose,
        coverage=args.coverage,
        parallel=args.parallel
    )

    if result == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")

    sys.exit(result)

if __name__ == "__main__":
    main()
