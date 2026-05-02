<#
.SYNOPSIS
    Script de búsqueda de datasets para el proyecto P2PCLAW en disco local Windows.

.DESCRIPTION
    Recorre recursivamente E:\OpenCLAW-4 buscando archivos .json, .jsonl, .zip y
    archivos con nombres clave (dataset*, papers*, train*, export*). Genera un
    reporte con tamaños, fechas, rutas y recomendaciones para cada hallazgo.

.USAGE
    .\find_p2pclaw_dataset.ps1

.NOTAS
    Autor: P2PCLAW Dataset Agent
    Requiere: PowerShell 5.1+ o PowerShell Core 7.x
    Ejecutar desde cualquier ubicacin con permisos de lectura en E:\OpenCLAW-4.
#>

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURACIN
# ──────────────────────────────────────────────────────────────────────────────

$BasePath       = "E:\OpenCLAW-4"
$LargeFileThreshold = 1MB   # 1 MB = 1048576 bytes
$Extensions     = @("*.json", "*.jsonl", "*.zip")
$KeyNamePatterns = @("dataset*", "papers*", "train*", "export*")

# Colores para consola (fallback seguro para Windows PowerShell y PowerShell Core)
function Write-ColorLine {
    param(
        [string]$Text,
        [string]$ForegroundColor = "White"
    )
    $supported = [enum]::GetValues([System.ConsoleColor])
    if ($supported -contains $ForegroundColor) {
        Write-Host $Text -ForegroundColor $ForegroundColor
    } else {
        Write-Host $Text
    }
}

# ──────────────────────────────────────────────────────────────────────────────
# BANNER
# ──────────────────────────────────────────────────────────────────────────────

$banner = @"
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║            P2PCLAW  -  BSQUEDA DE DATASETS EN DISCO LOCAL                   ║
║                                                                              ║
║   Repositorio servidor:  https://github.com/Agnuxo1/p2pclaw-mcp-server      ║
║   Repositorio frontend:  https://github.com/Agnuxo1/OpenCLAW-P2P              ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"@

Write-Host $banner
Write-Host ""
Write-ColorLine "Ruta base analizada: $BasePath" "Cyan"
Write-ColorLine "Inicio de escaneo:   $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" "Cyan"
Write-Host ""

# ──────────────────────────────────────────────────────────────────────────────
# VALIDACIN DE RUTA BASE
# ──────────────────────────────────────────────────────────────────────────────

if (-not (Test-Path -Path $BasePath)) {
    Write-ColorLine "[ERROR] No existe la ruta base: $BasePath" "Red"
    Write-ColorLine "Verifique que el proyecto P2PCLAW est en E:\OpenCLAW-4" "Yellow"
    exit 1
}

# ──────────────────────────────────────────────────────────────────────────────
# ESTRUCTURA ESPERADA (diagnstico rpido)
# ──────────────────────────────────────────────────────────────────────────────

Write-ColorLine "═══════════════════════════════════════════════════════════════════════════════" "Yellow"
Write-ColorLine " 1. VERIFICACIN DE ESTRUCTURA ESPERADA" "Yellow"
Write-ColorLine "═══════════════════════════════════════════════════════════════════════════════" "Yellow"

$expectedFolders = @(
    "p2pclaw-mcp-server",
    "p2pclaw-mcp-server\radata",
    "p2pclaw-mcp-server\backups",
    "p2pclaw-mcp-server\public\backups",
    "p2pclaw-mcp-server\scripts",
    "OpenCLAW-P2P",
    "OpenCLAW-P2P\src"
)

foreach ($folder in $expectedFolders) {
    $fullPath = Join-Path $BasePath $folder
    if (Test-Path -Path $fullPath) {
        Write-ColorLine "   [OK]    $folder" "Green"
    } else {
        Write-ColorLine "   [FALTA] $folder  <-- no encontrado" "Red"
    }
}

Write-Host ""

# ──────────────────────────────────────────────────────────────────────────────
# BSQUEDA DE ARCHIVOS POR EXTENSIN (.json, .jsonl, .zip)
# ──────────────────────────────────────────────────────────────────────────────

