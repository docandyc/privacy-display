@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0\.."

if exist ".venv\Scripts\python.exe" (
  set "PY=.venv\Scripts\python.exe"
) else (
  set "PY=python"
)

rem First token is the sub-command; everything after it is forwarded verbatim.
rem NOTE: %* ignores SHIFT in batch, so collect the remaining args explicitly.
set "CMD=%~1"
if not "%CMD%"=="" shift

set "ARGS="
:collect
if "%~1"=="" goto run
set "ARGS=!ARGS! %1"
shift
goto collect
:run

if "%CMD%"=="dry-run" (
  "%PY%" experiments\real_capture_ablation.py --study all --dry-run !ARGS!
  exit /b %ERRORLEVEL%
)

if "%CMD%"=="calibrate-roi" (
  "%PY%" experiments\real_capture_calibrate.py --select-roi --backend dshow !ARGS!
  exit /b %ERRORLEVEL%
)

if "%CMD%"=="calibrate-exposure" (
  "%PY%" experiments\real_capture_calibrate.py --calibrate-exposure --backend dshow !ARGS!
  exit /b %ERRORLEVEL%
)

if "%CMD%"=="full" (
  "%PY%" experiments\real_capture_ablation.py --study all --backend dshow --analyze !ARGS!
  exit /b %ERRORLEVEL%
)

echo Running default smoke capture: study 1, original vs deployed, short exposure, one sample.
echo Use: scripts\run_real_capture_ablation_windows.bat dry-run
echo Use: scripts\run_real_capture_ablation_windows.bat calibrate-roi --pos d0.5_a0
echo Use: scripts\run_real_capture_ablation_windows.bat calibrate-exposure
echo Use: scripts\run_real_capture_ablation_windows.bat full

"%PY%" experiments\real_capture_ablation.py --study 1 --subset-size 1 --attacks short --conditions original,deployed --backend dshow --analyze !ARGS!
