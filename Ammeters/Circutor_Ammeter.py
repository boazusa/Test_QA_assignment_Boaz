from Ammeters.base_ammeter import AmmeterEmulatorBase
from src.utils.Utils import generate_random_float

class CircutorAmmeter(AmmeterEmulatorBase):
    def __init__(self, port: int):
        super().__init__(port, "circutor")  # שם ללוגר

    @property
    def get_current_command(self) -> bytes:
        return b'MEASURE_CIRCUTOR -get_measurement'

    def measure_current(self) -> float:
        num_samples = 10
        time_step = generate_random_float(0.001, 0.01)
        voltages = [generate_random_float(0.1, 1.0) for _ in range(num_samples)]
        self.logger.info(
            f"CIRCUTOR Ammeter - Voltages: {voltages}, Time Step: {time_step}s"
        )
        current = sum(v * time_step for v in voltages)
        self.logger.info(f"CIRCUTOR Current: {current}A")  # במקום print
        return current