Write-ColorLine "═══════════════════════════════════════════════════════════════════════════════" "Yellow"
Write-ColorLine " 2. BSQUEDA RECURSIVA DE ARCHIVOS JSON / JSONL / ZIP" "Yellow"
Write-ColorLine "═══════════════════════════════════════════════════════════════════════════════" "Yellow"

$foundByExtension = @()
$searchErrors     = @()

foreach ($ext in $Extensions) {
    try {
        Write-ColorLine "   Escaneando extensin: $ext ..." "Gray"
        $items = Get-ChildItem -Path $BasePath -Filter $ext -Recurse -File -ErrorAction SilentlyContinue
        $foundByExtension += $items
    } catch {
        $searchErrors += "Error buscando $ext : $_"
    }
}

if ($foundByExtension.Count -eq 0) {
    Write-ColorLine "   No se encontraron archivos .json, .jsonl o .zip en $BasePath" "Red"
} else {
    Write-ColorLine "   Total encontrados: $($foundByExtension.Count) archivos" "Green"
    Write-Host ""

    # Ordenar por tamao descendente
    $sorted = $foundByExtension | Sort-Object Length -Descending

    foreach ($file in $sorted) {
        $sizeFormatted = if ($file.Length -ge 1MB) {
            "{0:N2} MB" -f ($file.Length / 1MB)
        } elseif ($file.Length -ge 1KB) {
            "{0:N2} KB" -f ($file.Length / 1KB)
        } else {
            "$($file.Length) B"
        }

        $isLarge = $file.Length -gt $LargeFileThreshold
        $color   = if ($isLarge) { "Magenta" } else { "White" }
        $marker  = if ($isLarge) { " [>>> DATASET CANDIDATO <<<]" } else { "" }

        $relativePath = $file.FullName.Replace($BasePath, "E:\\OpenCLAW-4")
        Write-ColorLine "   [$sizeFormatted]  $($file.LastWriteTime.ToString('yyyy-MM-dd HH:mm'))  $relativePath$marker" $color
    }
}

if ($searchErrors.Count -gt 0) {
    Write-Host ""
    Write-ColorLine "   Errores durante el escaneo:" "Red"
    $searchErrors | ForEach-Object { Write-ColorLine "      $_" "Red" }
}

Write-Host ""

# ──────────────────────────────────────────────────────────────────────────────
# BSQUEDA DE ARCHIVOS POR NOMBRE CLAVE
# ──────────────────────────────────────────────────────────────────────────────

Write-ColorLine "═══════════════════════════════════════════════════════════════════════════════" "Yellow"
Write-ColorLine " 3. BSQUEDA DE ARCHIVOS POR NOMBRE CLAVE (dataset*, papers*, train*, export*)" "Yellow"
Write-ColorLine "═══════════════════════════════════════════════════════════════════════════════" "Yellow"

$foundByName = @()

foreach ($pattern in $KeyNamePatterns) {
    try {
        Write-ColorLine "   Patrn: $pattern ..." "Gray"
        $items = Get-ChildItem -Path $BasePath -Filter "$pattern*" -Recurse -File -ErrorAction SilentlyContinue
        $foundByName += $items
    } catch {
        Write-ColorLine "   Error buscando $pattern : $_" "Red"
    }
}

# Eliminar duplicados (archivos ya listados por extensin)
$uniqueByName = $foundByName | Where-Object {
    $path = $_.FullName
    $foundByExtension.FullName -notcontains $path
}

if ($uniqueByName.Count -eq 0) {
    Write-ColorLine "   No se encontraron archivos adicionales con nombres clave." "Yellow"
} else {
    Write-ColorLine "   Archivos adicionales encontrados: $($uniqueByName.Count)" "Green"
    Write-Host ""
    foreach ($file in ($uniqueByName | Sort-Object Length -Descending)) {
        $sizeFormatted = if ($file.Length -ge 1MB) {
            "{0:N2} MB" -f ($file.Length / 1MB)
        } elseif ($file.Length -ge 1KB) {
            "{0:N2} KB" -f ($file.Length / 1KB)
        } else {
            "$($file.Length) B"
        }
        $relativePath = $file.FullName.Replace($BasePath, "E:\\OpenCLAW-4")
        Write-ColorLine "   [$sizeFormatted]  $($file.LastWriteTime.ToString('yyyy-MM-dd HH:mm'))  $relativePath" "Green"
    }
}

