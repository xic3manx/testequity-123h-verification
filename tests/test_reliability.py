"""Reliability verification — R90/C90 roll-up from component MTBFs.

Req 36: Temperature Sensor MTBF ≥ 50,000 hrs
Req 37: Humidity Sensor MTBF ≥ 40,000 hrs
Req 38: Control Relay MTBF ≥ 100,000 hrs
Req 39: System R90/C90 Life ≥ 20,000 hrs
"""

import config
from models.reliability import ReliabilityModel
from tests.conftest import record_result


class TestComponentMTBF:

    def test_temp_sensor_mtbf(self, chamber):
        mtbf = chamber.reliability.component_mtbfs["Temperature Sensor"]
        passed = config.passes(36, mtbf)
        record_result(36, mtbf, passed)
        assert mtbf >= 50_000, f"Temp sensor MTBF {mtbf} < 50,000 hrs"

    def test_humidity_sensor_mtbf(self, chamber):
        mtbf = chamber.reliability.component_mtbfs["Humidity Sensor"]
        passed = config.passes(37, mtbf)
        record_result(37, mtbf, passed)
        assert mtbf >= 40_000, f"Humidity sensor MTBF {mtbf} < 40,000 hrs"

    def test_relay_mtbf(self, chamber):
        mtbf = chamber.reliability.component_mtbfs["Control Relay"]
        passed = config.passes(38, mtbf)
        record_result(38, mtbf, passed)
        assert mtbf >= 100_000, f"Relay MTBF {mtbf} < 100,000 hrs"


class TestSystemReliability:

    def test_r90_c90_exceeds_20k_hours(self, chamber):
        r90c90 = chamber.reliability.r90_c90_life_hours()
        passed = config.passes(39, r90c90)
        record_result(39, r90c90, passed)
        assert r90c90 >= 20_000, f"R90/C90 = {r90c90:.0f} hrs < 20,000 hrs"

    def test_system_mtbf_greater_than_min_component(self, chamber):
        """System MTBF should be less than the weakest component (series model)."""
        sys_mtbf = chamber.reliability.system_mtbf()
        min_comp = min(chamber.reliability.component_mtbfs.values())
        assert sys_mtbf < min_comp, "Series system MTBF must be < weakest link"

    def test_reliability_decreases_over_time(self, chamber):
        r_1yr = chamber.reliability.system_reliability(8_760)
        r_3yr = chamber.reliability.system_reliability(26_280)
        assert r_3yr < r_1yr, "Reliability should decrease over time"

    def test_reliability_summary_structure(self, chamber):
        s = chamber.reliability.summary()
        assert "system_mtbf_hrs" in s
        assert "r90_c90_life_hrs" in s
        assert "passed" in s
        assert isinstance(s["component_mtbfs"], dict)
