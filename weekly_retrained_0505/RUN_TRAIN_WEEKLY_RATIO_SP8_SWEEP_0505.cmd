@echo off
setlocal enableextensions

REM Small, safe sweep on TOP of the best weekly feature set (cmp0428_sp8),
REM keeping everything else constant and changing ONE knob at a time.
REM Each run writes a metrics JSON so you can pick the lowest best_val_loss.

set "REPO_ROOT=E:\Urban Computing Final Project\Try_0412"
set "PY=%REPO_ROOT%\.venv\Scripts\python.exe"
set "AUTOFORMER_ROOT=E:\Urban Computing Final Project\autoformer_spatial_0425\Autoformer"
set "TRAIN_PY=%REPO_ROOT%\weekly_retrained_0429_ep40_noearly\train_panel_autoformer.py"

set "PANEL_CSV=panel_training_0426/outputs/panel_weekly_top100_2024_2025_cmp0428_sp8.csv"

REM Base output roots
set "CKPT_BASE=weekly_retrained_0505/checkpoints_sweep_sp8"
set "METRICS_DIR=weekly_retrained_0505/sweep_metrics_sp8"

cd /d "%REPO_ROOT%"

echo === Weekly sweep (cmp0428_sp8, ratio 70/15/15) ===
echo panel_csv: %PANEL_CSV%
echo ckpt_base: %CKPT_BASE%
echo metrics:   %METRICS_DIR%
echo.

REM ------------------------------------------------------------
REM Run A: baseline hyperparams (your weekly default)
REM ------------------------------------------------------------
"%PY%" "%TRAIN_PY%" ^
  --autoformer-root "%AUTOFORMER_ROOT%" ^
  --panel-csv "%PANEL_CSV%" ^
  --checkpoints-dir "%CKPT_BASE%/A_base" ^
  --metrics-json "%METRICS_DIR%/A_base.json" ^
  --split-mode ratio --train-ratio 0.7 --val-ratio 0.15 --test-ratio 0.15 ^
  --seq-len 24 --label-len 12 --pred-len 4 --freq w --target-transform log1p ^
  --loss huber --huber-delta 1.0 ^
  --epochs 40 --batch-size 64 ^
  --lr 1e-4 --dropout 0.05 --weight-decay 0 --grad-clip-norm 0 ^
  --d-model 128 --e-layers 2 --d-layers 1 --d-ff 512 --moving-avg 25
if errorlevel 1 exit /b %errorlevel%

REM ------------------------------------------------------------
REM Run B: slightly lower LR (often helps val stability)
REM ------------------------------------------------------------
"%PY%" "%TRAIN_PY%" ^
  --autoformer-root "%AUTOFORMER_ROOT%" ^
  --panel-csv "%PANEL_CSV%" ^
  --checkpoints-dir "%CKPT_BASE%/B_lr5e5" ^
  --metrics-json "%METRICS_DIR%/B_lr5e5.json" ^
  --split-mode ratio --train-ratio 0.7 --val-ratio 0.15 --test-ratio 0.15 ^
  --seq-len 24 --label-len 12 --pred-len 4 --freq w --target-transform log1p ^
  --loss huber --huber-delta 1.0 ^
  --epochs 40 --batch-size 64 ^
  --lr 5e-5 --dropout 0.05 --weight-decay 0 --grad-clip-norm 0 ^
  --d-model 128 --e-layers 2 --d-layers 1 --d-ff 512 --moving-avg 25
if errorlevel 1 exit /b %errorlevel%

REM ------------------------------------------------------------
REM Run C: larger model (capacity) but still reasonable
REM ------------------------------------------------------------
"%PY%" "%TRAIN_PY%" ^
  --autoformer-root "%AUTOFORMER_ROOT%" ^
  --panel-csv "%PANEL_CSV%" ^
  --checkpoints-dir "%CKPT_BASE%/C_dm192" ^
  --metrics-json "%METRICS_DIR%/C_dm192.json" ^
  --split-mode ratio --train-ratio 0.7 --val-ratio 0.15 --test-ratio 0.15 ^
  --seq-len 24 --label-len 12 --pred-len 4 --freq w --target-transform log1p ^
  --loss huber --huber-delta 1.0 ^
  --epochs 40 --batch-size 48 ^
  --lr 5e-5 --dropout 0.05 --weight-decay 0 --grad-clip-norm 0 ^
  --d-model 192 --n-heads 8 --e-layers 2 --d-layers 1 --d-ff 768 --moving-avg 25
if errorlevel 1 exit /b %errorlevel%

echo.
echo Sweep done. Check best_val_loss in:
echo   %METRICS_DIR%\A_base.json
echo   %METRICS_DIR%\B_lr5e5.json
echo   %METRICS_DIR%\C_dm192.json
endlocal

