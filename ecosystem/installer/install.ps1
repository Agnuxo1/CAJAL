# CAJAL One-Click Installer for Windows
# Usage: irm https://p2pclaw.com/silicon/install.ps1 | iex

param(
    [string]$InstallDir = "$env:USERPROFILE\cajal",
    [string]$ModelPath = "",
    [switch]$NoOllamaCheck,
    [switch]$SkipModelInstall
)

$ErrorActionPreference = "Stop"
$Version = "1.0.0"

function Write-Header {
    param([string]$Text)
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
}

function Write-Step {
    param([string]$Text)
    Write-Host "[+] $Text" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Text)
    Write-Host "[!] $Text" -ForegroundColor Yellow
}

function Write-Err {
    param([string]$Text)
    Write-Host "[X] $Text" -ForegroundColor Red
}

Write-Header "CAJAL Ecosystem Installer v$Version"
Write-Host "P2PCLAW Lab, Zurich | https://p2pclaw.com/silicon"
Write-Host ""

# 1. Check prerequisites
Write-Step "Checking prerequisites..."

# Check Windows version
$os = [System.Environment]::OSVersion.Version
if ($os.Major -lt 10) {
    Write-Err "Windows 10 or later is required."
    exit 1
}

# Check PowerShell version
if ($PSVersionTable.PSVersion.Major -lt 5) {
    Write-Err "PowerShell 5.0 or later is required."
    exit 1
}

# Check for admin (not strictly required, but nice to know)
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Warn "Running without administrator privileges. Some features may be limited."
}

# 2. Check / Install Ollama
if (-not $NoOllamaCheck) {
    $ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue
    if (-not $ollamaCmd) {
        Write-Warn "Ollama not found."
        Write-Host "Would you like to install Ollama now? [Y/n]" -ForegroundColor Yellow -NoNewline
        $resp = Read-Host
        if ($resp -eq "" -or $resp -match "^[Yy]") {
            Write-Step "Downloading Ollama installer..."
            $ollamaInstaller = "$env:TEMP\OllamaSetup.exe"
            try {
                Invoke-WebRequest -Uri "https://ollama.com/download/OllamaSetup.exe" -OutFile $ollamaInstaller -UseBasicParsing
                Write-Step "Installing Ollama (this may take a minute)..."
                Start-Process -FilePath $ollamaInstaller -ArgumentList "/silent" -Wait
                Remove-Item $ollamaInstaller -ErrorAction SilentlyContinue
                Write-Step "Ollama installed."
            } catch {
                Write-Err "Failed to download/install Ollama. Please install manually from https://ollama.com"
                exit 1
            }
        } else {
            Write-Warn "Skipping Ollama installation. CAJAL requires Ollama to run."
        }
    } else {
        Write-Step "Ollama found: $($ollamaCmd.Source)"
    }
}

# 3. Check / Install Python
Write-Step "Checking Python..."
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
}
if (-not $pythonCmd) {
    Write-Warn "Python not found. Please install Python 3.10+ from https://python.org"
    Write-Host "After installing Python, re-run this installer."
    exit 1
}
$pyVersion = & $pythonCmd.Source --version 2>&1
Write-Step "Python found: $pyVersion"

# 4. Create installation directory
Write-Step "Creating CAJAL directory: $InstallDir"
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
New-Item -ItemType Directory -Force -Path "$InstallDir\models" | Out-Null
New-Item -ItemType Directory -Force -Path "$InstallDir\cli" | Out-Null
New-Item -ItemType Directory -Force -Path "$InstallDir\webapp" | Out-Null

# 5. Download ecosystem files
Write-Step "Downloading CAJAL ecosystem files..."
$baseUrl = "https://raw.githubusercontent.com/p2pclaw/cajal/main/ecosystem"

# Download CLI
$cliFiles = @(
    "cli/cajal.py",
    "cli/requirements.txt"
)
foreach ($file in $cliFiles) {
    $localPath = Join-Path $InstallDir $file
    $url = "$baseUrl/$file"
    try {
        Invoke-WebRequest -Uri $url -OutFile $localPath -UseBasicParsing -ErrorAction Stop
    } catch {
        Write-Warn "Could not download $file — will use local copy if available."
    }
}

# Download WebApp
$webFiles = @(
    "webapp/index.html",
    "webapp/app.js",
    "webapp/styles.css"
)
foreach ($file in $webFiles) {
    $localPath = Join-Path $InstallDir $file
    $url = "$baseUrl/$file"
    try {
        Invoke-WebRequest -Uri $url -OutFile $localPath -UseBasicParsing -ErrorAction Stop
    } catch {
        Write-Warn "Could not download $file"
    }
}

# 6. Install Python dependencies
Write-Step "Installing Python dependencies..."
& $pythonCmd.Source -m pip install --user -q -r "$InstallDir\cli\requirements.txt" 2>&1 | Out-Null

