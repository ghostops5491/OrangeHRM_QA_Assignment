# OrangeHRM BDD Automation Framework

A premium BDD automation suite for OrangeHRM using Playwright Python, Behave, and Allure Reporting.

## Features

- **BDD Framework**: Built with Behave Python for Gherkin-style behavior-driven testing.
- **Modern Browser Automation**: Utilizes Playwright Python for fast, reliable, and headless/headed web browser execution.
- **Page Object Model (POM)**: Structured and maintainable modular page selectors and actions.
- **Environment Configuration**: Dotenv (`.env`) files configuration for easy configuration of base URLs, credentials, browser selections, and timeouts.
- **Resilient Execution**: Custom global retry mechanism (monkeypatched in `features/environment.py`) which automatically retries transient failures or timeouts (up to 3 times) and captures screenshots on failures/errors.
- **Advanced Reporting**: Allure integration for beautiful interactive reports detailing steps, parameters, run status, and screenshots.
- **Tag-Based Filtering**: Clear, standard tag categories (`@smoke`, `@regression`, `@login`, `@password-reset`, etc.).

---

## Setup & Installation

### Windows (Automated)

The framework includes a setup script that automates Python virtual environment creation, dependencies installation, and browser setup. Run:

```cmd
setup.bat
```

### Manual Setup (All Platforms)

1. **Create and activate a virtual environment**:
   ```bash
   python -m venv .venv
   # Windows PowerShell
   .venv\Scripts\Activate.ps1
   # macOS/Linux
   source .venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Install Playwright browser binaries**:
   ```bash
   playwright install chromium
   ```

4. **Environment Configuration**:
   Copy `.env.example` to `.env` and adjust the variables (credentials, browser types, timeouts) as required:
   ```bash
   cp .env.example .env
   ```

---

## Running Tests

Before running tests, ensure your virtual environment is activated:
```bash
.venv\Scripts\activate
```

### Execute Tests

* **Run all tests**:
  ```bash
  python run_tests.py
  ```

* **Run with tags** (e.g., Smoke tests, Regression tests):
  ```bash
  python run_tests.py --tags @smoke
  python run_tests.py --tags @regression
  ```

* **Generate & open Allure reports** automatically after execution:
  ```bash
  python run_tests.py --report
  ```

### Manual Report Generation

To generate and view Allure reports from existing results manually:
```bash
allure serve reports/allure-results
```
