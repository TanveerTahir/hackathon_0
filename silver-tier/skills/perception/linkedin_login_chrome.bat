@echo off
REM LinkedIn Login Helper - Using Your Regular Chrome
REM This opens LinkedIn in your regular Chrome browser for login

echo ============================================================
echo LinkedIn Login Helper - Chrome Browser
echo ============================================================
echo.
echo This will open LinkedIn in your regular Chrome browser.
echo.
echo Steps:
echo   1. Chrome will open to LinkedIn login page
echo   2. Login with your credentials
echo   3. Wait until you see your feed (10-15 seconds)
echo   4. Close Chrome when done
echo.
echo Press any key to continue...
pause >nul

echo.
echo Opening Chrome with LinkedIn...
echo.

REM Open Chrome with your default profile
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" ^
  --new-window ^
  https://www.linkedin.com

echo.
echo Chrome should be opening...
echo.
echo After logging in:
echo   1. Wait 10 seconds for session to save
echo   2. Close Chrome
echo   3. Run: test_linkedin_watcher.py
echo.
pause
