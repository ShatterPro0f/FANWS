# FANWS Application Backup Script (PowerShell)
# Creates comprehensive backups of your FANWS application

param(
    [Parameter(HelpMessage = "Type of backup: zip, folder, or both")]
    [ValidateSet("zip", "folder", "both")]
    [string]$BackupType = "both",

    [Parameter(HelpMessage = "Destination directory for backups")]
    [string]$BackupDir = "..\FANWS_Backups",

    [Parameter(HelpMessage = "List existing backups")]
    [switch]$ListBackups
)

function Write-Header {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "    FANWS Application Backup Tool" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Get-Timestamp {
    return Get-Date -Format "yyyyMMdd_HHmmss"
}

function New-BackupDirectory {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
        Write-Host "📁 Created backup directory: $Path" -ForegroundColor Green
    }
    else {
        Write-Host "📁 Using existing backup directory: $Path" -ForegroundColor Yellow
    }
}

function New-ZipBackup {
    param(
        [string]$SourcePath,
        [string]$BackupPath,
        [string]$Timestamp
    )

    $ZipPath = Join-Path $BackupPath "FANWS_Backup_$Timestamp.zip"
    Write-Host "🗜️  Creating ZIP backup..." -ForegroundColor Blue

    # Get all files excluding certain patterns
    $FilesToBackup = Get-ChildItem -Path $SourcePath -Recurse -File |
    Where-Object {
        $_.Extension -notin @('.pyc', '.pyo', '.log') -and
        $_.Name -notlike '.*' -and
        $_.Directory.Name -notin @('__pycache__', '.git', '.vscode', 'node_modules')
    }

    # Create ZIP file
    if (Get-Command Compress-Archive -ErrorAction SilentlyContinue) {
        # Use PowerShell 5+ built-in compression
        $TempList = $FilesToBackup | ForEach-Object { $_.FullName }
        Compress-Archive -Path $TempList -DestinationPath $ZipPath -Force
    }
    else {
        # Fallback to .NET compression
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        [System.IO.Compression.ZipFile]::CreateFromDirectory($SourcePath, $ZipPath)
    }

    $ZipSize = (Get-Item $ZipPath).Length / 1MB
    Write-Host "✅ ZIP backup created: $ZipPath ($($ZipSize.ToString('F1')) MB)" -ForegroundColor Green
    return $ZipPath
}

