@echo off
setlocal enableextensions

REM Daily panel Autoformer export (ratio split 70/15/15) - daily_retrained_0505
REM Run after training, from repo root:
REM   cd /d "E:\Urban Computing Final Project\Try_0412"
REM   daily_retrained_0505\RUN_EXPORT_DAILY_RATIO_TEST_2025_0505.cmd

set "REPO_ROOT=E:\Urban Computing Final Project\Try_0412"
set "PY=%REPO_ROOT%\.venv\Scripts\python.exe"
REM Same Autoformer checkout path as weekly_retrained_0505 CMDs
set "AUTOFORMER_ROOT=E:\Urban Computing Final Project\autoformer_spatial_0425\Autoformer"

cd /d "%REPO_ROOT%"

REM Change stamp to any string (used in dated output filenames)
set "STAMP=output_daily_0505_v1"

echo Repo root:       "%REPO_ROOT%"
echo Python:          "%PY%"
echo Autoformer root: "%AUTOFORMER_ROOT%"
echo Stamp:           "%STAMP%"
echo.

"%PY%" "%REPO_ROOT%\daily_training_0430\export_panel_predictions.py" ^
  --autoformer-root "%AUTOFORMER_ROOT%" ^
  --checkpoints-dir "daily_retrained_0505\checkpoints" ^
  --out-dir "daily_retrained_0505\outputs" ^
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
  --target-transform log1p ^
  --target-start "2025-10-01" ^
  --target-end "2025-10-31" ^
  --scope test ^
  --target-year 2025 ^
  --d-model 192 ^
  --n-heads 8 ^
  --e-layers 2 ^
  --d-layers 1 ^
  --d-ff 768 ^
  --dropout 0.08 ^
  --moving-avg 7 ^
  --stamp "%STAMP%"

endlocal
