# FANWS Application Backup Guide

## 🚀 Quick Start

Your FANWS application now has multiple backup options available:

### Method 1: Python Script (Recommended)
```bash
# Create a ZIP backup (compressed, smaller)
python backup_fanws.py --type zip

# Create a folder backup (uncompressed, faster access)
python backup_fanws.py --type folder

# Create both types
python backup_fanws.py --type both

# List existing backups
python backup_fanws.py --list
```

### Method 2: Windows Batch File (Simple)
```batch
# Double-click or run from command line
quick_backup.bat
```

### Method 3: PowerShell Script (Advanced)
```powershell
# Create ZIP backup
.\backup_fanws.ps1 -BackupType zip

# Create folder backup
.\backup_fanws.ps1 -BackupType folder

# Create both types
.\backup_fanws.ps1 -BackupType both

# List existing backups
.\backup_fanws.ps1 -ListBackups
```

## 📁 Backup Location

All backups are stored in: `../FANWS_Backups/`

## 🗂️ What Gets Backed Up

### ✅ Included:
- All Python source code (`src/` directory)
- Configuration files (`config/` directory)
- Documentation (`docs/` directory)
- Project files (`projects/` directory)
- Database files (`*.db`)
- Templates and resources
- Main application files (`fanws.py`, `README.md`, etc.)

### ❌ Excluded:
- Cache files (`__pycache__/`, `*.pyc`, `*.pyo`)
- Log files (`*.log`)
- Git files (`.git/`, `.gitignore`)
- IDE files (`.vscode/`)
- Temporary files

## 📦 Backup Types

### ZIP Backup
- **Pros**: Compressed, smaller file size, easy to transfer
- **Cons**: Need to extract before use
- **Best for**: Long-term storage, sharing, archiving

### Folder Backup
- **Pros**: Ready to use immediately, faster access
- **Cons**: Larger file size, takes more disk space
- **Best for**: Quick recovery, development backup

## 🔄 Backup Schedule Recommendations

### Daily Development
```bash
python backup_fanws.py --type zip
```

### Before Major Changes
```bash
python backup_fanws.py --type both
```

### Weekly Archive
```bash
python backup_fanws.py --type zip
# Then move older backups to external storage
```

## 🛡️ Recovery Process

### From ZIP Backup:
1. Extract the ZIP file to a new location
2. Navigate to the extracted folder
3. Install dependencies: `pip install -r requirements.txt`
4. Run the application: `python fanws.py`

### From Folder Backup:
1. Copy the backup folder to your desired location
2. Navigate to the folder
3. Install dependencies: `pip install -r requirements.txt`
4. Run the application: `python fanws.py`

### Database Recovery:
1. Stop the application
2. Replace the current `*.db` files with backup versions
3. Restart the application

## 🔧 Advanced Options

### Custom Backup Location
```bash
python backup_fanws.py --dest "D:\MyBackups" --type zip
```

### PowerShell with Custom Location
```powershell
.\backup_fanws.ps1 -BackupType zip -BackupDir "D:\MyBackups"
```

## 📋 Backup Manifest

Each backup includes a manifest file (`backup_manifest_*.json`) containing:
- Backup date and time
- Source directory
- File count
- Backup type
- System information

## 🚨 Emergency Backup

If you need a quick manual backup:
1. Copy the entire FANWS folder to a safe location
2. Or use Windows built-in compression: Right-click → Send to → Compressed folder

## 📞 Support

If you encounter issues with the backup scripts:
1. Check that Python is installed and accessible
2. Ensure you have write permissions to the backup directory
3. Verify that the source directory exists and is accessible
4. Check the log output for specific error messages

## 🔄 Automation

To automate backups, you can:
1. Use Windows Task Scheduler with the batch file
2. Set up a cron job (if using WSL/Linux)
3. Create a scheduled PowerShell task

Example Windows Task Scheduler command:
```
Program: python
Arguments: backup_fanws.py --type zip
Start in: C:\Users\samue\Documents\FANWS
```
