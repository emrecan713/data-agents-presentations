@echo off
setlocal
cd /d "%~dp0"

where node >nul 2>nul || (echo Node.js is required: https://nodejs.org & pause & exit /b 1)
if not exist node_modules\@marp-team\marp-cli (
  echo Installing Marp...
  call npm install --no-fund --no-audit || (pause & exit /b 1)
)

rem Direct use: start.bat preview ^| new "Purpose" [YYYY-MM-DD] ^| check [deck] ^| build [deck]
if /i "%~1"=="preview" (call npm run preview & exit /b)
if /i "%~1"=="new" (
  if "%~3"=="" (call npm run new -- %2) else (call npm run new -- %2 --date %3)
  exit /b
)
if /i "%~1"=="check" (call npm run check -- %2 & exit /b)
if /i "%~1"=="build" (call npm run build -- %2 %3 & exit /b)

:menu
echo.
echo   Data Agents Presentations
echo   1  Preview decks in the browser (live reload)
echo   2  New deck
echo   3  Check accessibility
echo   4  Build all decks (HTML + PDF)
echo   Q  Quit
choice /c 1234Q /n /m "Choose: "
if errorlevel 5 exit /b
if errorlevel 4 (call npm run build & goto menu)
if errorlevel 3 (call npm run check & goto menu)
if errorlevel 2 goto new
start "" /b cmd /c "timeout /t 4 >nul & start http://localhost:8090/"
call npm run preview
goto menu

:new
set "DECKTITLE="
set "DECKDATE="
set /p DECKTITLE=Purpose (e.g. Data Agents workshop): 
set /p DECKDATE=Date of use (YYYY-MM-DD, empty if not known yet): 
if "%DECKDATE%"=="" (call npm run new -- "%DECKTITLE%") else (call npm run new -- "%DECKTITLE%" --date %DECKDATE%)
goto menu
