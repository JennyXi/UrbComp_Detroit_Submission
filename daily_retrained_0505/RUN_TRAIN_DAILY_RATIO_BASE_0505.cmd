@echo off
setlocal enableextensions

REM Daily panel Autoformer training (ratio split 70/15/15) - daily_retrained_0505
REM Run from repo root:
REM   cd /d "E:\Urban Computing Final Project\Try_0412"
REM   daily_retrained_0505\RUN_TRAIN_DAILY_RATIO_BASE_0505.cmd

set "REPO_ROOT=E:\Urban Computing Final Project\Try_0412"
set "PY=%REPO_ROOT%\.venv\Scripts\python.exe"
REM Same Autoformer checkout path as weekly_retrained_0505 CMDs
set "AUTOFORMER_ROOT=E:\Urban Computing Final Project\autoformer_spatial_0425\Autoformer"

cd /d "%REPO_ROOT%"

echo Repo root:       "%REPO_ROOT%"
echo Python:          "%PY%"
echo Autoformer root: "%AUTOFORMER_ROOT%"
echo.
echo Starting training... (first log line may take a while while epoch 1 runs)
echo.

"%PY%" "%REPO_ROOT%\daily_training_0430\train_panel_autoformer.py" ^
  --autoformer-root "%AUTOFORMER_ROOT%" ^
  --checkpoints-dir "daily_retrained_0505\checkpoints" ^
  --panel-csv "panel_training_0426\outputs\panel_daily_top100_2024_2025_topk2024_city_lag1_wk_is_weekend_sp_nbr8_std_lag1_log1p.csv" ^
  --freq d ^
  --data-start "2025-04-08" ^
  --data-end "2025-10-31" ^
  --split-mode ratio ^
  --train-ratio 0.7 ^
  --val-ratio 0.15 ^
  --test-ratio 0.15 ^
  --seq-len 84 ^
  --label-len 42 ^
  --pred-len 14 ^
  --loss huber ^
  --huber-delta 1 ^
  --lr 5e-5 ^
  --batch-size 20 ^
  --epochs 40 ^
  --early-stop ^
  --patience 12 ^
  --d-model 192 ^
  --n-heads 8 ^
  --e-layers 2 ^
  --d-layers 1 ^
  --d-ff 768 ^
  --dropout 0.08 ^
  --moving-avg 7 ^
  --weight-decay 1e-4 ^
  --grad-clip-norm 1.0 ^
  --metrics-json "daily_retrained_0505\outputs\train_metrics_base_0505.json"

endlocal