Write-Host ""

# ──────────────────────────────────────────────────────────────────────────────
# ANLISIS ESPECFICO DE CARPETAS CLAVE: radata, backups, public\backups
# ──────────────────────────────────────────────────────────────────────────────

Write-ColorLine "═══════════════════════════════════════════════════════════════════════════════" "Yellow"
Write-ColorLine " 4. ANLISIS DE CARPETAS CLAVE (radata, backups, public\backups)" "Yellow"
Write-ColorLine "═══════════════════════════════════════════════════════════════════════════════" "Yellow"

$carpetasClave = @(
    "$BasePath\p2pclaw-mcp-server\radata",
    "$BasePath\p2pclaw-mcp-server\backups",
    "$BasePath\p2pclaw-mcp-server\public\backups"
)

foreach ($folder in $carpetasClave) {
    $folderLabel = $folder.Replace($BasePath, "E:\\OpenCLAW-4")
    Write-Host ""
    Write-ColorLine "   >>> Carpeta: $folderLabel" "Cyan"

    if (-not (Test-Path -Path $folder)) {
        Write-ColorLine "       [No existe o no es accesible]" "Red"
        continue
    }

    try {
        $allFiles = Get-ChildItem -Path $folder -Recurse -File -ErrorAction SilentlyContinue
        $fileCount = $allFiles.Count
        $totalSize = ($allFiles | Measure-Object -Property Length -Sum).Sum

        if ($fileCount -eq 0) {
            Write-ColorLine "       [Vaca] No hay archivos en esta carpeta." "Yellow"
            continue
        }

        $sizeFormatted = if ($totalSize -ge 1MB) {
            "{0:N2} MB" -f ($totalSize / 1MB)
        } elseif ($totalSize -ge 1KB) {
            "{0:N2} KB" -f ($totalSize / 1KB)
        } else {
            "$totalSize B"
        }

        Write-ColorLine "       Total: $fileCount archivos | Tamao acumulado: $sizeFormatted" "Green"

        # Detalle de archivos grandes
        $largeFiles = $allFiles | Where-Object { $_.Length -gt $LargeFileThreshold } | Sort-Object Length -Descending
        if ($largeFiles) {
            Write-ColorLine "       Archivos grandes (>1MB):" "Magenta"
            foreach ($lf in $largeFiles) {
                $lfSize = if ($lf.Length -ge 1MB) {
                    "{0:N2} MB" -f ($lf.Length / 1MB)
                } elseif ($lf.Length -ge 1KB) {
                    "{0:N2} KB" -f ($lf.Length / 1KB)
                } else {
                    "$($lf.Length) B"
                }
                $relPath = $lf.FullName.Replace($BasePath, "E:\\OpenCLAW-4")
                Write-ColorLine "         - $lfSize  |  $relPath" "Magenta"
            }
        }

        # Detalle de archivos ZIP especfico
        $zipFiles = $allFiles | Where-Object { $_.Extension -eq ".zip" } | Sort-Object Length -Descending
        if ($zipFiles) {
            Write-ColorLine "       Archivos ZIP encontrados:" "Yellow"
            foreach ($zf in $zipFiles) {
                $zfSize = "{0:N2} MB" -f ($zf.Length / 1MB)
                $relPath = $zf.FullName.Replace($BasePath, "E:\\OpenCLAW-4")
                Write-ColorLine "         - $zfSize  |  $relPath" "Yellow"
            }
            Write-ColorLine "       >> Sugerencia: extraiga con: Expand-Archive -Path '<ruta>' -DestinationPath '<destino>'" "Yellow"
        }
    } catch {
        Write-ColorLine "       [ERROR] No se pudo analizar: $_" "Red"
    }
}

Write-Host ""

# ──────────────────────────────────────────────────────────────────────────────
# RESUMEN GLOBAL
# ──────────────────────────────────────────────────────────────────────────────

Write-ColorLine "═══════════════════════════════════════════════════════════════════════════════" "Yellow"
Write-ColorLine " 5. RESUMEN GLOBAL" "Yellow"
Write-ColorLine "═══════════════════════════════════════════════════════════════════════════════" "Yellow"

