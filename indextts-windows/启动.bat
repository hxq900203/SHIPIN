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

rem BigVGAN 声码器：程序自带的下载走 hf-mirror，大文件容易断；这里先从 ModelScope 下好（支持断点续传）
set "BIGVGAN=%INSTALL_DIR%\index-tts\checkpoints\hf_cache\bigvgan"
if exist "%BIGVGAN%\config.json" if exist "%BIGVGAN%\bigvgan_generator.pt" goto :bigvgan_ok
echo 正在从 ModelScope 下载 BigVGAN 声码器（约 450 MB）...
if exist "%BIGVGAN%\*.tmp" del /q "%BIGVGAN%\*.tmp"
"%UV%" run --no-sync modelscope download --model nv-community/bigvgan_v2_22khz_80band_256x config.json bigvgan_generator.pt --local_dir "%BIGVGAN%"
if not exist "%BIGVGAN%\bigvgan_generator.pt" (
  echo [错误] BigVGAN 下载失败，请检查网络后重新运行“启动.bat”，会接着下载。
  pause
  exit /b 1
)
:bigvgan_ok

echo 正在启动 IndexTTS，加载模型需要一两分钟，准备好后会自动打开浏览器...
echo 用完直接关掉这个黑色窗口即可。
echo.

rem 后台等网页准备好，再自动打开浏览器
start "" /b powershell -NoProfile -WindowStyle Hidden -Command "while ($true) { try { Invoke-WebRequest 'http://127.0.0.1:7860' -UseBasicParsing -TimeoutSec 2 | Out-Null; break } catch { Start-Sleep 3 } }; Start-Process 'http://127.0.0.1:7860'"

"%UV%" run --no-sync webui.py --host 127.0.0.1 --port 7860
echo.
echo 程序已退出。如果是报错退出，请把上面的报错截图发给 Claude。
pause
