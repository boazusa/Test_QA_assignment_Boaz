import logging
import os
from datetime import datetime

class ColorFormatter(logging.Formatter):
    COLORS = {
        "GREENLEE": "\033[92m",   # ירוק
        "ENTES": "\033[93m",      # צהוב
        "CIRCUTOR": "\033[94m",   # כחול
        "RESET": "\033[0m",       # איפוס צבע
    }

    def format(self, record):
        msg = super().format(record)
        # בודק לפי שם האמולטור שהעברנו ב־logger.name
        if "greenlee" in record.name.lower():
            color = self.COLORS["GREENLEE"]
        elif "entes" in record.name.lower():
            color = self.COLORS["ENTES"]
        elif "circutor" in record.name.lower():
            color = self.COLORS["CIRCUTOR"]
        else:
            color = ""
        reset = self.COLORS["RESET"] if color else ""
        return f"{color}{msg}{reset}"

class TestLogger:
    def __init__(self, test_name: str):
        self._test_name = test_name
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """
        הגדרת הלוגר עם פורמט מותאם וכתיבה לקובץ
        """
        # יצירת תיקיית הלוגים
        log_dir = "results/logs"
        os.makedirs(log_dir, exist_ok=True)

        # הגדרת שם הקובץ עם תאריך ומזהה הבדיקה
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"{log_dir}/{timestamp}_{self._test_name}.log"

        # הגדרת הלוגר
        logger = logging.getLogger(f"test_{self._test_name}")
        # DEBUG log level
        logger.setLevel(logging.DEBUG)

        # File handler - print to file DEBUG level
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)

        # Adding colors to prints
        file_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s",
            "%H:%M:%S"
        )
        fh.setFormatter(file_formatter)

        # Stream handler - print to screen INFO log level and up
        sh = logging.StreamHandler()
        sh.setLevel(logging.INFO)
        color_formatter = ColorFormatter(
            "%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s",
            "%H:%M:%S"
        )
        sh.setFormatter(color_formatter)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s",
            "%H:%M:%S"
        )

        logger.addHandler(fh)
        # Prints to screen (in addition to logfile
        logger.addHandler(sh)

        return logger

    def info(self, message: str):
        self.logger.info(message)

    def error(self, message: str):
        self.logger.error(message)

    def debug(self, message: str):
        self.logger.debug(message)

    def warning(self, message: str):
        self.logger.warning(message)


