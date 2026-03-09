import random
import time
import statistics
from datetime import datetime
from src.utils.config import load_config
from Ammeters.client import get_current_from_ammeter

class AmmeterTestFramework:
    def __init__(self, config_path: str = "../config/config.yaml"):
        self.config = load_config(config_path)

    def get_measurement(self, ammeter_type: str) -> float:
        """
        מבצע מדידה אמיתית מהאמפרמטר לפי ההגדרות ב-config.yaml
        """
        conf = self.config.get("ammeters", {}).get(ammeter_type, {})
        if not conf:
            raise ValueError(f"No configuration found for ammeter {ammeter_type}")

        port = conf.get("port")
        command_str = conf.get("command", "")
        if not port or not command_str:
            raise ValueError(f"Port or command not defined for {ammeter_type} in config.yaml")

        command_bytes = command_str.encode()
        # קריאה אמיתית מהאמפרמטר דרך ה־socket (client.py)
        current = get_current_from_ammeter(port, command_bytes)
        return current

    def run_test(self, ammeter_type: str, samples: int = 20, duration: float = 3):
        """
        מבצע ריצה של מדידות עבור אמפרמטר נתון
        """
        measurements = [self.get_measurement(ammeter_type) for _ in range(samples)]
        mean_current = round(statistics.mean(measurements), 6)
        median_current = round(statistics.median(measurements), 6)
        std_dev_current = round(statistics.stdev(measurements) if len(measurements) > 1 else 0, 6)
        min_current = round(min(measurements), 6)
        max_current = round(max(measurements), 6)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        summary = {
            "emulator": ammeter_type,
            "total_measurements": samples,
            "mean_current_a": mean_current,
            "median_current_a": median_current,
            "std_dev_current_a": std_dev_current,
            "min_current_a": min_current,
            "max_current_a": max_current,
            "start_time": timestamp,
            "end_time": timestamp,
            "measurements": measurements
        }

        return summary