param(
    [ValidateSet("gpu", "cpu")]
    [string]$TorchVariant = "gpu"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $projectRoot

$uv = (Get-Command uv -CommandType Application -ErrorAction Stop).Source
$env:UV_HTTP_TIMEOUT = if ($env:UV_HTTP_TIMEOUT) { $env:UV_HTTP_TIMEOUT } else { "600" }
$pythonExe = Join-Path $projectRoot ".venv-surya\Scripts\python.exe"
$requirements = Join-Path $projectRoot "requirements-surya.txt"

if (-not (Test-Path -LiteralPath $pythonExe -PathType Leaf)) {
    & $uv venv ".venv-surya" --python 3.10
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create .venv-surya."
    }
}

if ($TorchVariant -eq "gpu") {
    Write-Host "Installing CUDA 12.6 PyTorch for Surya ..."
    & $uv pip install `
        --python $pythonExe `
        --index-url "https://download.pytorch.org/whl/cu126" `
        "torch==2.12.1+cu126" `
        "torchvision==0.27.1+cu126"
} else {
    Write-Host "Installing CPU PyTorch for Surya ..."
    & $uv pip install `
        --python $pythonExe `
        --index-url "https://download.pytorch.org/whl/cpu" `
        "torch==2.12.1+cpu" `
        "torchvision==0.27.1+cpu"
}
if ($LASTEXITCODE -ne 0) {
    throw "Failed to install PyTorch for Surya."
}

& $uv pip install --python $pythonExe --requirement $requirements
if ($LASTEXITCODE -ne 0) {
    throw "Failed to install Surya OCR dependencies."
}

& $pythonExe -c @'
from importlib.metadata import version

import torch
from surya.detection import DetectionPredictor
from surya.recognition import RecognitionPredictor

print(f"surya-ocr={version('surya-ocr')}")
print(f"torch={torch.__version__}")
print(f"cuda_available={torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"gpu={torch.cuda.get_device_name(0)}")
print("Surya dependency check passed.")
'@
if ($LASTEXITCODE -ne 0) {
    throw "Surya environment validation failed."
}

Write-Host "Surya OCR environment is ready: $pythonExe"
