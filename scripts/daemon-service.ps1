<#
.SYNOPSIS
    Windows Service & Task Scheduler Manager for AI_Flow Autonomous Background Daemon.

.DESCRIPTION
    Manages installation, uninstallation, starting, stopping, and status reporting
    for the AI_Flow Autonomous Background Daemon (scripts/daemon.py) on Windows.

.PARAMETER Action
    The action to perform: Install, Uninstall, Start, Stop, or Status. Default is 'Status'.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts\daemon-service.ps1 -Action Status
    powershell -ExecutionPolicy Bypass -File scripts\daemon-service.ps1 -Action Start
    powershell -ExecutionPolicy Bypass -File scripts\daemon-service.ps1 -Action Stop
    powershell -ExecutionPolicy Bypass -File scripts\daemon-service.ps1 -Action Install
    powershell -ExecutionPolicy Bypass -File scripts\daemon-service.ps1 -Action Uninstall
#>

[CmdletBinding()]
param(
    [ValidateSet('Install', 'Uninstall', 'Start', 'Stop', 'Status')]
    [string]$Action = 'Status'
)

$ErrorActionPreference = 'Continue'

# ---------------------------------------------------------------------------
# Resolve Project Directories & Binaries
# ---------------------------------------------------------------------------
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RepoRoot = Split-Path -Parent $ScriptDir
$DaemonScript = Join-Path $ScriptDir "daemon.py"
$DataDir = Join-Path $RepoRoot "data"
$PidFile = Join-Path $DataDir "daemon.pid"
$DbFile = Join-Path $DataDir "daemon.db"
$TaskName = "AIFlow_Daemon"

# Resolve pythonw executable (prefers pythonw, falls back to python)
$pythonwCmd = Get-Command pythonw.exe -ErrorAction SilentlyContinue
if ($pythonwCmd) {
    $PythonExe = $pythonwCmd.Source
} else {
    $pythonCmd = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        $PythonExe = $pythonCmd.Source
    } else {
        $PythonExe = "pythonw.exe"
    }
}

# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------
function Get-DaemonProcess {
    if (Test-Path $PidFile) {
        $rawPid = (Get-Content $PidFile -ErrorAction SilentlyContinue).Trim()
        if ($rawPid -match '^\d+$') {
            $p = Get-Process -Id ([int]$rawPid) -ErrorAction SilentlyContinue
            if ($p) {
                return $p
            }
        }
    }
    return $null
}

function Test-ScheduledTaskInstalled {
    $null = schtasks /Query /TN $TaskName 2>&1
    return ($LASTEXITCODE -eq 0)
}