$allFilesFound = $foundByExtension + $uniqueByName | Select-Object -Property FullName, Length, LastWriteTime -Unique
$totalCount    = $allFilesFound.Count
$totalBytes    = ($allFilesFound | Measure-Object -Property Length -Sum).Sum

Write-ColorLine "   Total de archivos relevantes encontrados: $totalCount" "Cyan"

if ($totalBytes -ge 1MB) {
    Write-ColorLine "   Tamao total acumulado: {0:N2} MB" -f ($totalBytes / 1MB) "Cyan"
} else {
    Write-ColorLine "   Tamao total acumulado: {0:N2} KB" -f ($totalBytes / 1KB) "Cyan"
}

$datasetCandidates = $allFilesFound | Where-Object { $_.Length -gt $LargeFileThreshold }
if ($datasetCandidates) {
    Write-Host ""
    Write-ColorLine "   >>> CANDIDATOS A DATASET (archivos > 1 MB) <<<" "Magenta"
    foreach ($cand in ($datasetCandidates | Sort-Object Length -Descending)) {
        $relPath = $cand.FullName.Replace($BasePath, "E:\\OpenCLAW-4")
        $candSize = "{0:N2} MB" -f ($cand.Length / 1MB)
        Write-ColorLine "       - $candSize  |  $relPath" "Magenta"
    }
}

Write-Host ""

# ──────────────────────────────────────────────────────────────────────────────
# INSTRUCCIONES FINALES
# ──────────────────────────────────────────────────────────────────────────────

Write-ColorLine "═══════════════════════════════════════════════════════════════════════════════" "Yellow"
Write-ColorLine " 6.QU HACER CON LOS ARCHIVOS ENCONTRADOS?" "Yellow"
Write-ColorLine "═══════════════════════════════════════════════════════════════════════════════" "Yellow"

$instructions = @"

   [A] Archivos .json / .jsonl grandes (>1 MB)
       ------------------------------------------
       Probablemente son datasets vlidos. Verifique el contenido:
       1. Abra con VS Code o editor de texto para ver la estructura.
       2. Idealmente cada lnea debe tener: { "messages": [ { "role": "...", "content": "..." } ] }
       3. Valide con: python -c "import json; [json.loads(l) for l in open('archivo.jsonl')]"
       4. Si es vlido, copelo a su carpeta de datasets de entrenamiento.

   [B] Archivos .zip en backups/ o public\backups/
       ------------------------------------------
       Son backups comprimidos del estado Gun.js (radata/). Para extraer:

       PS> Expand-Archive -Path "E:\OpenCLAW-4\p2pclaw-mcp-server\backups\radata_backup_YYYY-MM-DD.zip" `
                           -DestinationPath "E:\OpenCLAW-4\p2pclaw-mcp-server\backups\extraido"

       Luego analice el contenido extrado buscando archivos .json con datos de papers.

   [C] Carpeta radata/ (estado Gun.js)
       ------------------------------------------
       Gun.js almacena datos localmente en formato propietario (no legible directamente).
       Usar el script backup_radata.js del repo para hacer backup ZIP,
       o usar restore_papers.mjs para recuperar papers en formato JSON.

   [D] Si no encontr nada
       ------------------------------------------
       Opciones alternativas:
       1. Ejecutar el script backup_radata.js para crear un backup ZIP actualizado.
       2. Usar el endpoint API: GET https://www.p2pclaw.com/api/dataset/export?min_score=0
       3. Ejecutar el script Python: python download_from_api.py (si lo tiene).
       4. Verificar copias en Cloudflare / Railway desde el panel de control.

"@

Write-Host $instructions

Write-ColorLine "═══════════════════════════════════════════════════════════════════════════════" "Green"
Write-ColorLine " Escaneo completado: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" "Green"
Write-ColorLine "═══════════════════════════════════════════════════════════════════════════════" "Green"

# Pausa opcional si se ejecuta haciendo doble-clic (no desde consola interactiva)
if ($Host.Name -eq 'ConsoleHost' -and -not $env:TERM) {
    Write-Host ""
    Write-ColorLine "Presione Enter para cerrar..." "Gray"
    $null = Read-Host
}
