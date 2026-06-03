import os
import subprocess
import sys
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed
from config.config import Config


def run_feature(feature_file: str, tags: str = None) -> int:
    """Run a single feature file in a behave subprocess and log output."""
    cmd = [sys.executable, "-m", "behave", feature_file]
    
    if tags:
        cmd.extend(["--tags", tags])
    
    cmd.extend(["--format", "allure_behave.formatter:AllureFormatter", "-o", Config.ALLURE_RESULTS_DIR])
    
    # We redirect output to avoid console interleaving
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Write output to log file
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    feature_name = os.path.basename(feature_file).replace(".feature", "")
    log_path = os.path.join(log_dir, f"{feature_name}.log")
    
    with open(log_path, "w", encoding="utf-8") as log_file:
        log_file.write(f"=== FEATURE RUN: {feature_file} ===\n")
        log_file.write(f"Command run: {' '.join(cmd)}\n")
        log_file.write(f"Exit code: {result.returncode}\n\n")
        log_file.write("=== STDOUT ===\n")
        log_file.write(result.stdout)
        log_file.write("\n=== STDERR ===\n")
        log_file.write(result.stderr)
        
    return result.returncode


def run_tests_sequential(tags: str = None) -> int:
    """Run all Behave tests sequentially (standard behave execution)."""
    cmd = [sys.executable, "-m", "behave"]
    
    if tags:
        cmd.extend(["--tags", tags])
    
    cmd.extend(["--format", "allure_behave.formatter:AllureFormatter", "-o", Config.ALLURE_RESULTS_DIR])
    
    os.makedirs(Config.ALLURE_RESULTS_DIR, exist_ok=True)
    print(f"Running tests sequentially with command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


def run_tests_parallel(tags: str = None, workers: int = None) -> int:
    """Run all Behave feature files concurrently in separate processes."""
    os.makedirs(Config.ALLURE_RESULTS_DIR, exist_ok=True)
    
    features = glob.glob("features/**/*.feature", recursive=True)
    if not features:
        print("Error: No feature files found in features/ directory.")
        return 1
        
    num_workers = workers if workers else Config.PARALLEL_WORKERS
    print(f"Running {len(features)} feature files in parallel with {num_workers} workers...")
    print("Individual logs will be saved to the 'logs/' directory.\n")
    
    # We use ThreadPoolExecutor to run behave subprocesses in parallel
    results = {}
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(run_feature, f, tags): f for f in features}
        for future in as_completed(futures):
            feature_file = futures[future]
            try:
                exit_code = future.result()
                results[feature_file] = exit_code
                status = "PASSED" if exit_code == 0 else "FAILED"
                print(f"[{status}] {feature_file}")
            except Exception as e:
                print(f"[ERROR] {feature_file}: {e}")
                results[feature_file] = 1
                
    # Print execution summary
    print("\n" + "=" * 50)
    print("Parallel Execution Summary")
    print("=" * 50)
    
    failed_features = []
    for f, ec in results.items():
        status = "Passed" if ec == 0 else "Failed"
        print(f"{f:<50} : {status}")
        if ec != 0:
            feature_name = os.path.basename(f).replace(".feature", "")
            failed_features.append(f"{f} (logs: logs/{feature_name}.log)")
            
    print("=" * 50)
    
    if failed_features:
        print("\nThe following features failed:")
        for ff in failed_features:
            print(f" - {ff}")
        return 1
        
    print("\nAll feature files completed successfully.")
    return 0


def generate_allure_report():
    """Generate Allure report from results."""
    cmd = ["allure", "serve", Config.ALLURE_RESULTS_DIR]
    try:
        subprocess.run(cmd, shell=os.name == "nt")
    except KeyboardInterrupt:
        # Catch Ctrl+C cleanly when stopping the Allure serve process
        print("\nAllure report server stopped.")



if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run OrangeHRM automation tests")
    parser.add_argument("--tags", help="Tags to filter tests (e.g., @smoke)")
    parser.add_argument("--report", action="store_true", help="Generate and open Allure report after tests")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--workers", type=int, help="Number of parallel workers (overrides .env configuration)")
    
    args = parser.parse_args()
    
    try:
        if args.parallel:
            exit_code = run_tests_parallel(args.tags, args.workers)
        else:
            exit_code = run_tests_sequential(args.tags)
            
        if args.report or Config.AUTO_OPEN_REPORT:
            generate_allure_report()
            
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nExecution interrupted by user. Exiting...")
        sys.exit(130)