# 7. Create Modelfile if model path provided or default
$modelfilePath = "$InstallDir\models\Modelfile"
if ($ModelPath -and (Test-Path $ModelPath)) {
    Write-Step "Using provided model: $ModelPath"
    $modelDir = Split-Path $ModelPath -Parent
} else {
    # Default: assume model is already in outputs
    $defaultModel = "$InstallDir\models\CAJAL-4B-f16.gguf"
    if (Test-Path $defaultModel) {
        Write-Step "Found local model: $defaultModel"
        $modelDir = "$InstallDir\models"
    } else {
        Write-Warn "CAJAL-4B model GGUF not found locally."
        if (-not $SkipModelInstall) {
            Write-Host "Would you like to download CAJAL-4B (~8.4 GB)? [y/N]" -ForegroundColor Yellow -NoNewline
            $dl = Read-Host
            if ($dl -match "^[Yy]") {
                Write-Step "Downloading CAJAL-4B GGUF (this will take time)..."
                $modelUrl = "https://huggingface.co/p2pclaw/cajal-4b/resolve/main/CAJAL-4B-f16.gguf"
                try {
                    Invoke-WebRequest -Uri $modelUrl -OutFile $defaultModel -UseBasicParsing
                    Write-Step "Model downloaded successfully."
                    $modelDir = "$InstallDir\models"
                } catch {
                    Write-Err "Failed to download model. You can manually place the GGUF at: $defaultModel"
                    $modelDir = $null
                }
            } else {
                Write-Warn "Skipping model download. You'll need to provide the model path later."
                $modelDir = $null
            }
        }
    }
}

# Create Modelfile
if ($modelDir) {
    $ggufFile = Get-ChildItem "$modelDir\*.gguf" | Select-Object -First 1
    if ($ggufFile) {
        $relPath = $ggufFile.Name
        @"
FROM ./$relPath

TEMPLATE `"`"`"{{- if .System }}<|im_start|>system
{{ .System }}<|im_end|>
{{ end }}{{ range .Messages }}{{ if eq .Role `"user`" }}<|im_start|>user
{{ .Content }}<|im_end|>
{{ else if eq .Role `"assistant`" }}<|im_start|>assistant
{{ .Content }}<|im_end|>
{{ end }}{{ end }}<|im_start|>assistant
<think>
`"`"`

SYSTEM `"`"`"You are CAJAL, a distinguished scientist at the P2PCLAW laboratory in Zurich, Switzerland..."`"`"

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER num_ctx 4096
PARAMETER stop <|im_end|>
"@ | Set-Content -Path $modelfilePath -Encoding UTF8

        # Copy Modelfile to model dir
        Copy-Item $modelfilePath "$modelDir\Modelfile" -Force
    }
}

# 8. Install CAJAL into Ollama
if (-not $SkipModelInstall -and $modelDir -and (Test-Path "$modelDir\Modelfile")) {
    Write-Step "Installing CAJAL-4B into Ollama..."
    Push-Location $modelDir
    try {
        $env:PATH += ";C:\Program Files\Ollama;$env:LOCALAPPDATA\Programs\Ollama"
        ollama create cajal-4b -f Modelfile 2>&1 | ForEach-Object {
            if ($_ -match "success") { Write-Step "Ollama: $_" }
        }
        Write-Step "CAJAL-4B registered in Ollama!"
    } catch {
        Write-Warn "Could not auto-install into Ollama. Run manually: ollama create cajal-4b -f $modelDir\Modelfile"
    }
    Pop-Location
}

# 9. Create launcher scripts
Write-Step "Creating launcher scripts..."

# cajal-cli.bat
@"
@echo off
python "$InstallDir\cli\cajal.py" %*
"@ | Set-Content -Path "$InstallDir\cajal-cli.bat" -Encoding ASCII

# start-webapp.bat
@"
@echo off
echo Starting CAJAL Web Chat...
start "" "$InstallDir\webapp\index.html"
"@ | Set-Content -Path "$InstallDir\start-webapp.bat" -Encoding ASCII

# Add to PATH
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$InstallDir*") {
    Write-Step "Adding CAJAL to your PATH..."
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$InstallDir", "User")
    $env:Path += ";$InstallDir"
}

# 10. Create desktop shortcut
Write-Step "Creating desktop shortcut..."
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\CAJAL Chat.lnk")
$Shortcut.TargetPath = "$InstallDir\webapp\index.html"
$Shortcut.IconLocation = "%SystemRoot%\System32\shell32.dll,14"
$Shortcut.Save()

$Shortcut2 = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\CAJAL CLI.lnk")
$Shortcut2.TargetPath = "cmd.exe"
$Shortcut2.Arguments = "/k cajal-cli chat"
$Shortcut2.IconLocation = "%SystemRoot%\System32\cmd.exe,0"
$Shortcut2.Save()

# 11. Final summary
Write-Header "Installation Complete!"
Write-Host ""
Write-Host "CAJAL-4B is installed at: $InstallDir" -ForegroundColor Green
Write-Host ""
Write-Host "Quick Start Commands:" -ForegroundColor Cyan
Write-Host "  cajal-cli status      Check system status"
Write-Host "  cajal-cli chat        Interactive chat"
Write-Host "  cajal-cli ask Q       Ask a question"
Write-Host "  cajal-cli serve       Start API server"
Write-Host "  cajal-cli config      Edit settings"
Write-Host ""
Write-Host "Web Chat:     Double-click 'CAJAL Chat' on your desktop"
Write-Host "API Endpoint: http://localhost:8765/v1/chat/completions"
Write-Host ""
Write-Host "Integration guides: $InstallDir\integrations\" -ForegroundColor DarkGray
Write-Host ""
Write-Host "Connect to P2PCLAW: https://p2pclaw.com/silicon" -ForegroundColor Magenta
Write-Host ""

# Ask to start chat
Write-Host "Would you like to start CAJAL chat now? [Y/n]" -ForegroundColor Cyan -NoNewline
$start = Read-Host
if ($start -eq "" -or $start -match "^[Yy]") {
    Write-Host "Starting CAJAL chat...`n" -ForegroundColor Green
    & $pythonCmd.Source "$InstallDir\cli\cajal.py" chat
}
