# Windows GPU：EasyOCR 与 Surya 完整预处理网格

本文档用于在 Windows 上继续运行真实拍摄 OCR 的固定预处理攻击。固定网格包含 984 张主分析图片、6 种输入形式和 3 个 OCR 引擎；三引擎完整矩阵应有 17,712 个单元。

EasyOCR 与 Surya 共用同一个 JSONL checkpoint。必须顺序运行，不能让两个进程同时写入 checkpoint。

## 1. 更新仓库

以下 `$Repo` 指 Git 仓库根目录，即同时包含 `paper` 和内层 `privacy-display` 的目录。

```powershell
$Repo = "D:\your-path\privacy-display"

Set-Location $Repo
git checkout master
git pull origin master

Set-Location "$Repo\privacy-display"
Set-ExecutionPolicy -Scope Process Bypass
```

## 2. 准备真实拍摄图片

Git 仓库不包含真实拍摄 JPG。运行机器需要存在以下 8 个主分析目录及其 metadata 引用的图片：

```text
experiments\real_captures_d0.5_a0_final
experiments\real_captures_d0.5_a30_final
experiments\real_captures_d1_a0_final
experiments\real_captures_d1_a15_final
experiments\real_captures_d1_a30_final
experiments\real_captures_d1.5_a0_final
experiments\real_captures_d1.5_a15_final
experiments\real_captures_d1.5_a30_final
```

`d0.5_a15` 使用不同的曝光控制值，不属于当前主分析固定网格。

## 3. 建立 CUDA OCR 环境

安装 `uv` 后，使用项目脚本创建包含 CUDA PyTorch、EasyOCR 和固定版本 Surya 的环境：

```powershell
.\scripts\setup_surya_ocr_env.ps1 -TorchVariant gpu
.\scripts\download_surya_models.ps1
```

设置后续命令使用的公共变量：

```powershell
$Py = ".\.venv-surya\Scripts\python.exe"
$Checkpoint = "experiments\results\real_capture_preprocessing_rows\matrix.jsonl"
$Grid = "raw,gamma_0.5,clahe_luma,unsharp_mask,adaptive_threshold,upscale_2x"
$env:SURYA_DEVICE = "cuda"
$env:MODEL_CACHE_DIR = Join-Path (Get-Location) ".cache\surya"
```

正式运行前只检查 CUDA 是否可用，不检查具体 GPU 型号：

```powershell
& $Py -c "import torch; assert torch.cuda.is_available(), 'CUDA unavailable'; print('CUDA ready')"
if ($LASTEXITCODE -ne 0) {
    throw "CUDA preflight failed. Do not start the OCR grid on CPU."
}
```

EasyOCR 会在 `torch.cuda.is_available()` 为真时自动以 `gpu=True` 初始化；Surya 由 `SURYA_DEVICE=cuda` 固定到 CUDA。

## 4. 检查图片与 checkpoint

```powershell
& $Py experiments\real_capture_preprocessing_attack.py `
    --engines "easyocr,surya" `
    --preprocessors $Grid `
    --checkpoint $Checkpoint `
    --prepare-only
```

该命令会读取所有 metadata、检查 984 张选中图片是否存在，并打印 checkpoint 中已完成和待运行的单元。若出现 `missing selected capture image`，先补齐图片，不要开始正式计算。

## 5. 完整运行 EasyOCR GPU 网格

```powershell
& $Py experiments\real_capture_preprocessing_attack.py `
    --engines "easyocr" `
    --preprocessors $Grid `
    --checkpoint $Checkpoint `
    --json-out "experiments\results\real_capture_preprocessing_attack_easyocr.json" `
    --md-out "experiments\results\real_capture_preprocessing_attack_easyocr.md" `
    --workers 1

if ($LASTEXITCODE -ne 0) {
    throw "EasyOCR preprocessing sweep failed."
}
```

中断后重新执行同一条命令即可。每个完成单元都会立即追加并同步到 checkpoint，已完成单元不会重复运行。

完成后检查：

