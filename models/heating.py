"""Heating subsystem model for the TestEquity 123H.

Given heater power and chamber thermal mass, computes ramp rate,
time to temperature, and maximum achievable temperature.
"""


class HeatingModel:
    def __init__(
        self,
        heater_power_w: float = 2500.0,
        chamber_mass_kg: float = 8.0,
        specific_heat_j_kg_k: float = 500.0,
        heat_loss_w_per_k: float = 12.0,
    ):
        self.heater_power_w = heater_power_w
        self.chamber_mass_kg = chamber_mass_kg
        self.specific_heat = specific_heat_j_kg_k
        self.heat_loss = heat_loss_w_per_k

    def max_temperature_c(self, ambient_c: float = 25.0) -> float:
        """Steady-state max temperature where heater power = losses."""
        return ambient_c + self.heater_power_w / self.heat_loss

    def ramp_rate_c_per_min(self, target_c: float = 200.0, ambient_c: float = 25.0) -> float:
        """Average heating ramp rate in °C/min."""
        midpoint_c = (ambient_c + target_c) / 2
        loss_at_midpoint = self.heat_loss * (midpoint_c - ambient_c)
        net_power = self.heater_power_w - loss_at_midpoint
        rate_per_sec = net_power / (self.chamber_mass_kg * self.specific_heat)
        return rate_per_sec * 60.0

    def time_to_temperature_min(self, target_c: float = 200.0, ambient_c: float = 25.0) -> float:
        """Approximate time to reach target from ambient."""
        return (target_c - ambient_c) / self.ramp_rate_c_per_min(target_c, ambient_c)

    def total_power_w(self) -> float:
        return self.heater_power_w
