"""Temperature uniformity model for the chamber enclosure.

Estimates workspace temperature delta based on airflow and
heater placement symmetry.
"""


class UniformityModel:
    def __init__(
        self,
        airflow_speed_m_s: float = 2.0,
        chamber_height_m: float = 0.35,
        heater_symmetry: float = 0.85,
    ):
        self.airflow_speed = airflow_speed_m_s
        self.chamber_height = chamber_height_m
        self.heater_symmetry = heater_symmetry

    def uniformity_delta_c(self, setpoint_c: float = 100.0) -> float:
        """Max temperature spread across 9-point grid (°C).

        Higher airflow and better heater symmetry reduce the gradient.
        """
        base_gradient = 2.0 * (self.chamber_height / self.airflow_speed)
        return base_gradient * (1.0 - self.heater_symmetry) + 0.3
