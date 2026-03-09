from socket import socket, AF_INET, SOCK_STREAM
import time
from datetime import datetime
import json
import os
from src.utils.logger import TestLogger
from Ammeters.base_ammeter import AmmeterEmulatorBase
import statistics
from pathlib import Path


RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)
ORIGINAL_LOGS_DIR = Path("logs")
ORIGINAL_LOGS_DIR.mkdir(exist_ok=True)
ALL_RUNS_JSON = r"results/all_runs.json"

def request_current_from_ammeter(port: int, command: bytes):
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect(('localhost', port))
        s.sendall(command)
        data = s.recv(1024)
        if data:
            print(f"Received current measurement from port {port}: {data.decode('utf-8')} A")
        else:
            print("No data received.")


def get_current_from_ammeter(port: int, command: bytes) -> float:
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect(('localhost', port))
        s.sendall(command)
        data = s.recv(1024)
        if not data:
            raise RuntimeError(f"No data received from port {port}")
        return float(data.decode("utf-8").strip())


def create_unique_log_file(emulator_name: str):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    emulator_dir = RESULTS_DIR / emulator_name.lower()
    emulator_dir.mkdir(exist_ok=True)
    return emulator_dir / f"{timestamp}_{emulator_name.lower()}.log"


def sample_measurements(port: int, command: bytes, emulator_name: str,
                        samples: int = 50, duration: float = 5):
    """
    Sample measurements from an ammeter and update both log files and JSON archive.
    """
    logger_orig = AmmeterEmulatorBase.port_loggers.get(port)
    results = []
    interval = duration / samples
    start_time = time.time()

    # יצירת שם קובץ ייחודי לריצה
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join("results", emulator_name.lower(), f"{timestamp}_{emulator_name.lower()}.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    with open(log_file, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | Sampling start for {emulator_name}\n")
        for i in range(samples):
            value = get_current_from_ammeter(port, command)
            results.append(value)
            line = f"{time.strftime('%H:%M:%S')} | Measurement {i+1}: {value:.6f} A\n"
            f.write(line)
            if logger_orig:
                logger_orig.info(line.strip())
            # precise timing
            next_sample_time = start_time + (i + 1) * interval
            sleep_time = next_sample_time - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)

    # סיכום
    end_time = time.time()
    total_runtime = end_time - start_time
    frequency = samples / duration

    summary = {
        "total_measurements": samples,
        "requested_duration_s": duration,
        "sampling_frequency_hz": round(frequency, 3),
        "actual_runtime_s": round(total_runtime, 3),
        "mean_current_a": round(statistics.mean(results), 6),
        "median_current_a": round(statistics.median(results), 6),
        "std_dev_current_a": round(statistics.stdev(results) if samples > 1 else 0, 6),
        "min_current_a": round(min(results), 6),
        "max_current_a": round(max(results), 6),
        "metadata": {
            "emulator": emulator_name,
            "log_file": log_file,
            "start_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time)),
            "end_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))
        }
    }

    # כתיבה לסיכום בקובץ עצמו
    summary_lines = [f"{key}: {value}" if not isinstance(value, dict) else f"{key}: {value}" for key, value in summary.items()]
    with open(log_file, "a") as f:
        f.write("\n--- Sampling Summary ---\n")
        for line in summary_lines:
            f.write(line + "\n")

    if logger_orig:
        logger_orig.info("--- Sampling Summary ---")
        for line in summary_lines:
            logger_orig.info(line)

    # עדכון JSON
    if os.path.exists(ALL_RUNS_JSON):
        with open(ALL_RUNS_JSON, "r") as f_json:
            all_runs = json.load(f_json)
    else:
        all_runs = []

    all_runs.append(summary)

    with open(ALL_RUNS_JSON, "w") as f_json:
        json.dump(all_runs, f_json, indent=4)

    return results

# --- Functions for historical retrieval & comparison ---

def load_all_runs():
    if not os.path.exists(ALL_RUNS_JSON):
        return []
    with open(ALL_RUNS_JSON, "r") as f:
        return json.load(f)

def filter_runs(emulator=None, start_time=None, end_time=None):
    """
    Retrieve historical runs with optional filters.
    """
    all_runs = load_all_runs()
    filtered = []

    for run in all_runs:
        run_start = datetime.strptime(run["metadata"]["start_time"], "%Y-%m-%d %H:%M:%S")
        run_end = datetime.strptime(run["metadata"]["end_time"], "%Y-%m-%d %H:%M:%S")

        if emulator and run["metadata"]["emulator"].lower() != emulator.lower():
            continue
        if start_time and run_start < start_time:
            continue
        if end_time and run_end > end_time:
            continue

        filtered.append(run)
    return filtered

def compare_statistics(filtered_runs):
    """
    Compute comparative metrics from filtered runs.
    """
    comparison = []
    all_values = []

    for run in filtered_runs:
        summary = {
            "emulator": run["metadata"]["emulator"],
            "mean_current_a": run["mean_current_a"],
            "median_current_a": run["median_current_a"],
            "std_dev_current_a": run["std_dev_current_a"],
            "min_current_a": run["min_current_a"],
            "max_current_a": run["max_current_a"],
            "start_time": run["metadata"]["start_time"],
            "log_file": run["metadata"]["log_file"]
        }
        comparison.append(summary)
        # Add min, max, and mean of this run to the all_values list for overall stats
        all_values.extend([run["min_current_a"], run["max_current_a"]])

    if all_values:
        overall_summary = {
            "overall_min_current_a": min(all_values),
            "overall_max_current_a": max(all_values),
            "overall_mean_current_a": statistics.mean([r["mean_current_a"] for r in filtered_runs]),
            "overall_median_current_a": statistics.median([r["median_current_a"] for r in filtered_runs]),
            "overall_std_dev_current_a": statistics.stdev([r["mean_current_a"] for r in filtered_runs]) if len(
                filtered_runs) > 1 else 0.0
        }
    else:
        overall_summary = {}

    return comparison, overall_summary

