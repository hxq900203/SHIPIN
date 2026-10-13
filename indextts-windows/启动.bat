@echo off
chcp 65001 >nul
setlocal EnableExtensions
title IndexTTS 2.5

set "INSTALL_DIR=D:\IndexTTS"
set "UV=%INSTALL_DIR%\uv\uv.exe"
set "UV_CACHE_DIR=%INSTALL_DIR%\uv-cache"
set "UV_PYTHON_INSTALL_DIR=%INSTALL_DIR%\python"
set "MODELSCOPE_CACHE=%INSTALL_DIR%\modelscope-cache"
set "HF_ENDPOINT=https://hf-mirror.com"
set "UV_DEFAULT_INDEX=https://mirrors.aliyun.com/pypi/simple"

if not exist "%UV%" (
  echo 还没安装，请先运行 install.bat
  pause
  exit /b 1
)
cd /d "%INSTALL_DIR%\index-tts"

echo 正在启动 IndexTTS，加载模型需要一两分钟，准备好后会自动打开浏览器...
echo 用完直接关掉这个黑色窗口即可。
echo.

rem 后台等网页准备好，再自动打开浏览器
start "" /b powershell -NoProfile -WindowStyle Hidden -Command "while ($true) { try { Invoke-WebRequest 'http://127.0.0.1:7860' -UseBasicParsing -TimeoutSec 2 | Out-Null; break } catch { Start-Sleep 3 } }; Start-Process 'http://127.0.0.1:7860'"

"%UV%" run --no-sync webui.py --host 127.0.0.1 --port 7860
echo.
echo 程序已退出。如果是报错退出，请把上面的报错截图发给 Claude。
pause
