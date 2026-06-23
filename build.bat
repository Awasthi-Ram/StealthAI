@echo off
echo Building Stealth AI application...
pyinstaller --noconsole --onefile --hidden-import="mss" --hidden-import="keyboard" --hidden-import="sounddevice" --hidden-import="soundfile" --collect-all="playwright" --name "StealthAI_New" main.py
echo Build complete! Check the dist folder for StealthAI_New.exe
