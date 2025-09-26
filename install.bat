@echo off
echo Installing required packages...
py -m pip install --upgrade pip
py -m pip install beautifulsoup4 ics playwright
py -m playwright install chromium
echo.
echo Installation complete!
pause
