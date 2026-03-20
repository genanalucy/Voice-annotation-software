@echo off
setlocal

cd /d %~dp0

set /p VERSION=请输入本次打包版本号（例如 1.0.0）: 
if "%VERSION%"=="" (
  echo 未输入版本号，已取消打包。
  exit /b 1
)

set "VERSION_SAFE=%VERSION: =_%"
set "VERSION_SAFE=%VERSION_SAFE:/=-%"
set "VERSION_SAFE=%VERSION_SAFE:\=-%"
set "VERSION_SAFE=%VERSION_SAFE::=-%"
set "APP_NAME=audio-annotation-tool_v%VERSION_SAFE%"

python -m pip install pyinstaller
if errorlevel 1 exit /b 1

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

pyinstaller ^
  --noconfirm ^
  --clean ^
  --windowed ^
  --name "%APP_NAME%" ^
  --add-data "question_config.py;." ^
  app.py

echo %VERSION% > "%~dp0dist\%APP_NAME%\version.txt"

echo.
echo Windows 打包完成:
echo 版本号: %VERSION%
echo EXE: %~dp0dist\%APP_NAME%\%APP_NAME%.exe
echo VERSION: %~dp0dist\%APP_NAME%\version.txt
