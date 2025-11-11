# Video to Text - Application Launcher
# This script refreshes the PATH and launches the application

# Refresh PATH environment variable
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python not found. Please restart PowerShell or run:" -ForegroundColor Red
    Write-Host '  $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")' -ForegroundColor Yellow
    exit 1
}

# Launch the application
Write-Host "`nStarting Video to Text application...`n" -ForegroundColor Cyan
python main.py

