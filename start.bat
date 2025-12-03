@echo off
chcp 65001 >nul
REM 简易启动器：在 PowerShell 中运行 start.ps1，避免批处理编码/解析问题
set "PS=%SystemRoot%\system32\WindowsPowerShell\v1.0\powershell.exe"
if exist "%~dp0start.ps1" (
    "%PS%" -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1"
    exit /b %ERRORLEVEL%
) else (
    echo 错误：未找到 start.ps1，请确保此文件与 start.bat 位于同一目录
    pause
    exit /b 1
)