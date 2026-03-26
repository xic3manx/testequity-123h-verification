"""TC11 – Ramp Rate Performance Test.

Req 32: Heat Ramp Rate ≥ 5°C/min
Req 33: Cool-Down Rate ≥ 3°C/min
"""

import config
from tests.conftest import record_result


class TestRampRate:

    def test_heat_ramp_rate_exceeds_5(self, heating):
        rate = heating.ramp_rate_c_per_min()
        passed = config.passes(32, rate)
        record_result(32, rate, passed)
        assert rate >= 5.0, f"Heat ramp {rate:.2f}°C/min < 5°C/min"

    def test_cool_down_rate_exceeds_3(self, cooling):
        rate = cooling.cool_down_rate_c_per_min()
        passed = config.passes(33, rate)
        record_result(33, rate, passed)
        assert rate >= 3.0, f"Cool-down {rate:.2f}°C/min < 3°C/min"

    def test_time_to_200c_under_60min(self, heating):
        t = heating.time_to_temperature_min()
        assert t < 60.0, f"Time to 200°C is {t:.1f} min — too slow"

    def test_ramp_rate_positive(self, heating):
        assert heating.ramp_rate_c_per_min() > 0
