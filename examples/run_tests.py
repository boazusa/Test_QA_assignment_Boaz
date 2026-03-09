# run_tests_with_emulators.py
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




def main():
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
    ammeter_types = ["greenlee", "entes", "circutor"]
    all_results = []

    for ammeter in ammeter_types:
        print(f"\nRunning test for {ammeter}...")
        result = framework.run_test(ammeter)
        all_results.append(result)
        print(f"Summary for {ammeter}:")
        print(result)

    # Save to json file
    with open(RESULTS_JSON, "w") as f:
        json.dump(all_results, f, indent=4)

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
