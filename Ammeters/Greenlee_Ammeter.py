from Ammeters.base_ammeter import AmmeterEmulatorBase
from src.utils.Utils import generate_random_float

class GreenleeAmmeter(AmmeterEmulatorBase):
    def __init__(self, port: int):
        super().__init__(port, "greenlee")

    @property
    def get_current_command(self) -> bytes:
        return b'MEASURE_GREENLEE -get_measurement'

    def measure_current(self) -> float:
        voltage = generate_random_float(1.0, 10.0)
        resistance = generate_random_float(0.1, 100.0)
        current = voltage / resistance
        self.logger.info(f"Greenlee Ammeter - Voltage: {voltage}V, Resistance: {resistance}Ω, Current: {current}A")
        return current
