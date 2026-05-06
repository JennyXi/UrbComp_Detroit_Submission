@echo off
setlocal enableextensions

REM Daily POI alignment (Oct 2025), mirroring weekly_retrained_0505 README alignment commands.

set "REPO_ROOT=E:\Urban Computing Final Project\Try_0412"
set "PY=%REPO_ROOT%\.venv\Scripts\python.exe"

cd /d "%REPO_ROOT%"

mkdir "%REPO_ROOT%\daily_retrained_0505\alignment" 2>nul

echo === 1) compute_alignment.py (daily Oct 2025) ===
"%PY%" "%REPO_ROOT%\POI_Alignment_0429\compute_alignment.py" ^
  --pred-csv "%REPO_ROOT%\daily_retrained_0505\outputs\panel_pred_test_2025_by_date_output_daily_0505_v1.csv" ^
  --poi-parquet "%REPO_ROOT%\POI_Alignment_0429\grid100_poi_static_2024.parquet" ^
  --date-start 2025-10-01 --date-end 2025-10-31 ^
  --pred-col y_pred_mean ^
  --ridge-alpha 0.1 --target-log1p ^
  --out-csv "%REPO_ROOT%\daily_retrained_0505\alignment\alignment_oct2025_daily_0505.csv" ^
  --out-coefs-json "%REPO_ROOT%\daily_retrained_0505\alignment\alignment_ridge_coefs_oct2025_daily_0505.json"

echo.
echo === 2) summarize_alignment.py (ALL grids, gates disabled) ===
"%PY%" "%REPO_ROOT%\POI_Alignment_0429\summarize_alignment.py" ^
  --alignment-csv "%REPO_ROOT%\daily_retrained_0505\alignment\alignment_oct2025_daily_0505.csv" ^
  --high-positive-quantile 0 ^
  --gate-r-quantile 0 --gate-min-weeks 0 --gate-cbar-quantile 0 --gate-scarcity-q-min 0 ^
  --out-summary-json "%REPO_ROOT%\daily_retrained_0505\alignment\alignment_summary_oct2025_daily_0505_ALL.json" ^
  --out-top-positive-csv "%REPO_ROOT%\daily_retrained_0505\alignment\alignment_top_positive_oct2025_daily_0505_ALL.csv" ^
  --out-top-negative-csv "%REPO_ROOT%\daily_retrained_0505\alignment\alignment_top_negative_oct2025_daily_0505_ALL.csv" ^
  --out-priority-csv "%REPO_ROOT%\daily_retrained_0505\alignment\alignment_priority_candidates_oct2025_daily_0505_ALL.csv"

echo.
echo === 3) export_priority_candidates_to_gpkg.py ===
"%PY%" "%REPO_ROOT%\daily_retrained_0505\export_alignment_candidates_all_to_gpkg_oct2025_daily_0505.py"

endlocal
