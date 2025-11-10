@echo off
call .venv\Scripts\activate
python dashboard\run_pipeline.py
deactivate
pause