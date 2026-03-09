import os
import re
import statistics
import matplotlib.pyplot as plt

RESULTS_DIR = "../results"


def analyze_ammeter(ammeter):

    folder = os.path.join(RESULTS_DIR, ammeter.lower())

    measurements = []

    for file in os.listdir(folder):

        if not file.endswith(".log"):
            continue

        path = os.path.join(folder, file)

        with open(path) as f:
            for line in f:

                match = re.search(r'Measurement \d+: ([\d\.]+)', line)

                if match:
                    value = float(match.group(1))
                    measurements.append(value)

    if not measurements:
        print("No measurements found")
        return

    # -------- statistics --------

    mean_val = statistics.mean(measurements)
    median_val = statistics.median(measurements)
    std_val = statistics.stdev(measurements) if len(measurements) > 1 else 0

    print("\nAmmeter:", ammeter)
    print("Total measurements:", len(measurements))
    print("Mean:", round(mean_val,3))
    print("Median:", round(median_val,3))
    print("Std Dev:", round(std_val,3))

    # -------- plots --------

    fig, axs = plt.subplots(1, 3, figsize=(15,5))

    # Histogram
    axs[0].hist(measurements, bins=20)
    axs[0].set_title("Distribution")
    axs[0].set_xlabel("Current (A)")
    axs[0].set_ylabel("Frequency")

    # Time series
    axs[1].plot(measurements)
    axs[1].set_title("Measurements Over Time")
    axs[1].set_xlabel("Measurement #")
    axs[1].set_ylabel("Current (A)")

    # Boxplot
    axs[2].boxplot(measurements)
    axs[2].set_title("Spread")
    axs[2].set_ylabel("Current (A)")

    fig.suptitle(f"{ammeter} Ammeter Analysis", fontsize=14)

    plt.tight_layout()

    plt.show()


if __name__ == "__main__":
    analyze_ammeter("entes")
    analyze_ammeter("greenlee")
    analyze_ammeter("circutor")
