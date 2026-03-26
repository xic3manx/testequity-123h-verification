"""TC10 – Humidity Accuracy Test.

Req 29: Humidity Range (High) ≥ 95% RH
Req 30: Humidity Range (Low) ≤ 20% RH
Req 31: Humidity Accuracy ≤ ±2.0% RH
"""

import pytest
import config
from tests.conftest import record_result


class TestHumidity:

    def test_max_rh_exceeds_95(self, humidity):
        rh = humidity.max_rh_at_temp(25.0)
        passed = config.passes(29, rh)
        record_result(29, rh, passed)
        assert rh >= 95.0, f"Max RH {rh:.1f}% < 95%"

    def test_min_rh_below_20(self, humidity):
        rh = humidity.min_rh_at_temp(25.0)
        passed = config.passes(30, rh)
        record_result(30, rh, passed)
        assert rh <= 20.0, f"Min RH {rh:.1f}% > 20%"

    def test_humidity_accuracy_within_2pct(self, humidity):
        acc = humidity.humidity_accuracy_pct()
        passed = config.passes(31, acc)
        record_result(31, acc, passed)
        assert acc <= 2.0, f"Humidity accuracy ±{acc:.2f}% exceeds ±2.0%"

    @pytest.mark.parametrize("temp_c", [25, 50, 80])
    def test_max_rh_positive_at_temperature(self, humidity, temp_c):
        rh = humidity.max_rh_at_temp(temp_c)
        assert rh > 0, f"Max RH should be positive at {temp_c}°C"
