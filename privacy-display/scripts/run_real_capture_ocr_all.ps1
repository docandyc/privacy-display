param(
    [string[]]$Jobs = @(
        "d0.5_a0",
        "d0.5_a15",
        "d0.5_a30",
        "d1_a0",
        "d1_a15",
        "d1_a30",
        "d1.5_a0",
        "d1.5_a15",
        "d1.5_a30"
    ),
    [string]$TesseractPath = "D:\Program Files\Tesseract-OCR\tesseract.exe",
    [string]$Engines = "tesseract",
    [string]$PythonExe = "",
    [double]$OcrTimeout = 30,
    [switch]$Force,
    [switch]$SkipLangCheck,
    [switch]$NoProgress,
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $projectRoot

if (-not $PythonExe) {
    $projectPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
    if (Test-Path -LiteralPath $projectPython -PathType Leaf) {
        $PythonExe = $projectPython
    } else {
        $PythonExe = (Get-Command python -CommandType Application -ErrorAction Stop).Source
    }
}

function Add-ToPathOnce {
    param([Parameter(Mandatory = $true)][string]$Directory)
    $parts = $env:PATH -split [IO.Path]::PathSeparator
    if ($parts -notcontains $Directory) {
        $env:PATH = "$Directory$([IO.Path]::PathSeparator)$env:PATH"
    }
}

function Test-Tesseract {
    param(
        [Parameter(Mandatory = $true)][string]$Exe,
        [switch]$SkipLanguages
    )

    if (-not (Test-Path -LiteralPath $Exe -PathType Leaf)) {
        throw "Tesseract executable not found: $Exe"
    }

    $tesseractDir = Split-Path -Parent $Exe
    $env:TESSERACT_CMD = $Exe
    $env:TESSERACT_EXE = $Exe
    Add-ToPathOnce -Directory $tesseractDir

    Write-Host "Using Tesseract: $Exe"
    & $Exe --version | Select-Object -First 1

    if (-not $SkipLanguages) {
        $langs = & $Exe --list-langs 2>$null
        foreach ($lang in @("eng", "chi_sim")) {
            if ($langs -notcontains $lang) {
                throw "Tesseract language '$lang' is missing. Install it or rerun with -SkipLangCheck if you intentionally want to continue."
            }
        }
        Write-Host "Tesseract language check passed: eng, chi_sim"
    }
}

if (-not $DryRun) {
    Test-Tesseract -Exe $TesseractPath -SkipLanguages:$SkipLangCheck
}

$jobIndex = 0
foreach ($job in $Jobs) {
    $jobIndex += 1
    $captureDir = "experiments\real_captures_${job}_final"
    $outputDir = "experiments\results_${job}_final"
    $resultJson = Join-Path $outputDir "real_capture_ocr.json"
    $metadata = Join-Path $captureDir "metadata.json"

    if (-not $NoProgress) {
        $percent = [int]((($jobIndex - 1) / [Math]::Max($Jobs.Count, 1)) * 100)
        Write-Progress `
            -Id 1 `
            -Activity "Real capture OCR batch" `
            -Status "[$jobIndex/$($Jobs.Count)] $job" `
            -PercentComplete $percent
    }

    if (-not (Test-Path -LiteralPath $captureDir -PathType Container)) {
        throw "Capture directory not found for ${job}: $captureDir"
    }
    if (-not (Test-Path -LiteralPath $metadata -PathType Leaf)) {
        throw "Metadata file not found for ${job}: $metadata"
    }
    if ((Test-Path -LiteralPath $resultJson -PathType Leaf) -and -not $Force) {
        Write-Host "Skipping $job because $resultJson already exists. Use -Force to rerun."
        continue
    }

    Write-Host ""
    Write-Host "Running OCR for $job ..."
    Write-Host "  capture: $captureDir"
    Write-Host "  output : $outputDir"

    if ($DryRun) {
        Write-Host "  python : $PythonExe"
        continue
    }

    $pythonArgs = @(
        "experiments\real_capture_analysis.py",
        "--capture-dir", $captureDir,
        "--metadata", "metadata.json",
        "--output-dir", $outputDir,
        "--engines", $Engines,
        "--ocr-timeout", $OcrTimeout
    )
    if (-not $NoProgress) {
        $pythonArgs += "--progress"
    }

    & $PythonExe @pythonArgs

    if ($LASTEXITCODE -ne 0) {
        throw "OCR failed for $job"
    }

    if (-not $NoProgress) {
        $percent = [int](($jobIndex / [Math]::Max($Jobs.Count, 1)) * 100)
        Write-Progress `
            -Id 1 `
            -Activity "Real capture OCR batch" `
            -Status "Completed $job" `
            -PercentComplete $percent
    }
}

if (-not $NoProgress) {
    Write-Progress -Id 1 -Activity "Real capture OCR batch" -Completed
}

Write-Host ""
Write-Host "All requested real-capture OCR jobs are complete."
