@echo off
rem Bounded local launcher: materialize first, parse, then execute.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0parse-check.ps1" -ScriptPath "%~dp0launch-worker.ps1" || exit /b 1
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0launch-worker.ps1" %*
