# pystudy.ps1 - Windows PowerShell setter-upper for PyStudy CLI

# Config
$PythonVersion = "3.14"
$VenvDir = ".venv"
$MainScript = "main.py"
$RequirementsFile = "requirements.txt"

function Check-Command {
    param($cmd)
    $null -ne (Get-Command $cmd -ErrorAction SilentlyContinue)
}

function Main {

    # Check for Python
    Write-Host "Checking for Python $PythonVersion..."
    if (-not (Check-Command "python$PythonVersion")) {
        Write-Error "Python $PythonVersion is not installed. Please install it from https://python.org before running this script."
        exit 1
    }
    Write-Host "Python $PythonVersion found."

    $PythonExe = "python$PythonVersion"

    # Create virtual environment if it doesn't exist
    if (-not (Test-Path $VenvDir)) {
        Write-Host "Creating virtual environment in $VenvDir..."
        & $PythonExe -m venv $VenvDir
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to create virtual environment."
            exit 1
        }
        Write-Host "Virtual environment created."
    } else {
        Write-Host "Virtual environment found in $VenvDir."
    }

    # Activate virtual environment
    $VenvActivate = Join-Path $VenvDir "Scripts\Activate.ps1"
    if (-not (Test-Path $VenvActivate)) {
        Write-Error "Activation script not found at $VenvActivate"
        exit 1
    }

    Write-Host "Activating virtual environment..."
    & $VenvActivate
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to activate virtual environment."
        exit 1
    }
    Write-Host "Virtual environment activated."

    # Install dependencies if requirements.txt exists
    if (Test-Path $RequirementsFile) {
        Write-Host "Installing dependencies from $RequirementsFile..."
        & pip install -r $RequirementsFile
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to install dependencies. Ensure pip works and requirements.txt is valid."
            deactivate
            exit 1
        }
        Write-Host "Dependencies installed."
    } else {
        Write-Error "No $RequirementsFile found: cannot install dependencies."
        deactivate
        exit 1
    }

    # Run main.py
    Write-Host "Running $MainScript..."
    & python $MainScript
    $AppExitCode = $LASTEXITCODE

    # Deactivate virtual environment
    Write-Host "Deactivating virtual environment..."
    deactivate 2>$null
    Write-Host "Finished with exit code $AppExitCode"
    exit $AppExitCode
}

# Call main
Main
