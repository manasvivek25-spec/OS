<#
.SYNOPSIS
    Lazy OS Windows PowerShell Launcher
.DESCRIPTION
    Boots Lazy OS inside WSL2 Ubuntu environment and forwards the Command Center port.
#>

param (
    [switch]$Headless
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "          Starting Lazy OS v3 Product             " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Command Center URL: http://127.0.0.1:8766/" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan

if ($Headless) {
    wsl.exe -d Ubuntu -- bash -c "/mnt/c/Users/len/OS/dist/run-lazy-os.sh --headless"
} else {
    wsl.exe -d Ubuntu -- bash -c "/mnt/c/Users/len/OS/dist/run-lazy-os.sh"
}
