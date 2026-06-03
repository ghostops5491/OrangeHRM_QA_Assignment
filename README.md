# OrangeHRM BDD Automation Framework

A premium BDD automation suite for OrangeHRM using Playwright Python, Behave, and Allure Reporting.

## Features

- **BDD Framework**: Built with Behave Python for Gherkin-style behavior-driven testing.
- **Modern Browser Automation**: Utilizes Playwright Python for fast, reliable, and headless/headed web browser execution.
- **Page Object Model (POM)**: Structured and maintainable modular page selectors and actions.
- **Environment Configuration**: Dotenv (`.env`) files configuration for easy configuration of base URLs, credentials, browser selections, and timeouts.
- **Advanced Reporting**: Allure integration for beautiful interactive reports detailing steps, parameters, run status, screenshots, traces, and videos.
- **Tag-Based Filtering**: Clear, standard tag categories (`@smoke`, `@regression`, `@login`, `@password-reset`, etc.).

---

## AI-Powered Features

This framework integrates Google Gemini (`gemini-2.5-flash`) via an HTTP client to provide smart automation capabilities:

### 1. AI-Powered Self-Healing Locators
* **How it works**: When a Playwright element interaction (like `click()` or `fill()`) times out, the framework automatically intercepts the error, captures a screenshot, extracts a lightweight DOM profile of active elements, and requests Gemini to find the corrected selector.
* **Benefit**: Dramatically reduces test flakiness caused by minor UI shifts (e.g., button name or style changes) by correcting the selector dynamically at runtime.
* **Configuration**: Can be toggled on/off in `.env` via `AI_SELF_HEALING=true`.

### 2. Intelligent Failure & Flakiness Analysis
* **How it works**: When a test scenario fails or errors out, the framework compiles the failed step definition, error traceback, browser console logs, and failure screenshot, and sends them to Gemini.
* **Benefit**: Gemini returns a plain-English, markdown-formatted report diagnosing the root cause and suggesting a step-by-step fix, which is attached directly to the Allure report under "AI Failure Analysis Report".
* **Configuration**: Can be toggled on/off in `.env` via `AI_FAILURE_ANALYSIS=true`.

---

## Parallel Test Execution

To drastically reduce execution time, the framework supports parallel run capability at the feature-file level.

### How it works:
* The test runner (`run_tests.py`) crawls the `features/` directory and partitions test execution by `.feature` files.
* Each feature file is executed concurrently in its own independent `behave` subprocess using a thread pool.
* Subprocess outputs (stdout/stderr) are redirected to feature-specific log files inside the `logs/` directory (e.g., `logs/login.log`) to keep the main console clear and readable.
* Allure natively aggregates individual test results from concurrent processes, presenting them as a single cohesive report.

### Running Tests in Parallel:

* **Default Parallel Run**:
  Runs features in parallel using the default worker count defined in `.env` (`PARALLEL_WORKERS=3`):
  ```bash
  python run_tests.py --parallel
  ```

* **Custom Worker Count**:
  Override the default worker count dynamically:
  ```bash
  python run_tests.py --parallel --workers 4
  ```

* **Parallel Run with Tag Filter**:
  Filter and run matching tests concurrently:
  ```bash
  python run_tests.py --parallel --tags "@smoke"
  ```

* **Parallel Run and Open Allure Report**:
  Run tests in parallel and compile/open the report immediately:
  ```bash
  python run_tests.py --parallel --report
  ```

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
   *Make sure to configure your `GEMINI_API_KEY` in the `.env` file to utilize the AI features.*

---

## Running Tests (Sequential)

Before running tests, ensure your virtual environment is activated:
```bash
.venv\Scripts\activate
```

* **Run all tests sequentially**:
  ```bash
  python run_tests.py
  ```

* **Run sequential with tags**:
  ```bash
  python run_tests.py --tags @smoke
  ```

* **Generate & open Allure reports**:
  ```bash
  python run_tests.py --report
  ```

### Manual Report Generation

To generate and view Allure reports from existing results manually:
```bash
allure serve reports/allure-results
```
