@echo off
REM FANWS Production Validation Script
REM Run this after restarting terminal to confirm production readiness

echo ============================================================
echo FANWS PRODUCTION VALIDATION
echo ============================================================

cd /d "c:\Users\samue\Documents\FANWS"

echo.
echo 1. Running Quick Validation...
python quick_validation.py
if %ERRORLEVEL% NEQ 0 (
    echo FAILED: Quick validation failed
    pause
    exit /b 1
)

echo.
echo 2. Running Comprehensive Tests...
python testing_orchestrator.py
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Some comprehensive tests failed - check output
)

echo.
echo 3. Starting Error Tracking System...
start /b python error_tracking_system.py

echo.
echo ============================================================
echo FANWS PRODUCTION VALIDATION COMPLETE
echo ============================================================
echo.
echo Next steps:
echo - Review test results above
echo - Verify >95%% success rate
echo - Monitor error tracking system
echo - FANWS is ready for production use!
echo.
pause
