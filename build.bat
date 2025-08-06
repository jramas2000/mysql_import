@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo Building executable...
pyinstaller csv_import_gui.spec

echo Build complete! Executable is in the dist folder.
pause 