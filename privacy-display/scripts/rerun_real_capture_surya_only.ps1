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
    [double]$OcrTimeout = 30,
    [ValidateSet("auto", "cpu", "cuda", "mps")]
    [string]$Device = "auto",
    [switch]$SkipDependencyCheck,
    [switch]$SkipModelDownload,
    [switch]$NoProgress,
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$allReportJobs = @(
    "d0.5_a0",
    "d0.5_a15",
    "d0.5_a30",
    "d1_a0",
    "d1_a15",
    "d1_a30",
    "d1.5_a0",
    "d1.5_a15",
    "d1.5_a30"
)

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $projectRoot

$pythonExe = Join-Path $projectRoot ".venv-surya\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $pythonExe -PathType Leaf)) {
    throw "Surya environment not found. Run .\scripts\setup_surya_ocr_env.ps1 first."
}

$env:SURYA_DEVICE = $Device
if (-not $env:HF_HOME) {
    $env:HF_HOME = Join-Path $projectRoot ".cache\huggingface"
}
if (-not $env:MODEL_CACHE_DIR) {
    $env:MODEL_CACHE_DIR = Join-Path $projectRoot ".cache\surya"
}
if (-not $env:PARALLEL_DOWNLOAD_WORKERS) {
    $env:PARALLEL_DOWNLOAD_WORKERS = "1"
}
New-Item -ItemType Directory -Force -Path $env:HF_HOME | Out-Null
New-Item -ItemType Directory -Force -Path $env:MODEL_CACHE_DIR | Out-Null

function Test-SuryaDependency {
    $code = @'
from importlib.metadata import version

import torch
from surya.detection import DetectionPredictor
from surya.recognition import RecognitionPredictor

from src.attack.ocr_evaluator import OCREvaluator

surya_version = version("surya-ocr")
if surya_version != "0.14.7":
    raise RuntimeError(
        f"Expected surya-ocr 0.14.7, found {surya_version}. "
        "Surya 0.20+ uses a different server-based API."
    )

device = OCREvaluator._resolve_surya_device()
if device == "cuda" and not torch.cuda.is_available():
    raise RuntimeError("SURYA_DEVICE=cuda but CUDA is not available in this environment")

print(f"Surya dependency check passed: surya-ocr={surya_version}")
print(f"PyTorch={torch.__version__} requested_device={device}")
if torch.cuda.is_available():
    print(f"CUDA GPU: {torch.cuda.get_device_name(0)}")
'@

    $code | & $pythonExe -
    if ($LASTEXITCODE -ne 0) {
        throw "Surya dependency check failed. Run .\scripts\setup_surya_ocr_env.ps1."
    }
}

if (-not $DryRun -and -not $SkipDependencyCheck) {
    Test-SuryaDependency
}
if (-not $DryRun -and -not $SkipModelDownload) {
    & (Join-Path $PSScriptRoot "download_surya_models.ps1") `
        -CacheDir $env:MODEL_CACHE_DIR
    if ($LASTEXITCODE -ne 0) {
        throw "Surya model download failed."
    }
}

$tempRoot = Join-Path $projectRoot "experiments\.surya_rerun"
New-Item -ItemType Directory -Force -Path $tempRoot | Out-Null

Write-Host "Real-capture Surya replacement mode"
Write-Host "Existing Tesseract/EasyOCR rows are preserved."
Write-Host "Existing PaddleOCR/Surya rows are removed and replaced by new Surya rows."
Write-Host "Python: $pythonExe"
Write-Host "Surya device: $Device"
Write-Host "Surya model cache: $env:MODEL_CACHE_DIR"
Write-Host "Model download workers: $env:PARALLEL_DOWNLOAD_WORKERS"
Write-Host "The first row may take several minutes while Surya loads its models."

foreach ($job in $Jobs) {
    $captureDir = "experiments\real_captures_${job}_final"
    $outputDir = "experiments\results_${job}_final"
    $existingReport = Join-Path $projectRoot (Join-Path $outputDir "real_capture_ocr.json")
    $tempDir = Join-Path $tempRoot $job
    $suryaReport = Join-Path $tempDir "real_capture_ocr.json"

    if (-not (Test-Path -LiteralPath $existingReport -PathType Leaf)) {
        throw "Existing OCR report not found: $existingReport"
    }

    Write-Host "Running Surya OCR for $job ..."
    $args = @(
        "experiments\real_capture_analysis.py",
        "--capture-dir", $captureDir,
        "--metadata", "metadata.json",
        "--output-dir", $tempDir,
        "--engines", "surya",
        "--ocr-timeout", "$OcrTimeout"
    )
    if (-not $NoProgress) {
        $args += "--progress"
    }

    if ($DryRun) {
        Write-Host ("DRY RUN: $pythonExe " + ($args -join " "))
        Write-Host "DRY RUN: replace PaddleOCR/Surya rows in $existingReport"
        continue
    }

    & $pythonExe @args
    if ($LASTEXITCODE -ne 0) {
        throw "Surya OCR rerun failed for $job"
    }
    if (-not (Test-Path -LiteralPath $suryaReport -PathType Leaf)) {
        throw "Surya OCR rerun did not produce report: $suryaReport"
    }

    & $pythonExe "experiments\merge_real_capture_surya.py" replace `
        --existing $existingReport `
        --replacement $suryaReport
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to merge Surya rows into $existingReport"
    }
}

if (-not $DryRun) {
    $reportPaths = @(
        $allReportJobs | ForEach-Object {
            "experiments\results_${_}_final\real_capture_ocr.json"
        }
    )
    & $pythonExe "experiments\merge_real_capture_surya.py" aggregate `
        --reports @reportPaths `
        --output-dir "experiments\results" `
        --ocr-timeout "$OcrTimeout"
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to aggregate complete Surya position reports."
    }
}
