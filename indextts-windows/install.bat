@echo off
chcp 65001 >nul
setlocal EnableExtensions
title IndexTTS 2.5 一键安装

rem ====== 安装位置（想换盘就改这一行）======
set "INSTALL_DIR=D:\IndexTTS"
rem =========================================

set "REPO_DIR=%INSTALL_DIR%\index-tts"
set "UV_DIR=%INSTALL_DIR%\uv"
set "UV=%UV_DIR%\uv.exe"
set "LOG=%INSTALL_DIR%\install.log"

rem 国内镜像：PyPI 用阿里云，Python 本体用 npmmirror，HuggingFace 用 hf-mirror
set "UV_DEFAULT_INDEX=https://mirrors.aliyun.com/pypi/simple"
set "UV_PYTHON_INSTALL_MIRROR=https://registry.npmmirror.com/-/binary/python-build-standalone"
set "HF_ENDPOINT=https://hf-mirror.com"
rem 所有缓存都放在安装目录里，不占 C 盘
set "UV_CACHE_DIR=%INSTALL_DIR%\uv-cache"
set "UV_PYTHON_INSTALL_DIR=%INSTALL_DIR%\python"
set "MODELSCOPE_CACHE=%INSTALL_DIR%\modelscope-cache"
set "UV_HTTP_TIMEOUT=600"
set "UV_LINK_MODE=copy"

echo.
echo  ==============================================
echo    IndexTTS 2.5 一键安装  -  安装到 %INSTALL_DIR%
echo    全程大约需要下载 10 GB，请保持网络畅通
echo  ==============================================
echo.

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%INSTALL_DIR%" (
  echo [错误] 无法创建目录 %INSTALL_DIR%，请确认 D 盘存在且有写入权限。
  goto :fail
)

rem ---------- 1. 检查显卡驱动 ----------
echo [1/5] 检查 NVIDIA 显卡驱动...
where nvidia-smi >nul 2>&1
if errorlevel 1 (
  echo [警告] 找不到 nvidia-smi，可能没装 NVIDIA 驱动。
  echo        请先到 https://www.nvidia.cn/drivers/ 安装最新驱动，否则只能用 CPU，非常慢。
  pause
) else (
  nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
  echo        驱动版本需要 570 或更高，低于这个请先更新驱动。
)
echo.

rem ---------- 2. 安装 uv ----------
echo [2/5] 准备 uv（Python 环境管理工具）...
if exist "%UV%" goto :uv_ok
set "UV_ZIP=%INSTALL_DIR%\uv.zip"
call :download "https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip" "%UV_ZIP%"
if errorlevel 1 call :download "https://ghfast.top/https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip" "%UV_ZIP%"
if errorlevel 1 (
  echo [错误] uv 下载失败，请检查网络后重新运行本脚本。
  goto :fail
)
powershell -NoProfile -Command "Expand-Archive -Force '%UV_ZIP%' '%UV_DIR%'"
del "%UV_ZIP%" >nul 2>&1
if not exist "%UV%" (
  echo [错误] uv 解压失败。
  goto :fail
)
:uv_ok
"%UV%" --version
echo.

rem ---------- 3. 下载 IndexTTS 代码 ----------
echo [3/5] 下载 IndexTTS 官方代码...
if exist "%REPO_DIR%\webui.py" (
  echo        代码已存在，跳过。
  goto :code_ok
)
where git >nul 2>&1
if errorlevel 1 goto :code_zip
git clone --depth 1 https://github.com/index-tts/index-tts.git "%REPO_DIR%"
if not errorlevel 1 goto :code_ok
git clone --depth 1 https://ghfast.top/https://github.com/index-tts/index-tts.git "%REPO_DIR%"
if not errorlevel 1 goto :code_ok
:code_zip
set "CODE_ZIP=%INSTALL_DIR%\index-tts.zip"
call :download "https://github.com/index-tts/index-tts/archive/refs/heads/main.zip" "%CODE_ZIP%"
if errorlevel 1 call :download "https://ghfast.top/https://github.com/index-tts/index-tts/archive/refs/heads/main.zip" "%CODE_ZIP%"
if errorlevel 1 (
  echo [错误] 代码下载失败，请检查网络后重新运行本脚本。
  goto :fail
)
if exist "%REPO_DIR%" rmdir /s /q "%REPO_DIR%"
powershell -NoProfile -Command "Expand-Archive -Force '%CODE_ZIP%' '%INSTALL_DIR%'"
ren "%INSTALL_DIR%\index-tts-main" index-tts
del "%CODE_ZIP%" >nul 2>&1
if not exist "%REPO_DIR%\webui.py" (
  echo [错误] 代码解压失败。
  goto :fail
)
:code_ok
cd /d "%REPO_DIR%"
echo.

rem ---------- 4. 安装 Python 和依赖 ----------
echo [4/5] 安装 Python 3.11 和依赖（PyTorch 约 3 GB，时间较长，请耐心等）...
"%UV%" sync --extra webui
if not errorlevel 1 goto :deps_ok
echo        第一次失败，换官方源再试一次...
set "UV_PYTHON_INSTALL_MIRROR="
set "UV_DEFAULT_INDEX="
"%UV%" sync --extra webui
if errorlevel 1 (
  echo [错误] 依赖安装失败。请把上面的报错截图发给 Claude。
  goto :fail
)
:deps_ok
"%UV%" run python -c "import torch; print('PyTorch', torch.__version__, '| CUDA 可用:', torch.cuda.is_available(), '|', torch.cuda.get_device_name(0) if torch.cuda.is_available() else '没有检测到显卡')"
echo.

rem ---------- 5. 下载模型 ----------
echo [5/5] 从 ModelScope 下载 IndexTTS-2.5 模型（约 5 GB）...
"%UV%" run modelscope download --model IndexTeam/IndexTTS-2.5 --local_dir checkpoints
if errorlevel 1 (
  echo [警告] 模型下载没有完成。可以直接重新运行本脚本继续下载，
  echo        或者先运行“启动.bat”，程序也会自动补下载。
)

echo.
echo  ==============================================
echo    安装完成！以后双击“启动.bat”即可使用。
echo    第一次启动还会自动下载几个小模型，稍等一会儿。
echo  ==============================================
pause
exit /b 0

:fail
echo.
echo 安装没有完成。修好问题后可以直接重新运行本脚本，已完成的步骤会自动跳过。
pause
exit /b 1

rem 用法：call :download URL 保存路径
:download
echo        下载 %~1
powershell -NoProfile -Command "$ProgressPreference='SilentlyContinue'; try { Invoke-WebRequest -Uri '%~1' -OutFile '%~2' -UseBasicParsing -TimeoutSec 120; exit 0 } catch { Write-Host $_.Exception.Message; exit 1 }"
exit /b %errorlevel%
