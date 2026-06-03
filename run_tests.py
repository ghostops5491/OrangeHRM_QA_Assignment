import os
import subprocess
import sys
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed
from config.config import Config


def run_target(target: str, tags: str = None) -> int:
    """Run a single feature or scenario in a behave subprocess and log output."""
    cmd = [sys.executable, "-m", "behave", target]
    
    if tags:
        cmd.extend(["--tags", tags])
    
    # Generate a safe filename for the temporary rerun file
    safe_name = target.replace("/", "_").replace("\\", "_").replace(":", "_").replace(".", "_")
    temp_rerun = os.path.join("logs", f"rerun_{safe_name}.features")
    
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Clear any existing temp rerun file for this target
    if os.path.exists(temp_rerun):
        try:
            os.remove(temp_rerun)
        except Exception:
            pass
            
    cmd.extend([
        "--format", "allure_behave.formatter:AllureFormatter", "-o", Config.ALLURE_RESULTS_DIR,
        "--format", "rerun", "-o", temp_rerun
    ])
    
    # We redirect output to avoid console interleaving
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Write output to log file
    log_dir = "logs"
    log_path = os.path.join(log_dir, f"{safe_name}.log")
    
    with open(log_path, "w", encoding="utf-8") as log_file:
        log_file.write(f"=== TARGET RUN: {target} ===\n")
        log_file.write(f"Command run: {' '.join(cmd)}\n")
        log_file.write(f"Exit code: {result.returncode}\n\n")
        log_file.write("=== STDOUT ===\n")
        log_file.write(result.stdout)
        log_file.write("\n=== STDERR ===\n")
        log_file.write(result.stderr)
        
    return result.returncode


def run_tests_sequential(tags: str = None, rerun_only: bool = False) -> int:
    """Run Behave tests sequentially (standard behave execution)."""
    cmd = [sys.executable, "-m", "behave"]
    
    if rerun_only:
        rerun_file = "rerun_failed.features"
        if not os.path.exists(rerun_file) or os.path.getsize(rerun_file) == 0:
            print("No failed scenarios to rerun.")
            return 0
        cmd.append(f"@{rerun_file}")
    elif tags:
        cmd.extend(["--tags", tags])
    
    cmd.extend([
        "--format", "allure_behave.formatter:AllureFormatter", "-o", Config.ALLURE_RESULTS_DIR,
        "--format", "rerun", "-o", "rerun_failed.features"
    ])
    
    os.makedirs(Config.ALLURE_RESULTS_DIR, exist_ok=True)
    print(f"Running tests sequentially with command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


def run_tests_parallel(tags: str = None, workers: int = None, rerun_only: bool = False) -> int:
    """Run Behave features or failed scenarios concurrently in separate processes."""
    os.makedirs(Config.ALLURE_RESULTS_DIR, exist_ok=True)
    
    if rerun_only:
        rerun_file = "rerun_failed.features"
        if not os.path.exists(rerun_file) or os.path.getsize(rerun_file) == 0:
            print("No failed scenarios to rerun.")
            return 0
        with open(rerun_file, "r", encoding="utf-8") as f:
            targets = [line.strip() for line in f if line.strip()]
        if not targets:
            print("No failed scenarios to rerun.")
            return 0
    else:
        targets = glob.glob("features/**/*.feature", recursive=True)
        if not targets:
            print("Error: No feature files found in features/ directory.")
            return 1
            
    num_workers = workers if workers else Config.PARALLEL_WORKERS
    print(f"Running {len(targets)} targets in parallel with {num_workers} workers...")
    print("Individual logs will be saved to the 'logs/' directory.\n")
    
    # Remove old temporary rerun files
    os.makedirs("logs", exist_ok=True)
    for f in glob.glob("logs/rerun_*.features"):
        try:
            os.remove(f)
        except Exception:
            pass
            
    # We use ThreadPoolExecutor to run behave subprocesses in parallel
    results = {}
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(run_target, t, tags): t for t in targets}
        for future in as_completed(futures):
            target = futures[future]
            try:
                exit_code = future.result()
                results[target] = exit_code
                status = "PASSED" if exit_code == 0 else "FAILED"
                print(f"[{status}] {target}")
            except Exception as e:
                print(f"[ERROR] {target}: {e}")
                results[target] = 1
                
    # Print execution summary
    print("\n" + "=" * 50)
    print("Parallel Execution Summary")
    print("=" * 50)
    
    failed_targets = []
    for t, ec in results.items():
        status = "Passed" if ec == 0 else "Failed"
        print(f"{t:<50} : {status}")
        if ec != 0:
            safe_name = t.replace("/", "_").replace("\\", "_").replace(":", "_").replace(".", "_")
            failed_targets.append(f"{t} (logs: logs/{safe_name}.log)")
            
    print("=" * 50)
    
    # Merge temporary rerun files into the master rerun_failed.features
    temp_rerun_files = glob.glob("logs/rerun_*.features")
    master_rerun = "rerun_failed.features"
    all_failed_lines = []
    for temp_file in temp_rerun_files:
        if os.path.exists(temp_file):
            with open(temp_file, "r", encoding="utf-8") as tf:
                for line in tf:
                    if line.strip():
                        all_failed_lines.append(line.strip())
                        
    # Write unique failed lines back to master rerun file
    with open(master_rerun, "w", encoding="utf-8") as mf:
        for line in sorted(list(set(all_failed_lines))):
            mf.write(f"{line}\n")
            
    # Clean up temporary rerun files
    for temp_file in temp_rerun_files:
        try:
            os.remove(temp_file)
        except Exception:
            pass
            
    if failed_targets:
        print("\nThe following targets failed:")
        for ft in failed_targets:
            print(f" - {ft}")
        return 1
        
    print("\nAll targets completed successfully.")
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
    parser.add_argument("--rerun", action="store_true", help="Rerun only the failed test cases from the last run")
    
    args = parser.parse_args()
    
    try:
        if args.parallel:
            exit_code = run_tests_parallel(args.tags, args.workers, args.rerun)
        else:
            exit_code = run_tests_sequential(args.tags, args.rerun)
            
        if args.report or Config.AUTO_OPEN_REPORT:
            generate_allure_report()
            
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nExecution interrupted by user. Exiting...")
        sys.exit(130)


