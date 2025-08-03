# FANWS Comprehensive Testing Launcher (PowerShell)
# Launches FANWS with full user testing monitoring

param(
    [string]$SessionId = "",
    [switch]$SkipValidation = $false,
    [switch]$SkipAutomatedTests = $false,
    [switch]$Help = $false
)

# Help message
if ($Help) {
    Write-Host "🧪 FANWS Comprehensive Testing Launcher" -ForegroundColor Cyan
    Write-Host ("=" * 50)
    Write-Host ""
    Write-Host "Usage: .\launch_testing.ps1 [options]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -SessionId <id>        Specify session ID"
    Write-Host "  -SkipValidation        Skip pre-launch validation"
    Write-Host "  -SkipAutomatedTests    Skip automated test suite"
    Write-Host "  -Help                  Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\launch_testing.ps1"
    Write-Host "  .\launch_testing.ps1 -SessionId 'my_test_session'"
    Write-Host "  .\launch_testing.ps1 -SkipValidation -SkipAutomatedTests"
    exit 0
}

# Function to write colored output
function Write-ColorOutput {
    param($Message, $Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

# Function to check if file exists
function Test-RequiredFile {
    param($FilePath, $Description)
    if (Test-Path $FilePath) {
        Write-ColorOutput "✅ $Description" "Green"
        return $true
    }
    else {
        Write-ColorOutput "❌ $Description - MISSING" "Red"
        return $false
    }
}

# Function to run validation
function Invoke-PreLaunchValidation {
    Write-ColorOutput "🔍 Running pre-launch validation..." "Yellow"

    $allValid = $true

    # Check core files
    $requiredFiles = @(
        @{Path = "fanws.py"; Desc = "FANWS main script" },
        @{Path = "src\memory_manager.py"; Desc = "Memory manager" },
        @{Path = "src\file_operations.py"; Desc = "File operations" },
        @{Path = "src\per_project_config_manager.py"; Desc = "Project config manager" },
        @{Path = "requirements.txt"; Desc = "Requirements file" },
        @{Path = "user_testing_monitor.py"; Desc = "Testing monitor" },
        @{Path = "fanws_testing_integration.py"; Desc = "Testing integration" },
        @{Path = "USER_TESTING_GUIDE.md"; Desc = "User testing guide" }
    )

    foreach ($file in $requiredFiles) {
        if (-not (Test-RequiredFile $file.Path $file.Desc)) {
            $allValid = $false
        }
    }

    # Check directories
    $requiredDirs = @("src", "projects", "templates", "config", "metadata")
    foreach ($dir in $requiredDirs) {
        if (Test-Path $dir -PathType Container) {
            Write-ColorOutput "✅ $dir/" "Green"
        }
        else {
            Write-ColorOutput "❌ $dir/ - MISSING" "Red"
            $allValid = $false
        }
    }

    # Check Python environment
    try {
        $pythonVersion = python --version 2>&1
        Write-ColorOutput "✅ Python: $pythonVersion" "Green"
    }
    catch {
        Write-ColorOutput "❌ Python not available" "Red"
        $allValid = $false
    }

    if ($allValid) {
        Write-ColorOutput "`n✅ All validation checks passed!" "Green"
    }
    else {
        Write-ColorOutput "`n⚠️  Validation issues found!" "Yellow"
    }

    return $allValid
}

# Function to run automated tests
function Invoke-AutomatedTests {
    Write-ColorOutput "`n🤖 Running automated test suite..." "Yellow"

    $testScripts = @("quick_test_runner.py", "fanws_state_tester.py")
    $passed = 0
    $total = 0

    foreach ($script in $testScripts) {
        if (Test-Path $script) {
            Write-ColorOutput "`n📋 Running $script..." "Cyan"
            $total++

            try {
                $result = & python $script 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-ColorOutput "✅ $script - PASSED" "Green"
                    $passed++
                }
                else {
                    Write-ColorOutput "❌ $script - FAILED" "Red"
                    Write-ColorOutput "Error output: $result" "DarkRed"
                }
            }
            catch {
                Write-ColorOutput "💥 $script - ERROR: $_" "Red"
            }
        }
        else {
            Write-ColorOutput "⚠️  $script not found, skipping..." "Yellow"
        }
    }

    Write-ColorOutput "`n📊 Automated Tests: $passed/$total passed" "Cyan"

    if ($passed -eq $total -and $total -gt 0) {
        Write-ColorOutput "✅ All automated tests passed!" "Green"
        return $true
    }
    else {
        Write-ColorOutput "⚠️  Some automated tests failed. Proceed with caution." "Yellow"
        return $false
    }
}

# Main script
try {
    Write-ColorOutput "🧪 FANWS Comprehensive Testing Launcher" "Cyan"
    Write-ColorOutput ("=" * 50) "Cyan"

    # Get session ID if not provided
    if (-not $SessionId) {
        $SessionId = Read-Host "Enter session ID (or press Enter for auto-generated)"
        if (-not $SessionId) {
            $SessionId = "powershell_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        }
    }

    Write-ColorOutput "`n🏷️  Session ID: $SessionId" "Green"

    # Step 1: Pre-launch validation
    if (-not $SkipValidation) {
        if (-not (Invoke-PreLaunchValidation)) {
            $continue = Read-Host "`n❌ Pre-launch validation failed! Continue anyway? (y/N)"
            if ($continue -ne "y" -and $continue -ne "Y") {
                Write-ColorOutput "🔚 Testing cancelled." "Yellow"
                exit 1
            }
        }
    }
    else {
        Write-ColorOutput "⏭️  Skipping pre-launch validation..." "Yellow"
    }

    # Step 2: Automated tests
    if (-not $SkipAutomatedTests) {
        Write-ColorOutput ("`n" + ("=" * 50)) "Cyan"
        if (-not (Invoke-AutomatedTests)) {
            $continue = Read-Host "`n⚠️  Some automated tests failed! Continue with user testing? (y/N)"
            if ($continue -ne "y" -and $continue -ne "Y") {
                Write-ColorOutput "🔚 Testing cancelled." "Yellow"
                exit 1
            }
        }
    }
    else {
        Write-ColorOutput "⏭️  Skipping automated tests..." "Yellow"
    }

    # Step 3: Launch comprehensive testing
    Write-ColorOutput ("`n" + ("=" * 50)) "Cyan"
    Write-ColorOutput "🚀 Launching comprehensive testing..." "Green"

    # Execute the Python launcher
    $launcherArgs = @()
    if ($SessionId) {
        # For interactive input, we'll let the Python script handle it
        Write-ColorOutput "📱 Starting Python testing launcher..." "Cyan"
    }

    # Run the comprehensive testing launcher
    & python comprehensive_testing_launcher.py

    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "`n🎉 Testing completed successfully!" "Green"
    }
    else {
        Write-ColorOutput "`n❌ Testing completed with errors." "Red"
    }

}
catch {
    Write-ColorOutput "`n💥 Unexpected error: $_" "Red"
    Write-ColorOutput "Stack trace: $($_.ScriptStackTrace)" "DarkRed"
    exit 1
}

Write-ColorOutput "`n📋 Review the generated reports in user_testing_logs/ for actionable fixes." "Cyan"
Write-ColorOutput "📄 See USER_TESTING_GUIDE.md for detailed testing instructions." "Cyan"
