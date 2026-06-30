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
    [double]$OcrTimeout = 30,
    [switch]$SkipLangCheck,
    [switch]$SkipDependencyCheck,
    [switch]$NoProgress,
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $projectRoot

$PythonExe = Join-Path $projectRoot ".venv-surya\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $PythonExe -PathType Leaf)) {
    throw "Surya environment not found. Run .\scripts\setup_surya_ocr_env.ps1 first."
}
if (-not $env:SURYA_DEVICE) {
    $env:SURYA_DEVICE = "auto"
}
if (-not $env:MODEL_CACHE_DIR) {
    $env:MODEL_CACHE_DIR = Join-Path $projectRoot ".cache\surya"
}
if (-not $env:PARALLEL_DOWNLOAD_WORKERS) {
    $env:PARALLEL_DOWNLOAD_WORKERS = "1"
}
New-Item -ItemType Directory -Force -Path $env:MODEL_CACHE_DIR | Out-Null

$runner = Join-Path $PSScriptRoot "run_real_capture_ocr_all.ps1"
if (-not (Test-Path -LiteralPath $runner -PathType Leaf)) {
    throw "Base OCR runner not found: $runner"
}

function Test-PythonOcrDependencies {
    $code = @'
import importlib
import sys

modules = ["easyocr", "surya"]
missing = []
for module in modules:
    try:
        importlib.import_module(module)
    except Exception as exc:
        missing.append(f"{module}: {exc}")

if missing:
    print("Missing or broken OCR Python modules:")
    for item in missing:
        print(f"  {item}")
    sys.exit(1)

print("Python OCR dependency check passed: easyocr, surya")
'@

    $code | & $PythonExe -
    if ($LASTEXITCODE -ne 0) {
        throw "EasyOCR/Surya dependency check failed. Run .\scripts\setup_surya_ocr_env.ps1."
    }
}

function Merge-RealCaptureOcrReports {
    param(
        [Parameter(Mandatory = $true)][string[]]$ReportJobs,
        [Parameter(Mandatory = $true)][double]$TimeoutSeconds
    )

    $jobsJson = "[" + (($ReportJobs | ForEach-Object { $_ | ConvertTo-Json -Compress }) -join ",") + "]"
    $code = @"
import json
from pathlib import Path

from src.evaluation.real_capture import (
    REAL_CAPTURE_JSON,
    REAL_CAPTURE_MD,
    render_real_capture_markdown,
    summarize_real_capture_rows,
)

jobs = $jobsJson
root = Path("experiments")
rows = []
positions = []
source_reports = []
engines = []

for job in jobs:
    report_path = root / f"results_{job}_final" / REAL_CAPTURE_JSON
    if not report_path.exists():
        raise FileNotFoundError(f"missing per-position OCR report: {report_path}")

    report = json.loads(report_path.read_text(encoding="utf-8"))
    report_rows = []
    for row in report.get("captures", []):
        enriched = dict(row)
        enriched.setdefault("position", job)
        report_rows.append(enriched)

    for engine in report.get("config", {}).get("engines", []):
        if engine not in engines:
            engines.append(engine)

    rows.extend(report_rows)
    source_reports.append(str(report_path))

    distance = next((row.get("distance_m") for row in report_rows if row.get("distance_m") is not None), None)
    angle = next((row.get("angle_degrees") for row in report_rows if row.get("angle_degrees") is not None), None)
    positions.append({
        "position": job,
        "distance_m": distance,
        "angle_degrees": angle,
        "n_captures": int(report.get("config", {}).get("n_captures", 0)),
        "n_rows": len(report_rows),
        "source_report": str(report_path),
    })

merged = {
    "schema_version": 1,
    "capture_dir": "multiple",
    "metadata_file": "metadata.json",
    "config": {
        "engines": engines,
        "n_positions": len(positions),
        "n_captures": sum(pos["n_captures"] for pos in positions),
        "n_rows": len(rows),
        "ocr_timeout": $TimeoutSeconds,
        "source_reports": source_reports,
    },
    "positions": positions,
    "summary": summarize_real_capture_rows(rows),
    "captures": rows,
}

out_dir = root / "results"
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / REAL_CAPTURE_JSON).write_text(
    json.dumps(merged, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
(out_dir / REAL_CAPTURE_MD).write_text(
    render_real_capture_markdown(merged),
    encoding="utf-8",
)

print(f"Merged real-capture OCR report: {out_dir / REAL_CAPTURE_JSON}")
print(f"Merged real-capture OCR markdown: {out_dir / REAL_CAPTURE_MD}")
print(f"Merged rows={len(rows)} positions={len(positions)} engines={','.join(engines)}")
"@

    $code | & $PythonExe -
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to merge per-position OCR reports into experiments\results."
    }
}

if (-not $DryRun -and -not $SkipDependencyCheck) {
    Test-PythonOcrDependencies
}
if (-not $DryRun) {
    & (Join-Path $PSScriptRoot "download_surya_models.ps1") `
        -CacheDir $env:MODEL_CACHE_DIR
    if ($LASTEXITCODE -ne 0) {
        throw "Surya model download failed."
    }
}

$runnerParams = @{
    Jobs = $Jobs
    TesseractPath = $TesseractPath
    Engines = "tesseract,easyocr,surya"
    PythonExe = $PythonExe
    OcrTimeout = $OcrTimeout
    Force = $true
}

if ($SkipLangCheck) {
    $runnerParams.SkipLangCheck = $true
}
if ($NoProgress) {
    $runnerParams.NoProgress = $true
}
if ($DryRun) {
    $runnerParams.DryRun = $true
}

Write-Host "Real-capture OCR rerun mode: overwrite existing results"
Write-Host "Engines: tesseract, easyocr, surya"
Write-Host "Python: $PythonExe"

& $runner @runnerParams

if (-not $DryRun) {
    Merge-RealCaptureOcrReports -ReportJobs $Jobs -TimeoutSeconds $OcrTimeout
}
