# Creates "Python Learning" icons: one on your Desktop and one in the course folder (like a game's icon beside its files).
# Double-click either one: PowerShell opens in the course folder, and `learn` works in that window.
# Run by setup (learn.cmd) and by:  .\learn.cmd shortcut

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$launcher = Join-Path $root 'learn.cmd'
if (-not (Test-Path -LiteralPath $launcher)) { throw "learn.cmd not found in $root. Run this script from the course folder." }

$desktop = [Environment]::GetFolderPath('Desktop')
$linkPaths = @((Join-Path $desktop 'Python Learning.lnk'), (Join-Path $root 'Python Learning.lnk'))

# Text the shortcut's PowerShell runs first: defines `learn` for that window, then starts it. Single quotes are doubled for PowerShell.
$launcherQ = $launcher.Replace("'", "''")
$rootQ = $root.Replace("'", "''")
$startup = "function learn { & '$launcherQ' @args }; Set-Location -LiteralPath '$rootQ'; " +
           "Write-Host 'Starting Python Learning...' -ForegroundColor Cyan; learn"

$powershell = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
$icon = Join-Path $root 'scripts\assets\learn.ico'
$shell = New-Object -ComObject WScript.Shell
foreach ($linkPath in $linkPaths) {
    $shortcut = $shell.CreateShortcut($linkPath)
    $shortcut.TargetPath = $powershell
    $shortcut.Arguments = "-NoExit -NoLogo -ExecutionPolicy Bypass -Command `"$startup`""
    $shortcut.WorkingDirectory = $root
    $shortcut.Description = 'Python learning course'
    $shortcut.IconLocation = if (Test-Path -LiteralPath $icon) { $icon } else { "$powershell,0" }
    $shortcut.Save()
    Write-Host "Created: $linkPath"
}
