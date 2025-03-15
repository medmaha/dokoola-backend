# PowerShell script to restore backup files to clean JSON with proper encoding
# Usage: .\restore.ps1

# Script configuration
$backupDir = ".\.backups"
$tempFilename = "temporary.json"
$tempFilePath = Join-Path $backupDir $tempFilename

Write-Output "Temp file location: $tempFilePath"


# Create output directory if it doesn't exist
if (-not (Test-Path $backupDir)) {
    try {
        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
        Write-Host "Created output directory: $backupDir" -ForegroundColor Green
    }
    catch {
        Write-Host "Error creating output directory: $_" -ForegroundColor Red
        exit 1
    }
}

# Function for logging
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"

    $logTimestamp = Get-Date -Format "yyyy-MM-dd-HHmm"
    $logFile = ".\.backups\.logs\restore-$logTimestamp.log"

    Add-Content -Path $logFile -Value $logMessage

    switch ($Level) {
        "ERROR" { Write-Host $logMessage -ForegroundColor Red }
        "WARNING" { Write-Host $logMessage -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $logMessage -ForegroundColor Green }
        default { Write-Host $logMessage }
    }
}

# Start execution
Write-Log "-------------------------------------" "INFO"
Write-Log "Starting restoration process" "INFO"
Write-Log "-------------------------------------" "INFO"

try {
    # Find the most recent backup file
    Write-Log "Searching for latest backup file in $backupDir" "INFO"
    $mostRecentBackup = Get-ChildItem "$backupDir\*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

    if ($null -eq $mostRecentBackup) {
        Write-Log "No backup files found in $backupDir" "ERROR"
        exit 1
    }

    Write-Log "Found most recent backup: $($mostRecentBackup.Name)" "SUCCESS"

    # Try multiple encoding approaches since I don't know the exact encoding
    $encodingsToTry = @(
        @{Name = "UTF-8"; Encoding = [System.Text.Encoding]::UTF8 },
        @{Name = "UTF-16"; Encoding = [System.Text.Encoding]::Unicode },
        @{Name = "ASCII"; Encoding = [System.Text.Encoding]::ASCII },
        @{Name = "Default"; Encoding = [System.Text.Encoding]::Default }
    )

    $jsonContent = $null
    $success = $false

    foreach ($encodingInfo in $encodingsToTry) {
        Write-Log "Attempting to read with $($encodingInfo.Name) encoding" "INFO"
        try {
            # Read file with the current encoding
            $rawContent = [System.IO.File]::ReadAllBytes($mostRecentBackup.FullName)

            # Check for BOM and skip if present
            $skipBytes = 0
            if ($rawContent.Length -ge 3 -and $rawContent[0] -eq 0xEF -and $rawContent[1] -eq 0xBB -and $rawContent[2] -eq 0xBF) {
                $skipBytes = 3
                Write-Log "UTF-8 BOM detected, will skip BOM bytes" "INFO"
            }
            elseif ($rawContent.Length -ge 2 -and $rawContent[0] -eq 0xFF -and $rawContent[1] -eq 0xFE) {
                $skipBytes = 2
                Write-Log "UTF-16 LE BOM detected, will skip BOM bytes" "INFO"
            }

            # Convert bytes to string using the specified encoding
            $fileContent = $encodingInfo.Encoding.GetString($rawContent, $skipBytes, $rawContent.Length - $skipBytes)

            # Try parsing as JSON to validate
            $jsonContent = $fileContent | ConvertFrom-Json

            $success = $true
            Write-Log "Successfully read and parsed file with $($encodingInfo.Name) encoding" "SUCCESS"
            break
        }
        catch {
            Write-Log "Failed to read or parse with $($encodingInfo.Name) encoding: $_" "WARNING"
            continue
        }
    }

    if (-not $success) {
        Write-Log "All encoding attempts failed. Could not parse the backup file." "ERROR"
        exit 1
    }

    # Convert JSON back to string with proper formatting
    Write-Log "Converting JSON object to properly formatted string" "INFO"

    # A reliable approach using temporary file
    $formattedJson = $jsonContent | ConvertTo-Json -Depth 100
    $tempFile = New-TemporaryFile
    Write-Log "Created a temp file for convertedJson" "INFO"
    $utf8NoBomEncoding = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllLines($tempFilePath, $formattedJson, $utf8NoBomEncoding)
    Write-Log "Saved the JSON content to temp file" "INFO"

    # Load the data from the temp file
    Write-Log "Loading data from the temp file" "INFO"
    Write-Log "Running loaddata command" "INFO"
    python manage.py loaddata $tempFilePath
    Write-Log "Restoration complete!" "SUCCESS"

    if ($null -ne $tempFile) {
        Remove-Item $tempFile
        Write-Log "Removed a temp file $tempFile" "INFO"
    }
}

catch {
    Write-Log "An unexpected error occurred: $_" "ERROR"
    exit 1
}

Write-Log "-------------------------------------" "INFO"
Write-Log "Finished restoration process" "INFO"
Write-Log "-------------------------------------" "INFO"
