param(
    [string]$CacheDir = "",
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
if (-not $CacheDir) {
    $CacheDir = Join-Path $projectRoot ".cache\surya"
}
$CacheDir = [IO.Path]::GetFullPath($CacheDir)
$systemCurl = Join-Path $env:SystemRoot "System32\curl.exe"
if (Test-Path -LiteralPath $systemCurl -PathType Leaf) {
    $curlExe = $systemCurl
} else {
    $curlExe = (
        Get-Command curl.exe -All -CommandType Application -ErrorAction Stop |
            Select-Object -First 1
    ).Source
}
Write-Host "Using curl: $curlExe"

$models = @(
    "text_recognition/2025_05_16",
    "text_detection/2025_05_07"
)
$baseUrl = "https://models.datalab.to"

function Test-ModelComplete {
    param([Parameter(Mandatory = $true)][string]$ModelDir)

    $manifestPath = Join-Path $ModelDir "manifest.json"
    $markerPath = Join-Path $ModelDir ".complete"
    if (
        -not (Test-Path -LiteralPath $manifestPath -PathType Leaf) -or
        -not (Test-Path -LiteralPath $markerPath -PathType Leaf)
    ) {
        return $false
    }

    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    foreach ($file in $manifest.files) {
        if (-not (Test-Path -LiteralPath (Join-Path $ModelDir $file) -PathType Leaf)) {
            return $false
        }
    }
    return $true
}

function Invoke-Download {
    param(
        [Parameter(Mandatory = $true)][string]$Url,
        [Parameter(Mandatory = $true)][string]$Output,
        [switch]$Resume
    )

    $args = @(
        "--fail",
        "--location",
        "--show-error",
        "--retry", "20",
        "--retry-all-errors",
        "--retry-delay", "5",
        "--connect-timeout", "30"
    )
    if ($Resume) {
        $args += @("--continue-at", "-")
    }
    $args += @("--output", $Output, $Url)

    & $curlExe @args
    if ($LASTEXITCODE -ne 0) {
        throw "Download failed: $Url"
    }
}

foreach ($model in $models) {
    $modelDir = Join-Path $CacheDir ($model -replace "/", [IO.Path]::DirectorySeparatorChar)
    if (Test-ModelComplete -ModelDir $modelDir) {
        Write-Host "Surya model already complete: $model"
        continue
    }

    Write-Host "Downloading Surya model with resume support: $model"
    if ($DryRun) {
        Write-Host "DRY RUN: $baseUrl/$model/manifest.json -> $modelDir"
        continue
    }

    New-Item -ItemType Directory -Force -Path $modelDir | Out-Null
    $manifestPath = Join-Path $modelDir "manifest.json"
    $manifestTemp = "$manifestPath.part"
    Invoke-Download -Url "$baseUrl/$model/manifest.json" -Output $manifestTemp
    Move-Item -LiteralPath $manifestTemp -Destination $manifestPath -Force

    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    foreach ($file in $manifest.files) {
        $target = Join-Path $modelDir $file
        if (Test-Path -LiteralPath $target -PathType Leaf) {
            Write-Host "  Cached: $file"
            continue
        }

        $parent = Split-Path -Parent $target
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
        $partial = "$target.part"
        Write-Host "  Downloading: $file"
        Invoke-Download `
            -Url "$baseUrl/$model/$file" `
            -Output $partial `
            -Resume
        Move-Item -LiteralPath $partial -Destination $target -Force
    }

    [IO.File]::WriteAllText(
        (Join-Path $modelDir ".complete"),
        "surya-ocr 0.14.7`n",
        [Text.UTF8Encoding]::new($false)
    )
    Write-Host "Surya model download complete: $model"
}

Write-Host "Surya model cache is ready: $CacheDir"
