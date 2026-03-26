"""TC12 – Temperature Uniformity Mapping + Power Consumption.

Req 34: Temperature Uniformity ≤ ±1.0°C
Req 35: Power Consumption ≤ 3000 W
"""

import config
from tests.conftest import record_result


class TestUniformity:

    def test_uniformity_within_1c(self, uniformity):
        delta = uniformity.uniformity_delta_c()
        passed = config.passes(34, delta)
        record_result(34, delta, passed)
        assert delta <= 1.0, f"Uniformity delta {delta:.2f}°C > 1.0°C"

    def test_uniformity_improves_with_higher_airflow(self, uniformity):
        original = uniformity.airflow_speed
        low = UniformityModel(airflow_speed_m_s=1.0).uniformity_delta_c()
        high = uniformity.uniformity_delta_c()
        assert high < low, "Higher airflow should reduce temperature spread"

    def test_power_consumption_within_budget(self, chamber):
        results = chamber.run_all()
        power = results[35]
        passed = config.passes(35, power)
        record_result(35, power, passed)
        assert power <= 3000.0, f"Power {power:.0f} W exceeds 3000 W limit"


# Need the import for the parametric test
from models.uniformity import UniformityModel
