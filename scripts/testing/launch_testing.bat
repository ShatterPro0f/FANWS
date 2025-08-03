@echo off
REM FANWS Comprehensive Testing Launcher (Batch)
REM Simple batch alternative to PowerShell script

echo 🧪 FANWS Comprehensive Testing Launcher
echo ==================================================

REM Parse command line arguments
set SESSION_ID=
set SKIP_VALIDATION=0
set SKIP_TESTS=0

:parse_args
if "%1"=="" goto start_testing
if "%1"=="/?" goto show_help
if "%1"=="--help" goto show_help
if "%1"=="-h" goto show_help
if "%1"=="--session" (
    set SESSION_ID=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--skip-validation" (
    set SKIP_VALIDATION=1
    shift
    goto parse_args
)
if "%1"=="--skip-tests" (
    set SKIP_TESTS=1
    shift
    goto parse_args
)
shift
goto parse_args

:show_help
echo.
echo Usage: launch_testing.bat [options]
echo.
echo Options:
echo   --session ^<id^>      Specify session ID
echo   --skip-validation   Skip pre-launch validation
echo   --skip-tests        Skip automated test suite
echo   --help             Show this help message
echo.
echo Examples:
echo   launch_testing.bat
echo   launch_testing.bat --session my_test_session
echo   launch_testing.bat --skip-validation --skip-tests
echo.
goto end

:start_testing
REM Generate session ID if not provided
if "%SESSION_ID%"=="" (
    for /f "tokens=1-4 delims=/ " %%a in ('date /t') do set mydate=%%d%%b%%c
    for /f "tokens=1-2 delims=: " %%a in ('time /t') do set mytime=%%a%%b
    set SESSION_ID=batch_%mydate%_%mytime%
)

echo.
echo 🏷️  Session ID: %SESSION_ID%

REM Step 1: Pre-launch validation
if %SKIP_VALIDATION%==0 (
    echo.
    echo 🔍 Running pre-launch validation...
    call :validate_files
    if errorlevel 1 (
        echo.
        set /p continue="❌ Pre-launch validation failed! Continue anyway? (y/N): "
        if /i not "!continue!"=="y" (
            echo 🔚 Testing cancelled.
            goto end
        )
    )
) else (
    echo ⏭️  Skipping pre-launch validation...
)

REM Step 2: Automated tests
if %SKIP_TESTS%==0 (
    echo.
    echo ==================================================
    echo 🤖 Running automated test suite...
    call :run_automated_tests
    if errorlevel 1 (
        echo.
        set /p continue="⚠️  Some automated tests failed! Continue with user testing? (y/N): "
        if /i not "!continue!"=="y" (
            echo 🔚 Testing cancelled.
            goto end
        )
    )
) else (
    echo ⏭️  Skipping automated tests...
)

REM Step 3: Launch comprehensive testing
echo.
echo ==================================================
echo 🚀 Launching comprehensive testing...
echo 📱 Starting Python testing launcher...

python comprehensive_testing_launcher.py

if errorlevel 1 (
    echo ❌ Testing completed with errors.
) else (
    echo 🎉 Testing completed successfully!
)

echo.
echo 📋 Review the generated reports in user_testing_logs/ for actionable fixes.
echo 📄 See USER_TESTING_GUIDE.md for detailed testing instructions.

goto end

:validate_files
setlocal enabledelayedexpansion
set validation_failed=0

echo Checking core files...

set files=fanws.py src\memory_manager.py src\file_operations.py src\per_project_config_manager.py requirements.txt user_testing_monitor.py fanws_testing_integration.py USER_TESTING_GUIDE.md

for %%f in (%files%) do (
    if exist "%%f" (
        echo ✅ %%f
    ) else (
        echo ❌ %%f - MISSING
        set validation_failed=1
    )
)

echo Checking directories...
set dirs=src projects templates config metadata

for %%d in (%dirs%) do (
    if exist "%%d\" (
        echo ✅ %%d/
    ) else (
        echo ❌ %%d/ - MISSING
        set validation_failed=1
    )
)

echo Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not available
    set validation_failed=1
) else (
    for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo ✅ Python: %%v
)

if %validation_failed%==0 (
    echo.
    echo ✅ All validation checks passed!
    exit /b 0
) else (
    echo.
    echo ⚠️  Validation issues found!
    exit /b 1
)

:run_automated_tests
setlocal enabledelayedexpansion
set tests_failed=0
set passed=0
set total=0

set test_scripts=quick_test_runner.py fanws_state_tester.py

for %%s in (%test_scripts%) do (
    if exist "%%s" (
        echo.
        echo 📋 Running %%s...
        set /a total+=1

        python "%%s"
        if errorlevel 1 (
            echo ❌ %%s - FAILED
            set tests_failed=1
        ) else (
            echo ✅ %%s - PASSED
            set /a passed+=1
        )
    ) else (
        echo ⚠️  %%s not found, skipping...
    )
)

echo.
echo 📊 Automated Tests: %passed%/%total% passed

if %tests_failed%==0 (
    echo ✅ All automated tests passed!
    exit /b 0
) else (
    echo ⚠️  Some automated tests failed. Proceed with caution.
    exit /b 1
)

:end
pause
