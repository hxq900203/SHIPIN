@echo off
chcp 65001 >nul
setlocal EnableExtensions
title IndexTTS 一键调试

set "INSTALL_DIR=D:\IndexTTS"
set "UV=%INSTALL_DIR%\uv\uv.exe"
set "UV_CACHE_DIR=%INSTALL_DIR%\uv-cache"
set "UV_PYTHON_INSTALL_DIR=%INSTALL_DIR%\python"
set "MODELSCOPE_CACHE=%INSTALL_DIR%\modelscope-cache"
set "HF_ENDPOINT=https://hf-mirror.com"
set "PYTHONUTF8=1"

if not exist "%UV%" (
  echo 还没安装，请先运行 install.bat
  pause
  exit /b 1
)
if not exist "%~dp0tune.py" (
  echo 找不到 tune.py，请把它和本文件放在同一个文件夹里。
  pause
  exit /b 1
)
cd /d "%INSTALL_DIR%\index-tts"

rem 用法：把参考音频拖到本文件图标上；直接双击也行，会提示你拖进窗口
"%UV%" run --no-sync python "%~dp0tune.py" %1
echo.
pause
