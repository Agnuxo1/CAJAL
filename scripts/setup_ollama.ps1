#Requires -Version 5.1
<#
.SYNOPSIS
    CAJAL Ollama Setup Script (Windows)

.DESCRIPTION
    Verifica la instalacion de Ollama, descarga/usa el GGUF generado, crea el modelo
    y lo ejecuta en Windows.

.PARAMETER ModelDir
    Directorio donde estan los archivos GGUF exportados. Default: .\gguf_exports

.PARAMETER Quant
    Nivel de cuantizacion a usar. Default: q4_k_m

.EXAMPLE
    .\setup_ollama.ps1 -ModelDir "C:\Models\p2pclaw" -Quant "q5_k_m"
#>
[CmdletBinding()]
param(
    [string]$ModelDir = ".\gguf_exports",
    [ValidateSet("q4_k_m", "q5_k_m", "q8_0", "f16")]
    [string]$Quant = "q4_k_m"
)

# =============================================================================
# Configuracion
# =============================================================================
$MODEL_NAME = "cajal"
$OLLAMA_PORT = 11434
$ErrorActionPreference = "Stop"

# =============================================================================
# Funciones auxiliares
# =============================================================================

function Write-Banner {
    param([string]$Text)
    $width = 60
    $line = "=" * $width
    Write-Host ""
    Write-Host $line -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host $line -ForegroundColor Cyan
    Write-Host ""
}

function Test-OllamaInstalled {
    Write-Host "[CHECK] Verificando instalacion de Ollama..." -ForegroundColor Yellow
    
    $ollamaCmd = Get-Command "ollama" -ErrorAction SilentlyContinue
    if (-not $ollamaCmd) {
        Write-Host "[ERROR] Ollama no esta instalado o no esta en el PATH." -ForegroundColor Red
        Write-Host ""
        Write-Host "Instalacion rapida en Windows:" -ForegroundColor White
        Write-Host "  1. Descargue desde: https://ollama.com/download/windows"
        Write-Host "  2. Ejecute el instalador .exe"
        Write-Host "  3. Reinicie PowerShell y reintente"
        Write-Host ""
        Write-Host "Alternativa via winget:" -ForegroundColor White
        Write-Host "  winget install Ollama.Ollama"
        Write-Host ""
        exit 1
    }
    
    $version = (ollama --version 2>$null) -join " "
    Write-Host "[OK] Ollama detectado: $version" -ForegroundColor Green
}

function Test-OllamaRunning {
    Write-Host "[CHECK] Verificando servicio Ollama..." -ForegroundColor Yellow
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:${OLLAMA_PORT}/api/tags" -Method Get -ErrorAction Stop
        Write-Host "[OK] Servicio Ollama responde en puerto $OLLAMA_PORT" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "[WARN] El servicio Ollama no responde. Intentando iniciar..." -ForegroundColor Yellow
        
        # Intentar iniciar Ollama
        Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
        Start-Sleep -Seconds 3
        
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:${OLLAMA_PORT}/api/tags" -Method Get -ErrorAction Stop
            Write-Host "[OK] Servicio Ollama iniciado correctamente" -ForegroundColor Green
            return $true
        }
        catch {
            Write-Host "[ERROR] No se pudo iniciar el servicio Ollama." -ForegroundColor Red
            Write-Host "Inicielo manualmente desde una nueva terminal: ollama serve" -ForegroundColor White
            exit 1
        }
    }
}

function Resolve-ModelDir {
    param([string]$Dir)
    
    # Resolver ruta relativa a absoluta
    if (-not [System.IO.Path]::IsPathRooted($Dir)) {
        $Dir = Join-Path (Get-Location) $Dir
    }
    $Dir = (Resolve-Path $Dir -ErrorAction SilentlyContinue).Path
    if (-not $Dir) {
        Write-Host "[ERROR] Directorio no encontrado: $Dir" -ForegroundColor Red
        exit 1
    }
    return $Dir
}

function Test-ModelFiles {
    param([string]$Dir)
    
    Write-Host "[CHECK] Verificando archivos del modelo..." -ForegroundColor Yellow
    
    $global:GGUF_FILE = Join-Path $Dir "cajal-${Quant}.gguf"
    $global:MODELFILE_PATH = Join-Path $Dir "Modelfile"
    
    if (-not (Test-Path $GGUF_FILE)) {
        Write-Host "[ERROR] No se encontro el archivo GGUF: $GGUF_FILE" -ForegroundColor Red
        Write-Host "Asegurese de haber ejecutado export_to_gguf.py primero:" -ForegroundColor White
        Write-Host "  python export_to_gguf.py --model .\model --params 14 --output $Dir"
        exit 1
    }
    
    $size = (Get-Item $GGUF_FILE).Length / 1GB
    Write-Host "[OK] GGUF encontrado: $(Split-Path $GGUF_FILE -Leaf) ($([math]::Round($size, 2)) GB)" -ForegroundColor Green
    
    if (-not (Test-Path $MODELFILE_PATH)) {
        Write-Host "[WARN] Modelfile no encontrado. Generando uno nuevo..." -ForegroundColor Yellow
        Generate-Modelfile -Path $MODELFILE_PATH
    }
    else {
        Write-Host "[OK] Modelfile encontrado: $MODELFILE_PATH" -ForegroundColor Green
    }
}