# ---------------------------------------------------------------------------
# Execute Requested Action
# ---------------------------------------------------------------------------
switch ($Action) {
    'Install' {
        Write-Host "`n[AIFlow_Daemon] Installing Windows Task Scheduler task '$TaskName'..." -ForegroundColor Cyan
        $taskCmd = "`"$PythonExe`" `"$DaemonScript`""
        
        # Register scheduled task to run silently on logon
        $createOutput = schtasks /Create /TN $TaskName /TR "$taskCmd" /SC ONLOGON /F 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[AIFlow_Daemon] Successfully registered Task Scheduler task '$TaskName'." -ForegroundColor Green
            Write-Host "                Trigger: At user logon (SC ONLOGON)" -ForegroundColor Gray
            Write-Host "                Command: $taskCmd" -ForegroundColor Gray
        } else {
            Write-Host "[AIFlow_Daemon] Warning: schtasks returned exit code $LASTEXITCODE" -ForegroundColor Yellow
            Write-Host "                Details: $createOutput" -ForegroundColor Gray
        }
    }

    'Uninstall' {
        Write-Host "`n[AIFlow_Daemon] Uninstalling Windows Task Scheduler task '$TaskName'..." -ForegroundColor Cyan
        
        # Stop running daemon if active
        $proc = Get-DaemonProcess
        if ($proc) {
            Write-Host "[AIFlow_Daemon] Stopping running daemon process (PID: $($proc.Id))..." -ForegroundColor Yellow
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            if (Test-Path $PidFile) { Remove-Item $PidFile -Force -ErrorAction SilentlyContinue }
        }

        $deleteOutput = schtasks /Delete /TN $TaskName /F 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[AIFlow_Daemon] Successfully removed Task Scheduler task '$TaskName'." -ForegroundColor Green
        } else {
            Write-Host "[AIFlow_Daemon] Task '$TaskName' was not found or already removed." -ForegroundColor Yellow
        }
    }

    'Start' {
        Write-Host "`n[AIFlow_Daemon] Starting AI_Flow Background Daemon..." -ForegroundColor Cyan
        $existing = Get-DaemonProcess
        if ($existing) {
            $memMb = [math]::Round($existing.WorkingSet64 / 1MB, 2)
            Write-Host "[AIFlow_Daemon] Daemon is ALREADY running!" -ForegroundColor Yellow
            Write-Host "                PID    : $($existing.Id)" -ForegroundColor Yellow
            Write-Host "                Memory : $memMb MB" -ForegroundColor Yellow
            return
        }

        # Start process with pythonw in hidden window style
        try {
            $startProc = Start-Process -FilePath $PythonExe -ArgumentList "`"$DaemonScript`"" -WindowStyle Hidden -PassThru
            Start-Sleep -Seconds 1
            
            $activeProc = Get-DaemonProcess
            if (-not $activeProc -and $startProc -and -not $startProc.HasExited) {
                $activeProc = $startProc
            }

            if ($activeProc) {
                $memMb = [math]::Round($activeProc.WorkingSet64 / 1MB, 2)
                Write-Host "[AIFlow_Daemon] Daemon successfully started!" -ForegroundColor Green
                Write-Host "                PID    : $($activeProc.Id)" -ForegroundColor Green
                Write-Host "                Memory : $memMb MB" -ForegroundColor Gray
                Write-Host "                Ledger : $DbFile" -ForegroundColor Gray
            } else {
                Write-Host "[AIFlow_Daemon] Process was started (ID: $($startProc.Id)), verifying PID registration..." -ForegroundColor Green
            }
        } catch {
            Write-Host "[AIFlow_Daemon] Failed to start daemon: $_" -ForegroundColor Red
        }
    }

    'Stop' {
        Write-Host "`n[AIFlow_Daemon] Stopping AI_Flow Background Daemon..." -ForegroundColor Cyan
        $proc = Get-DaemonProcess
        if ($proc) {
            $procId = $proc.Id
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
            Start-Sleep -Milliseconds 500
            if (Test-Path $PidFile) { Remove-Item $PidFile -Force -ErrorAction SilentlyContinue }
            Write-Host "[AIFlow_Daemon] Daemon process $procId stopped successfully." -ForegroundColor Green
        } else {
            # Clean up dangling PID file if process already terminated
            if (Test-Path $PidFile) {
                Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
            }
            Write-Host "[AIFlow_Daemon] No running daemon process found." -ForegroundColor Yellow
        }
    }

    'Status' {
        Write-Host "`n============================================================" -ForegroundColor Cyan
        Write-Host "        AI_Flow Background Daemon Service Status            " -ForegroundColor Cyan
        Write-Host "============================================================" -ForegroundColor Cyan

        # 1. Scheduled Task Status
        $isInstalled = Test-ScheduledTaskInstalled
        if ($isInstalled) {
            Write-Host "Scheduled Task ($TaskName) : " -NoNewline
            Write-Host "Installed (Runs on Logon)" -ForegroundColor Green
        } else {
            Write-Host "Scheduled Task ($TaskName) : " -NoNewline
            Write-Host "Not Installed" -ForegroundColor Gray
        }

        # 2. Process Status
        $proc = Get-DaemonProcess
        if ($proc) {
            $memMb = [math]::Round($proc.WorkingSet64 / 1MB, 2)
            $cpuTime = $proc.TotalProcessorTime.ToString("hh\:mm\:ss\.fff")
            $startTime = $proc.StartTime.ToString("yyyy-MM-dd HH:mm:ss")
            Write-Host "Daemon Process            : " -NoNewline
            Write-Host "RUNNING" -ForegroundColor Green
            Write-Host "  - PID                   : $($proc.Id)" -ForegroundColor White
            Write-Host "  - Memory (WorkingSet)   : $memMb MB" -ForegroundColor White
            Write-Host "  - CPU Time Used         : $cpuTime" -ForegroundColor White
            Write-Host "  - Started At            : $startTime" -ForegroundColor White
        } else {
            Write-Host "Daemon Process            : " -NoNewline
            Write-Host "STOPPED" -ForegroundColor Yellow
        }

        # 3. Environment & Ledger Info
        Write-Host "`nPaths & Storage:" -ForegroundColor Cyan
        Write-Host "  - Daemon Script         : $DaemonScript" -ForegroundColor Gray
        Write-Host "  - Python Executable     : $PythonExe" -ForegroundColor Gray
        
        if (Test-Path $DbFile) {
            $dbItem = Get-Item $DbFile
            $dbKb = [math]::Round($dbItem.Length / 1KB, 2)
            Write-Host "  - SQLite Ledger         : $DbFile ($dbKb KB)" -ForegroundColor Gray
        } else {
            Write-Host "  - SQLite Ledger         : $DbFile (Not initialized yet)" -ForegroundColor Gray
        }

        $inboxCount = (Get-ChildItem -Path (Join-Path $DataDir "queue\inbox") -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -ne ".gitkeep" }).Count
        Write-Host "  - Inbox Queue Tasks     : $inboxCount pending" -ForegroundColor Gray
        Write-Host "============================================================`n" -ForegroundColor Cyan
    }
}
