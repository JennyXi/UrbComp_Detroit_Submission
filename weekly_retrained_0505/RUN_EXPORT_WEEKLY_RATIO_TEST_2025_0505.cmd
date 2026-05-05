@echo off
setlocal enableextensions

REM ====== Edit these paths if needed ======
set "REPO_ROOT=E:\Urban Computing Final Project\Try_0412"
set "PY=%REPO_ROOT%\.venv\Scripts\python.exe"
set "AUTOFORMER_ROOT=E:\Urban Computing Final Project\autoformer_spatial_0425\Autoformer"

REM Export entrypoint
set "EXPORT_PY=%REPO_ROOT%\weekly_retrained_0429_ep40_noearly\export_panel_predictions.py"

REM Weekly panel CSV (must match training features/columns)
set "PANEL_CSV=panel_training_0426/outputs/panel_weekly_top100_2024_2025_topk2024_city_lag1_log1p.csv"

REM Checkpoints directory (where your weekly checkpoint is)
set "CKPT_DIR=panel_training_0426/checkpoints"

REM ====== REQUIRED: set the weekly checkpoint folder name here ======
REM Use the weekly one (24/12/4, dm128, huber1) unless you trained another config.
set "SETTING=panel_Autoformer_ftMS_sl24_ll12_pl4_dm128_el2_dl1_log1p_huber1"

REM Output directory
set "OUT_DIR=weekly_retrained_0505"

cd /d "%REPO_ROOT%"

echo === Export weekly TEST predictions (ratio split 70/15/15, target-year=2025) ===
echo setting:        %SETTING%
echo out_dir:        %OUT_DIR%
echo.

"%PY%" "%EXPORT_PY%" ^
  --autoformer-root "%AUTOFORMER_ROOT%" ^
  --panel-csv "%PANEL_CSV%" ^
  --checkpoints-dir "%CKPT_DIR%" ^
  --setting "%SETTING%" ^
  --out-dir "%OUT_DIR%" ^
  --split-mode ratio --train-ratio 0.7 --val-ratio 0.15 --test-ratio 0.15 ^
  --scope test --target-year 2025 ^
  --seq-len 24 --label-len 12 --pred-len 4 --freq w --target-transform log1p ^
  --d-model 128 --e-layers 2 --d-layers 1 --d-ff 512 --dropout 0.05 --moving-avg 25 ^
  --stamp 0505

echo.
echo Outputs (in %OUT_DIR%):
echo - panel_pred_test_2025_long_0505.csv
echo - panel_pred_test_2025_by_date_0505.csv
echo (plus the stable filenames without _0505)
endlocal

