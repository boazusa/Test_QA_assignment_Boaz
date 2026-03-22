# run_tests_with_emulators.py
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.testing.test_framework import AmmeterTestFramework
from Ammeters.Greenlee_Ammeter import GreenleeAmmeter
from Ammeters.Entes_Ammeter import EntesAmmeter
from Ammeters.Circutor_Ammeter import CircutorAmmeter
import threading
import json
from pathlib import Path
import time

RESULTS_JSON = Path("results/all_runs.json")
RESULTS_JSON.parent.mkdir(exist_ok=True)


def main(_ammeter=None, _num_of_samples=40):
    # Creation of ammeter objects:
    greenlee = GreenleeAmmeter(5000)
    entes = EntesAmmeter(5001)
    circutor = CircutorAmmeter(5002)

    # Create start servers threads
    threads = [
        threading.Thread(target=greenlee.start_server),
        threading.Thread(target=entes.start_server),
        threading.Thread(target=circutor.start_server),
    ]

    # Strat threads
    for t in threads:
        t.start()

    # Wait until the ammeter threads start
    time.sleep(3)

    # --- הרצת הבדיקות ---
    framework = AmmeterTestFramework()
    if not _ammeter:
        ammeter_types = ["greenlee", "entes", "circutor"]
    else:
        ammeter_types = [_ammeter]
    all_results = []

    for ammeter in ammeter_types:
        print(f"\nRunning test for {ammeter}...")
        result = framework.run_test(ammeter, _num_of_samples)
        all_results.append(result)
        print(f"Summary for {ammeter}:")
        print(result)

    # --- Load existing results if file exists ---
    if RESULTS_JSON.exists():
        with open(RESULTS_JSON, "r") as f:
            try:
                existing_results = json.load(f)
            except json.JSONDecodeError:
                existing_results = []
    else:
        existing_results = []

    # --- Append new results ---
    existing_results.extend(all_results)

    # --- Save back to file ---
    with open(RESULTS_JSON, "w") as f:
        json.dump(existing_results, f, indent=4)

    print(f"\nAll results appended to {RESULTS_JSON}")

    print(f"\nAll results saved to {RESULTS_JSON}")

    # Stop emulators servers
    greenlee.stop_server()
    entes.stop_server()
    circutor.stop_server()

    # Wait until all threads are finished
    for t in threads:
        t.join()

    print("\nAll emulators finished.")


if __name__ == "__main__":
    main()
