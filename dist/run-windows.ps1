<#
.SYNOPSIS
    Lazy OS Windows PowerShell Launcher
.DESCRIPTION
    Boots Lazy OS inside WSL2 Ubuntu environment and forwards the Command Center port.
#>

param (
    [switch]$Headless,
    [switch]$FullScreen
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "          Starting Lazy OS v3 Product             " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Command Center URL: http://127.0.0.1:8766/" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan

$Args = ""
if ($Headless) {
    $Args += " --headless"
}
if ($FullScreen) {
    $Args += " --fullscreen"
}

# Resolve WSL path dynamically
try {
    $WslScriptDir = (wsl.exe -d Ubuntu wslpath -u "$ScriptDir").Trim()
    wsl.exe -d Ubuntu -- bash -c "'$WslScriptDir/run-lazy-os.sh'$Args"
} catch {
    Write-Error "Failed to execute Lazy OS launcher via WSL Ubuntu: $_"
}