```powershell
$Easy = Get-Content `
    "experiments\results\real_capture_preprocessing_attack_easyocr.json" `
    -Raw | ConvertFrom-Json

$Easy.audit
$Easy.config.engines
```

目标值：

```text
matrix_row_count : 5904
ocr_error_count  : 0
engines          : easyocr
```

## 6. 完整运行 Surya GPU 网格

EasyOCR 完成后，再运行 Surya；不要并行执行两者。

```powershell
& $Py experiments\real_capture_preprocessing_attack.py `
    --engines "surya" `
    --preprocessors $Grid `
    --checkpoint $Checkpoint `
    --json-out "experiments\results\real_capture_preprocessing_attack_surya.json" `
    --md-out "experiments\results\real_capture_preprocessing_attack_surya.md" `
    --workers 1

if ($LASTEXITCODE -ne 0) {
    throw "Surya preprocessing sweep failed."
}
```

完成后检查：

```powershell
$Surya = Get-Content `
    "experiments\results\real_capture_preprocessing_attack_surya.json" `
    -Raw | ConvertFrom-Json

$Surya.audit
$Surya.config.engines
```

目标值：

```text
matrix_row_count : 5904
ocr_error_count  : 0
engines          : surya
```

## 7. 重跑失败单元

只有在修复依赖、CUDA、显存或模型问题后，才使用 `--retry-errors`。它只移除当前指定引擎的失败单元，保留其他引擎的已完成结果。

EasyOCR：

```powershell
& $Py experiments\real_capture_preprocessing_attack.py `
    --engines "easyocr" `
    --preprocessors $Grid `
    --checkpoint $Checkpoint `
    --json-out "experiments\results\real_capture_preprocessing_attack_easyocr.json" `
    --md-out "experiments\results\real_capture_preprocessing_attack_easyocr.md" `
    --workers 1 `
    --retry-errors
```

Surya：

```powershell
& $Py experiments\real_capture_preprocessing_attack.py `
    --engines "surya" `
    --preprocessors $Grid `
    --checkpoint $Checkpoint `
    --json-out "experiments\results\real_capture_preprocessing_attack_surya.json" `
    --md-out "experiments\results\real_capture_preprocessing_attack_surya.md" `
    --workers 1 `
    --retry-errors
```

## 8. 生成三引擎联合报告

EasyOCR 和 Surya 都完成后运行：

```powershell
& $Py experiments\real_capture_preprocessing_attack.py `
    --engines "tesseract,easyocr,surya" `
    --preprocessors $Grid `
    --checkpoint $Checkpoint `
    --json-out "experiments\results\real_capture_preprocessing_attack_three_engine.json" `
    --md-out "experiments\results\real_capture_preprocessing_attack_three_engine.md" `
    --workers 1
```

如果三个矩阵已经完整，这一步只读取 checkpoint 并聚合结果，不会重新运行 OCR。

```powershell
$Combined = Get-Content `
    "experiments\results\real_capture_preprocessing_attack_three_engine.json" `
    -Raw | ConvertFrom-Json

$Combined.audit
$Combined.config.engines
```

目标值：

```text
matrix_row_count : 17712
ocr_error_count  : 0
engines          : tesseract, easyocr, surya
```

## 9. 提交结果

```powershell
Set-Location $Repo

git add `
    privacy-display/experiments/results/real_capture_preprocessing_rows/matrix.jsonl `
    privacy-display/experiments/results/real_capture_preprocessing_attack_easyocr.json `
    privacy-display/experiments/results/real_capture_preprocessing_attack_easyocr.md `
    privacy-display/experiments/results/real_capture_preprocessing_attack_surya.json `
    privacy-display/experiments/results/real_capture_preprocessing_attack_surya.md `
    privacy-display/experiments/results/real_capture_preprocessing_attack_three_engine.json `
    privacy-display/experiments/results/real_capture_preprocessing_attack_three_engine.md

git commit -m "exp: complete EasyOCR and Surya preprocessing sweeps"
git push origin master
```

推送后再更新论文、结果表和 reproducibility manifest，不要手工把控制台数字复制进论文。