function New-FolderBackup {
    param(
        [string]$SourcePath,
        [string]$BackupPath,
        [string]$Timestamp
    )

    $FolderPath = Join-Path $BackupPath "FANWS_Backup_$Timestamp"
    Write-Host "📂 Creating folder backup..." -ForegroundColor Blue

    # Copy directory structure
    robocopy $SourcePath $FolderPath /E /XD __pycache__ .git .vscode node_modules /XF *.pyc *.pyo *.log .* /NFL /NDL /NP

    if ($LASTEXITCODE -le 7) {
        # robocopy success codes
        $FolderSize = (Get-ChildItem -Path $FolderPath -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB
        Write-Host "✅ Folder backup created: $FolderPath ($($FolderSize.ToString('F1')) MB)" -ForegroundColor Green
        return $FolderPath
    }
    else {
        Write-Host "❌ Folder backup failed" -ForegroundColor Red
        return $null
    }
}

function Backup-Databases {
    param(
        [string]$SourcePath,
        [string]$BackupPath,
        [string]$Timestamp
    )

    $DatabaseFiles = Get-ChildItem -Path $SourcePath -Filter "*.db" -File
    $BackupPaths = @()

    foreach ($DbFile in $DatabaseFiles) {
        $BackupDbPath = Join-Path $BackupPath "$($DbFile.BaseName)_backup_$Timestamp.db"
        Copy-Item -Path $DbFile.FullName -Destination $BackupDbPath -Force
        Write-Host "💾 Database backup: $BackupDbPath" -ForegroundColor Magenta
        $BackupPaths += $BackupDbPath
    }

    return $BackupPaths
}

function Save-BackupManifest {
    param(
        [string]$BackupPath,
        [string]$SourcePath,
        [string]$Timestamp
    )

    $ManifestPath = Join-Path (Split-Path $BackupPath) "backup_manifest_$Timestamp.json"

    $Manifest = @{
        backup_date      = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
        source_directory = $SourcePath
        backup_path      = $BackupPath
        backup_type      = "full_application_backup"
        created_by       = "PowerShell_Backup_Script"
        computer_name    = $env:COMPUTERNAME
        user_name        = $env:USERNAME
    }

    $Manifest | ConvertTo-Json -Depth 2 | Out-File -FilePath $ManifestPath -Encoding UTF8
    Write-Host "📋 Backup manifest saved: $ManifestPath" -ForegroundColor Cyan
    return $ManifestPath
}

function Show-ExistingBackups {
    param([string]$BackupPath)

    if (-not (Test-Path $BackupPath)) {
        Write-Host "❌ No backup directory found at: $BackupPath" -ForegroundColor Red
        return
    }

    $Backups = Get-ChildItem -Path $BackupPath | Where-Object { $_.Name -like "FANWS_Backup_*" } | Sort-Object LastWriteTime -Descending

    if ($Backups.Count -eq 0) {
        Write-Host "❌ No existing backups found" -ForegroundColor Red
        return
    }

    Write-Host "📋 Existing backups:" -ForegroundColor Yellow
    foreach ($Backup in $Backups) {
        $Size = if ($Backup.PSIsContainer) {
            (Get-ChildItem -Path $Backup.FullName -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB
        }
        else {
            $Backup.Length / 1MB
        }
        $Type = if ($Backup.PSIsContainer) { "Folder" } else { "ZIP" }
        Write-Host "   📦 $($Backup.Name) ($Type, $($Size.ToString('F1')) MB) - $($Backup.LastWriteTime.ToString('yyyy-MM-dd HH:mm'))" -ForegroundColor White
    }
}

function Start-BackupProcess {
    param(
        [string]$SourcePath,
        [string]$BackupPath,
        [string]$BackupType,
        [string]$Timestamp
    )

    Write-Host "🚀 Starting FANWS Application Backup..." -ForegroundColor Green
    Write-Host "📍 Source: $SourcePath" -ForegroundColor Gray
    Write-Host "📁 Destination: $BackupPath" -ForegroundColor Gray
    Write-Host "=" * 50 -ForegroundColor Gray

    New-BackupDirectory -Path $BackupPath

    $BackupPaths = @()

    # Create backups based on type
    switch ($BackupType) {
        "zip" {
            $ZipPath = New-ZipBackup -SourcePath $SourcePath -BackupPath $BackupPath -Timestamp $Timestamp
            if ($ZipPath) {
                $BackupPaths += $ZipPath
                Save-BackupManifest -BackupPath $ZipPath -SourcePath $SourcePath -Timestamp $Timestamp | Out-Null
            }
        }
        "folder" {
            $FolderPath = New-FolderBackup -SourcePath $SourcePath -BackupPath $BackupPath -Timestamp $Timestamp
            if ($FolderPath) {
                $BackupPaths += $FolderPath
                Save-BackupManifest -BackupPath $FolderPath -SourcePath $SourcePath -Timestamp $Timestamp | Out-Null
            }
        }
        "both" {
            $ZipPath = New-ZipBackup -SourcePath $SourcePath -BackupPath $BackupPath -Timestamp $Timestamp
            if ($ZipPath) {
                $BackupPaths += $ZipPath
                Save-BackupManifest -BackupPath $ZipPath -SourcePath $SourcePath -Timestamp $Timestamp | Out-Null
            }

            $FolderPath = New-FolderBackup -SourcePath $SourcePath -BackupPath $BackupPath -Timestamp $Timestamp
            if ($FolderPath) {
                $BackupPaths += $FolderPath
                Save-BackupManifest -BackupPath $FolderPath -SourcePath $SourcePath -Timestamp $Timestamp | Out-Null
            }
        }
    }

    # Backup databases
    $DbBackups = Backup-Databases -SourcePath $SourcePath -BackupPath $BackupPath -Timestamp $Timestamp
    $BackupPaths += $DbBackups

    Write-Host ""
    Write-Host "=" * 50 -ForegroundColor Gray
    Write-Host "✅ Backup completed successfully!" -ForegroundColor Green
    Write-Host "📁 Backup location: $BackupPath" -ForegroundColor Cyan
    Write-Host "📊 Total backups created: $($BackupPaths.Count)" -ForegroundColor Cyan

    return $BackupPaths
}

# Main execution
Write-Header

$CurrentPath = Get-Location
$BackupDestination = Resolve-Path $BackupDir -ErrorAction SilentlyContinue
if (-not $BackupDestination) {
    $BackupDestination = Join-Path (Split-Path $CurrentPath) "FANWS_Backups"
}

if ($ListBackups) {
    Show-ExistingBackups -BackupPath $BackupDestination
}
else {
    $Timestamp = Get-Timestamp
    Start-BackupProcess -SourcePath $CurrentPath -BackupPath $BackupDestination -BackupType $BackupType -Timestamp $Timestamp
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
