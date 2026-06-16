@echo off
setlocal

cd /d "%~dp0\.."

if exist ".venv\Scripts\python.exe" (
  set "PY=.venv\Scripts\python.exe"
) else (
  set "PY=python"
)

if "%~1"=="dry-run" (
  shift
  "%PY%" experiments\real_capture_ablation.py --study all --dry-run %*
  exit /b %ERRORLEVEL%
)

if "%~1"=="calibrate-roi" (
  shift
  "%PY%" experiments\real_capture_calibrate.py --select-roi --backend dshow %*
  exit /b %ERRORLEVEL%
)

if "%~1"=="calibrate-exposure" (
  shift
  "%PY%" experiments\real_capture_calibrate.py --calibrate-exposure --backend dshow %*
  exit /b %ERRORLEVEL%
)

if "%~1"=="full" (
  shift
  "%PY%" experiments\real_capture_ablation.py --study all --backend dshow --analyze %*
  exit /b %ERRORLEVEL%
)

echo Running default smoke capture: study 1, original vs deployed, short exposure, one sample.
echo Use: scripts\run_real_capture_ablation_windows.bat dry-run
echo Use: scripts\run_real_capture_ablation_windows.bat calibrate-roi --pos d0.5_a0
echo Use: scripts\run_real_capture_ablation_windows.bat calibrate-exposure
echo Use: scripts\run_real_capture_ablation_windows.bat full

"%PY%" experiments\real_capture_ablation.py --study 1 --subset-size 1 --attacks short --conditions original,deployed --backend dshow --analyze %*
