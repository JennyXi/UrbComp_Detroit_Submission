@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM Daily retrain (date split), outputs under daily_retrained_0506/
REM ============================================================

set "ROOT=%~dp0"
cd /d "%ROOT%\.."

set "PY=%CD%\.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"

set "AUTOFORMER_ROOT=E:\Urban Computing Final Project\autoformer_spatial_0425\Autoformer"

set "PANEL_CSV=panel_training_0426/outputs/panel_daily_top100_2025_2025_topk2025_city_lag1_wk_is_weekend_sp_nbr8_std_lag1_log1p.csv"
set "CKPT_DIR=daily_retrained_0506/checkpoints"

REM --- Date split (target dates) ---
set "TRAIN_START=2025-07-01"
set "TRAIN_END=2025-08-30"
set "VAL_START=2025-08-31"
set "VAL_END=2025-09-30"
set "TEST_START=2025-10-01"
set "TEST_END=2025-10-30"

REM --- Model hyperparams (daily baseline) ---
set "SEQ_LEN=84"
set "LABEL_LEN=42"
set "PRED_LEN=7"
set "BATCH=20"
set "EPOCHS=60"
set "PATIENCE=18"
set "LR=2.5e-5"
set "DM=256"
set "DFF=1024"
set "DROPOUT=0.12"
set "MA=7"
set "LOSS=huber"
set "HUBER_DELTA=1.5"
set "WD=2e-4"
set "CLIP=1.0"

REM Train (explicit date split)
"%PY%" daily_training_0430/train_panel_autoformer.py ^
  --autoformer-root "%AUTOFORMER_ROOT%" ^
  --checkpoints-dir "%CKPT_DIR%" ^
  --panel-csv "%PANEL_CSV%" ^
  --freq d ^
  --split-mode date ^
  --train-start "%TRAIN_START%" --train-end "%TRAIN_END%" ^
  --val-start "%VAL_START%" --val-end "%VAL_END%" ^
  --test-start "%TEST_START%" --test-end "%TEST_END%" ^
  --seq-len %SEQ_LEN% --label-len %LABEL_LEN% --pred-len %PRED_LEN% ^
  --lr %LR% --batch-size %BATCH% --epochs %EPOCHS% ^
  --early-stop --patience %PATIENCE% ^
  --d-model %DM% --d-ff %DFF% --dropout %DROPOUT% --moving-avg %MA% ^
  --loss %LOSS% --huber-delta %HUBER_DELTA% ^
  --weight-decay %WD% --grad-clip-norm %CLIP%

endlocal

