import os
import subprocess
import sys
from config.config import Config


def run_tests(tags: str = None):
    """Run Behave tests with optional tags."""
    cmd = [sys.executable, "-m", "behave"]
    
    if tags:
        cmd.extend(["--tags", tags])
    
    cmd.extend(["--format", "allure_behave.formatter:AllureFormatter", "-o", Config.ALLURE_RESULTS_DIR])
    
    os.makedirs(Config.ALLURE_RESULTS_DIR, exist_ok=True)
    
    print(f"Running tests with command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


def generate_allure_report():
    """Generate Allure report from results."""
    cmd = ["allure", "serve", Config.ALLURE_RESULTS_DIR]
    subprocess.run(cmd)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run OrangeHRM automation tests")
    parser.add_argument("--tags", help="Tags to filter tests (e.g., @smoke)")
    parser.add_argument("--report", action="store_true", help="Generate and open Allure report after tests")
    
    args = parser.parse_args()
    
    exit_code = run_tests(args.tags)
    
    if args.report and exit_code == 0:
        generate_allure_report()
    
    sys.exit(exit_code)
