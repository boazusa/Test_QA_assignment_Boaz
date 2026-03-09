import threading
import time
from datetime import datetime

from Ammeters.Circutor_Ammeter import CircutorAmmeter
from Ammeters.Entes_Ammeter import EntesAmmeter
from Ammeters.Greenlee_Ammeter import GreenleeAmmeter
from Ammeters.client import sample_measurements, filter_runs, compare_statistics, request_current_from_ammeter, load_all_runs


# modified the run_*_emulator functions to start servers in threads so they can be stopped
# and the threads can be finished before the end of execution (and not hang forever and hold the application up)

# Creation of ammeter objects:
greenlee = GreenleeAmmeter(5000)    # port shift, 5000 and not 5001 according to README.md
entes = EntesAmmeter(5001)          # port shift, 5001 and not 5002 according to README.md
circutor = CircutorAmmeter(5002)    # port shift, 5002 and not 5003 according to README.md


if __name__ == "__main__":

    # start servers in separate threads, and get handles of the threads so they can be join()ed latter
    greenlee_thread = threading.Thread(target=greenlee.start_server)
    entes_thread = threading.Thread(target=entes.start_server)
    circutor_thread = threading.Thread(target=circutor.start_server)

    # start
    greenlee_thread.start()
    entes_thread.start()
    circutor_thread.start()

    time.sleep(5)  # לתת זמן לשרתים להתחיל

    # The function request_current_from_ammeter is implemented in sample_measurements using an equivalent function
    # that also returns measurements, not just prints them. See sample_measurements in the following lines.

    # request_current_from_ammeter(5000, b'MEASURE_GREENLEE')
    # request_current_from_ammeter(5001, b'MEASURE_ENTES')
    # request_current_from_ammeter(5002, b'MEASURE_CIRCUTOR')

    # 2. Measurement Sampling & 3. Result Analysis

    greenlee_samples = sample_measurements(5000, b'MEASURE_GREENLEE -get_measurement', 'Greenlee', samples=49, duration=3)
    print(f"greenlee_emulator measurements: {greenlee_samples}")

    entes_samples = sample_measurements(5001, b'MEASURE_ENTES -get_data', 'Entes', samples=47, duration=3)
    print(f"entes_emulator measurements: {entes_samples}")

    circutor_samples = sample_measurements(5002, b'MEASURE_CIRCUTOR -get_measurement', 'Circutor', samples=59, duration=3)
    print(f"circutor_emulator measurements: {circutor_samples}")

    # End emulators, Stop servers
    greenlee.stop_server()
    entes.stop_server()
    circutor.stop_server()

    # Wait until Emulators are finished
    greenlee_thread.join()
    entes_thread.join()
    circutor_thread.join()

    # ---------------------------------------------------------------------------------------------------------------------
    # filtering all "Greenlee" runs
    greenlee_runs = filter_runs(emulator="Greenlee")

    print(f"Greenlee runs: {greenlee_runs}")

    # Example: Filtering runs between two dates
    start = datetime(2026, 3, 8, 0, 0, 0)
    end = datetime(2026, 3, 9, 23, 59, 59)
    filtered_runs = filter_runs(start_time=start, end_time=end)

    # Can also combine: emulator + time range
    greenlee_filtered = filter_runs(emulator="Greenlee", start_time=start, end_time=end)

    print(f"Found {len(greenlee_filtered)} Greenlee runs in the time range")

    comparison, overall_summary = compare_statistics(greenlee_filtered)
    print(f"greenlee all runs comparison: {comparison}")
    print(f"greenlee compare statistics:{overall_summary}")

