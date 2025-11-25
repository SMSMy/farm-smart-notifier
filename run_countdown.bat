@echo off
echo ========================================
echo        Farm Notifier Countdown Timer
echo ========================================
echo.

echo Installing requirements...
pip install -r requirements.txt

echo.
echo Starting countdown timer...
python test_countdown.py

pause

