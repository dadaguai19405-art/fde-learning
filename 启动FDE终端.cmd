@echo off
chcp 65001 >nul
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "PYTHONPATH=C:\Users\Administrator\Documents\Codex\2026-10-19\f\tools\python-packages\site-packages;%PYTHONPATH%"
set "GIT_CONFIG_GLOBAL=C:\Users\Administrator\Documents\Codex\2026-10-19\f\tools\gitconfig"
set "PATH=C:\Users\Administrator\Documents\Codex\2026-10-19\f\tools\bin;C:\Users\Administrator\Documents\Codex\2026-10-19\f\tools\Git\cmd;C:\Users\Administrator\AppData\Local\Programs\Python\Python314;C:\Users\Administrator\AppData\Local\Programs\Python\Python314\Scripts;%PATH%"
cd /d "C:\Users\Administrator\Documents\Codex\2026-10-19\f\fde-learning"
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoExit -Command "Write-Host 'FDE environment ready' -ForegroundColor Green; Write-Host ('Python: ' + (python --version)); Write-Host ('Git: ' + (git --version)); Write-Host ('Current directory: ' + (Get-Location))"
