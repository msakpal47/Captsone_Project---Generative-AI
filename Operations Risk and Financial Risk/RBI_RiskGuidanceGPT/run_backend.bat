@echo off
setlocal
cd /d "%~dp0"
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8020 --reload --log-level info
endlocal
