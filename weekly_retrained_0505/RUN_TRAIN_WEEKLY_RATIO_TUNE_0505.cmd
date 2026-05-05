@echo off
setlocal enableextensions

REM A tuned weekly training run (ratio split) to reduce val loss.
REM This mirrors how you previously tuned DAILY: lower LR, add weight_decay, higher dropout, enable early-stop.

REM ====== Edit these paths if needed ======
set "REPO_ROOT=E:\Urban Computing Final Project\Try_0412"
set "PY=%REPO_ROOT%\.venv\Scripts\python.exe"
set "AUTOFORMER_ROOT=E:\Urban Computing Final Project\autoformer_spatial_0425\Autoformer"

set "TRAIN_PY=%REPO_ROOT%\weekly_retrained_0429_ep40_noearly\train_panel_autoformer.py"
set "PANEL_CSV=panel_training_0426/outputs/panel_weekly_top100_2024_2025_topk2024_city_lag1_log1p.csv"
set "CKPT_DIR=panel_training_0426/checkpoints"

cd /d "%REPO_ROOT%"

echo === Tuned weekly panel Autoformer (ratio split 70/15/15) ===
echo Goal: lower val loss with regularization + early stopping.
echo.

REM Notes:
REM - Keep weekly window: 24/12/4
REM - Keep model size: dm128 (fast + matches your baseline export)
REM - Changes vs baseline:
REM   * lr: 1e-4 -> 5e-5
REM   * dropout: 0.05 -> 0.10
REM   * weight_decay: 0 -> 1e-4
REM   * grad_clip_norm: 0 -> 1.0
REM   * early-stop on, patience 8, epochs 60
REM   * resume on (continues from existing checkpoint if present)

"%PY%" "%TRAIN_PY%" ^
  --autoformer-root "%AUTOFORMER_ROOT%" ^
  --panel-csv "%PANEL_CSV%" ^
  --checkpoints-dir "%CKPT_DIR%" ^
  --split-mode ratio --train-ratio 0.7 --val-ratio 0.15 --test-ratio 0.15 ^
  --seq-len 24 --label-len 12 --pred-len 4 --freq w --target-transform log1p ^
  --loss huber --huber-delta 1.0 ^
  --epochs 60 --early-stop --patience 8 --resume ^
  --lr 5e-5 --dropout 0.10 --weight-decay 1e-4 --grad-clip-norm 1.0 ^
  --d-model 128 --e-layers 2 --d-layers 1 --d-ff 512 --moving-avg 25

echo.
echo Done.
endlocal

