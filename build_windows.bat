@echo off
setlocal

cd /d %~dp0

python -m pip install pyinstaller
if errorlevel 1 exit /b 1

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

pyinstaller ^
  --noconfirm ^
  --clean ^
  --windowed ^
  --name "audio-annotation-tool" ^
  --add-data "question_config.py;." ^
  app.py

echo.
echo Windows 打包完成:
echo EXE: %~dp0dist\audio-annotation-tool\audio-annotation-tool.exe

