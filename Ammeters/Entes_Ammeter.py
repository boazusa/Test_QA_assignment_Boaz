from Ammeters.base_ammeter import AmmeterEmulatorBase
from src.utils.Utils import generate_random_float

class EntesAmmeter(AmmeterEmulatorBase):
    def __init__(self, port: int):
        super().__init__(port, "entes")  # שם ללוגר

    @property
    def get_current_command(self) -> bytes:
        return b'MEASURE_ENTES -get_data'

    def measure_current(self) -> float:
        magnetic_field = generate_random_float(0.01, 0.1)  # T
        calibration_factor = generate_random_float(500, 2000)
        current = magnetic_field * calibration_factor
        self.logger.info(
            f"ENTES Ammeter - Magnetic Field: {magnetic_field}T, "
            f"Calibration Factor: {calibration_factor}, Current: {current}A"
        )
        return current
