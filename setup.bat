@echo off
echo =================================================================
echo        OrangeHRM BDD Automation Framework Setup ^& Install
echo =================================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to your system PATH.
    echo Please install Python 3.8+ and try again.
    pause
    exit /b %errorlevel%
)

:: Create virtual environment if it doesn't exist
if not exist .venv (
    echo [INFO] Creating Python virtual environment [.venv]...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b %errorlevel%
    )
    echo [INFO] Virtual environment created successfully.
) else (
    echo [INFO] Virtual environment [.venv] already exists.
)
echo.

:: Activate virtual environment
echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b %errorlevel%
)
echo [INFO] Virtual environment activated.
echo.

:: Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip
echo.

:: Install dependencies
echo [INFO] Installing required dependencies from requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b %errorlevel%
)
echo [INFO] Dependencies installed successfully.
echo.

:: Install Playwright browsers
echo [INFO] Installing Playwright browsers (Chromium)...
playwright install chromium
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Playwright browsers.
    pause
    exit /b %errorlevel%
)
echo [INFO] Playwright browsers installed successfully.
echo.

echo =================================================================
echo                  Setup Completed Successfully!
echo =================================================================
echo.
echo First, activate the virtual environment:
echo   .venv\Scripts\activate.bat
echo.
echo Available Test Execution Commands:
echo   - Run all tests:             python run_tests.py
echo   - Run in parallel:           python run_tests.py --parallel
echo   - Run specific tag:          python run_tests.py --tags @smoke
echo   - Run with Allure report:    python run_tests.py --report
echo   - Rerun failed tests only:   python run_tests.py --rerun
echo   - Run specific feature file: behave features/user_management.feature
echo.
echo You can also combine options:
echo   - Run @smoke in parallel:    python run_tests.py --parallel --tags @smoke
echo.
echo CLI Usage Signature:
echo   usage: run_tests.py [-h] [--tags TAGS] [--report] [--parallel] [--workers WORKERS] [--rerun]
echo.
pause