function Generate-Modelfile {
    param([string]$Path)
    
    $content = @"
# CAJAL Modelfile
# Generado automaticamente por setup_ollama.ps1

FROM ./cajal-${Quant}.gguf

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER repeat_penalty 1.15
PARAMETER num_ctx 32768
PARAMETER num_gpu 999

SYSTEM """
You are CAJAL, a Silicon agent in the P2PCLAW network, specialized in peer-to-peer networks, distributed systems, game theory, mechanism design, and legal-tech intersections. Named in honor of Santiago Ramón y Cajal. You provide rigorous, well-cited research assistance, generate LaTeX-formatted paper drafts, perform mathematical derivations, and analyze protocol incentives with formal precision. Always think step-by-step and cite sources when possible.
"""

# Parametros adicionales para Qwen3 thinking mode
PARAMETER stop </thinking>
PARAMETER stop <|endoftext|>
"@
    
    $content | Out-File -FilePath $Path -Encoding utf8
    Write-Host "[OK] Modelfile generado: $Path" -ForegroundColor Green
}

function New-OllamaModel {
    Write-Banner -Text "CREANDO MODELO EN OLLAMA"
    
    Write-Host "[INFO] Cambiando a directorio del modelo: $MODEL_DIR" -ForegroundColor White
    Push-Location $MODEL_DIR
    
    try {
        Write-Host "[INFO] Creando modelo '${MODEL_NAME}'..." -ForegroundColor White
        ollama create $MODEL_NAME -f Modelfile
        Write-Host "[OK] Modelo '${MODEL_NAME}' creado exitosamente." -ForegroundColor Green
    }
    finally {
        Pop-Location
    }
}

function Test-ModelExists {
    Write-Host "[VERIFY] Verificando que el modelo existe..." -ForegroundColor Yellow
    
    $models = ollama list | Select-String $MODEL_NAME
    if ($models) {
        Write-Host "[OK] Modelo confirmado en Ollama." -ForegroundColor Green
    }
    else {
        Write-Host "[ERROR] El modelo no aparece en 'ollama list'." -ForegroundColor Red
        exit 1
    }
}

function Show-ApiInfo {
    Write-Banner -Text "API REST INFORMACION"
    
    Write-Host "El modelo tambien esta disponible via API REST de Ollama:"
    Write-Host ""
    Write-Host "  # Generacion simple" -ForegroundColor White
    Write-Host "  Invoke-RestMethod -Uri http://localhost:11434/api/generate -Method Post -Body (@{" -ForegroundColor DarkGray
    Write-Host "    model = '${MODEL_NAME}'" -ForegroundColor DarkGray
    Write-Host "    prompt = 'Explain Sybil attacks in P2P networks'" -ForegroundColor DarkGray
    Write-Host "    stream = `$false" -ForegroundColor DarkGray
    Write-Host "    options = @{ temperature = 0.7; num_ctx = 32768 }" -ForegroundColor DarkGray
    Write-Host "  } | ConvertTo-Json) -ContentType 'application/json'" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  # Chat completions" -ForegroundColor White
    Write-Host "  Invoke-RestMethod -Uri http://localhost:11434/api/chat -Method Post -Body (@{" -ForegroundColor DarkGray
    Write-Host "    model = '${MODEL_NAME}'" -ForegroundColor DarkGray
    Write-Host "    messages = @(" -ForegroundColor DarkGray
    Write-Host "      @{ role = 'system'; content = 'You are CAJAL.' }" -ForegroundColor DarkGray
    Write-Host "      @{ role = 'user'; content = 'Analyze incentive compatibility in BitTorrent.' }" -ForegroundColor DarkGray
    Write-Host "    )" -ForegroundColor DarkGray
    Write-Host "    stream = `$false" -ForegroundColor DarkGray
    Write-Host "  } | ConvertTo-Json) -ContentType 'application/json'" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "Documentacion: https://github.com/ollama/ollama/blob/main/docs/api.md" -ForegroundColor DarkGray
    Write-Host ""
}

function Start-InteractiveMode {
    Write-Banner -Text "EJECUTANDO CAJAL"
    
    Write-Host "Comandos disponibles:" -ForegroundColor White
    Write-Host "  ollama run ${MODEL_NAME}          # Modo interactivo" -ForegroundColor DarkGray
    Write-Host "  ollama run ${MODEL_NAME} --verbose  # Con estadisticas" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "Iniciando modo interactivo..." -ForegroundColor Green
    Write-Host "(Escriba /bye para salir)" -ForegroundColor DarkGray
    Write-Host ""
    
    ollama run $MODEL_NAME
}

# =============================================================================
# Main
# =============================================================================

Write-Banner -Text "CAJAL + OLLAMA SETUP (Windows)"

Write-Host "[CONFIG]" -ForegroundColor White
Write-Host "  Directorio modelo: $ModelDir" -ForegroundColor DarkGray
Write-Host "  Cuantizacion:      $Quant" -ForegroundColor DarkGray
Write-Host "  Nombre modelo:     $MODEL_NAME" -ForegroundColor DarkGray
Write-Host ""

# Resolver ruta
$global:MODEL_DIR = Resolve-ModelDir -Dir $ModelDir

# Ejecutar checks
Test-OllamaInstalled
Test-OllamaRunning
Test-ModelFiles -Dir $MODEL_DIR

# Crear y verificar modelo
New-OllamaModel
Test-ModelExists

# Mostrar info API
Show-ApiInfo

# Iniciar modo interactivo
Start-InteractiveMode
