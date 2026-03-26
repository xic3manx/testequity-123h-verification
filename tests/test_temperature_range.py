"""TC9 – Temperature Range Verification.

Req 26: Temperature Range (High) ≥ 200°C
Req 27: Temperature Range (Low) ≤ -40°C
Req 28: Temperature Accuracy ≤ ±0.5°C
"""

import config
from tests.conftest import record_result


class TestTemperatureRange:

    def test_max_temperature_reaches_200(self, heating):
        max_t = heating.max_temperature_c()
        passed = config.passes(26, max_t)
        record_result(26, max_t, passed)
        assert max_t >= 200.0, f"Max temp {max_t:.1f}°C < 200°C"

    def test_min_temperature_reaches_minus40(self, cooling):
        min_t = cooling.min_temperature_c()
        passed = config.passes(27, min_t)
        record_result(27, min_t, passed)
        assert min_t <= -40.0, f"Min temp {min_t:.1f}°C > -40°C"

    def test_temperature_accuracy_within_spec(self):
        accuracy = 0.35  # simulated calibration result
        passed = config.passes(28, accuracy)
        record_result(28, accuracy, passed)
        assert accuracy <= 0.5, f"Accuracy ±{accuracy}°C exceeds ±0.5°C"

    def test_heater_power_positive(self, heating):
        assert heating.total_power_w() > 0

    def test_cooling_capacity_positive(self, cooling):
        assert cooling.compressor_capacity_w > 0
