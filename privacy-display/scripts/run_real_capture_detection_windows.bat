@echo off
setlocal

cd /d "%~dp0\.."

if exist ".venv\Scripts\python.exe" (
  set "PY=.venv\Scripts\python.exe"
) else (
  set "PY=python"
)

if "%~1"=="calibrate-roi" (
  shift
  rem ROI must rectify to the display canvas: output size = display resolution.
  "%PY%" experiments\real_capture_calibrate.py --select-roi --backend dshow --output-width 2560 --output-height 1600 %*
  exit /b %ERRORLEVEL%
)

if "%~1"=="calibrate-exposure" (
  shift
  "%PY%" experiments\real_capture_calibrate.py --calibrate-exposure --backend dshow --scene mask_only %*
  exit /b %ERRORLEVEL%
)

if "%~1"=="coco" (
  shift
  "%PY%" experiments\real_capture_detection.py --backend dshow --device cuda:0 %*
  exit /b %ERRORLEVEL%
)

if "%~1"=="mot" (
  shift
  "%PY%" experiments\real_capture_mot.py --backend dshow --device cuda:0 %*
  exit /b %ERRORLEVEL%
)

if "%~1"=="dry-run" (
  shift
  "%PY%" experiments\real_capture_detection.py --dry-run --max-images 5 %*
  "%PY%" experiments\real_capture_mot.py --dry-run --max-frames 20 %*
  exit /b %ERRORLEVEL%
)

echo Real-device capture for COCO/MOT detection + tracking (Windows 240Hz).
echo Steps:
echo   1) scripts\run_real_capture_detection_windows.bat calibrate-roi --pos d0.5_a0
echo   2) scripts\run_real_capture_detection_windows.bat calibrate-exposure --image data\coco\val2017\000000000139.jpg
echo   3) scripts\run_real_capture_detection_windows.bat coco --max-images 150
echo   4) scripts\run_real_capture_detection_windows.bat mot --sequence MOT17-09-FRCNN --max-frames 450
echo   (preview plans only: scripts\run_real_capture_detection_windows.bat dry-run)
