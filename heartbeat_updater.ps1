# ========================================
# Trainee Tracker - Server Heartbeat Updater
# ========================================
# This script runs in the background and updates the SERVER_LOCK
# file every 60 seconds to indicate the server is still running.
# It automatically exits when the server stops.
# ========================================

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$lockFile = Join-Path $scriptDir "SERVER_LOCK"

# Function to update heartbeat
function Update-Heartbeat {
    param (
        [string]$LockFile
    )

    try {
        # Read existing lock file
        if (Test-Path $LockFile) {
            $content = Get-Content $LockFile

            # Update LAST_HEARTBEAT line
            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            $updatedContent = @()
            $heartbeatFound = $false

            foreach ($line in $content) {
                if ($line -match "^LAST_HEARTBEAT:") {
                    $updatedContent += "LAST_HEARTBEAT: $timestamp"
                    $heartbeatFound = $true
                } else {
                    $updatedContent += $line
                }
            }

            # If heartbeat line doesn't exist, add it
            if (-not $heartbeatFound) {
                $updatedContent += "LAST_HEARTBEAT: $timestamp"
            }

            # Write back to file
            $updatedContent | Set-Content $LockFile -Force

            return $true
        } else {
            # Lock file doesn't exist - server must have stopped
            return $false
        }
    } catch {
        # Error updating heartbeat - likely server stopped
        return $false
    }
}

# Main loop
Write-Host "Heartbeat updater starting..." -ForegroundColor Green
Write-Host "Updating $lockFile every 60 seconds..." -ForegroundColor Cyan
Write-Host "This window will auto-close when server stops." -ForegroundColor Yellow
Write-Host ""

$updateCount = 0

while ($true) {
    # Wait 60 seconds
    Start-Sleep -Seconds 60

    # Update heartbeat
    $success = Update-Heartbeat -LockFile $lockFile

    if ($success) {
        $updateCount++
        $timestamp = Get-Date -Format "HH:mm:ss"
        Write-Host "[$timestamp] Heartbeat #$updateCount updated" -ForegroundColor Gray
    } else {
        Write-Host ""
        Write-Host "Lock file removed - server stopped. Exiting..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
        exit 0
    }
}
