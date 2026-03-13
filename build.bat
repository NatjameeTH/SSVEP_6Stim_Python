@echo off
cd /d "%~dp0"

rmdir /s /q build
rmdir /s /q dist

pyinstaller --onefile --windowed ^
 --name "Fatigue SSVEP" ^
 --icon=BCI.ico ^
 --add-data "stimuli;stimuli" ^
 --add-data "modules;modules" ^
 main.py

echo.
echo Build complete!
pause