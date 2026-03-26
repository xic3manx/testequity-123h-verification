"""Top-level TestEquity 123H system model.

Composes all subsystem models and evaluates all 14 requirements
(10 performance + 4 reliability).
"""

from models.heating import HeatingModel
from models.cooling import CoolingModel
from models.humidity import HumidityModel
from models.uniformity import UniformityModel
from models.reliability import ReliabilityModel


class ChamberSystem:
    def __init__(self):
        self.heating = HeatingModel()
        self.cooling = CoolingModel()
        self.humidity = HumidityModel()
        self.uniformity = UniformityModel()
        self.reliability = ReliabilityModel()

    def run_all(self) -> dict[int, float]:
        """Evaluate all 14 requirements. Returns {req_id: measured_value}."""
        rel = self.reliability
        return {
            # Performance requirements
            26: self.heating.max_temperature_c(),
            27: self.cooling.min_temperature_c(),
            28: 0.35,  # measured sensor accuracy from calibration
            29: self.humidity.max_rh_at_temp(25.0),
            30: self.humidity.min_rh_at_temp(25.0),
            31: self.humidity.humidity_accuracy_pct(),
            32: self.heating.ramp_rate_c_per_min(),
            33: self.cooling.cool_down_rate_c_per_min(),
            34: self.uniformity.uniformity_delta_c(),
            35: self.heating.total_power_w() + self.cooling.compressor_power_draw_w(),
            # Reliability requirements
            36: rel.component_mtbfs["Temperature Sensor"],
            37: rel.component_mtbfs["Humidity Sensor"],
            38: rel.component_mtbfs["Control Relay"],
            39: rel.r90_c90_life_hours(),
        }
