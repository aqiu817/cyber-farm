@echo off
set PORT=%1
if "%PORT%"=="" set PORT=4173
python app.py --host 0.0.0.0 --port %PORT%
