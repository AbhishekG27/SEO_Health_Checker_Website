@echo off
REM Run scheduled SEO audit (use with Windows Task Scheduler at 10 AM daily).
REM Edit PROJECT_DIR to your new-automation folder path. Use the same Python that has dependencies installed.

set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

python run_scheduled_audit.py
if errorlevel 1 exit /b 1
exit /b 0
