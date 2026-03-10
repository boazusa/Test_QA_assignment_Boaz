import socket
import time
import random
from abc import ABC, abstractmethod
from src.utils.logger import TestLogger  # log file setup
import threading

class AmmeterEmulatorBase(ABC):
    port_loggers = {}

    def __init__(self, port: int, name: str):
        self.port = port
        # May be removed as it does not affect code and the random seeds are being generated from src.utils.Utils
        random.seed(time.time())
        # each emulator get logger by name
        self.logger = TestLogger(name).logger
        AmmeterEmulatorBase.port_loggers[self.port] = self.logger
        self.name = name
        self._running = threading.Event()  # for implementing the stop_server

    def start_server(self):
        """
        Starts the server to listen for client requests.
        The server will run indefinitely, handling one client request at a time.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', self.port))
            s.listen()
            s.settimeout(1.0)  # 🔹 timeout כדי לאפשר shutdown
            self._running.set()  # start running
            self.logger.info(f"{self.__class__.__name__} is running on port {self.port}")

            while self._running.is_set():
                try:
                    conn, addr = s.accept()
                except socket.timeout:
                    continue  # 🔹 חזור לבדוק אם צריך לעצור
                with conn:
                    self.logger.info(f"Connected by {addr}")
                    data = conn.recv(1024)
                    if data == self.get_current_command:
                        current = self.measure_current()
                        conn.sendall(str(current).encode('utf-8'))

        print(f"{self.name} server stopped.")

    def stop_server(self):
        """Stop the running server gracefully."""
        self.logger.info(f"Stopping {self.__class__.__name__} server on port {self.port}")
        self._running.clear()

    @property
    @abstractmethod
    def get_current_command(self) -> bytes:
        """
        This property must be implemented by each subclass to provide the specific
        command to get the current measurement.
        """
        raise NotImplementedError("Subclasses must implement this property.")

    @abstractmethod
    def measure_current(self) -> float:
        """
        This method must be implemented by each subclass to provide the specific
        logic for current measurement.
        """
        raise NotImplementedError("Subclasses must implement this method.")
