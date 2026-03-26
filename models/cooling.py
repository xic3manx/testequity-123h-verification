"""Cooling subsystem model for the TestEquity 123H.

Given compressor capacity and chamber thermal mass, computes
cool-down rate and minimum achievable temperature.
"""


class CoolingModel:
    def __init__(
        self,
        compressor_capacity_w: float = 1800.0,
        chamber_mass_kg: float = 8.0,
        specific_heat_j_kg_k: float = 500.0,
        ambient_heat_leak_w_per_k: float = 10.0,
        cop: float = 4.0,
    ):
        self.compressor_capacity_w = compressor_capacity_w
        self.chamber_mass_kg = chamber_mass_kg
        self.specific_heat = specific_heat_j_kg_k
        self.heat_leak = ambient_heat_leak_w_per_k
        self.cop = cop

    def min_temperature_c(self, ambient_c: float = 25.0) -> float:
        """Steady-state minimum where cooling = heat leak."""
        return ambient_c - self.compressor_capacity_w / self.heat_leak

    def cool_down_rate_c_per_min(self, start_c: float = 25.0, target_c: float = -40.0) -> float:
        """Average cooling rate in °C/min."""
        midpoint_c = (start_c + target_c) / 2
        heat_leak_in = self.heat_leak * max(0, 25.0 - midpoint_c)
        net_cooling = self.compressor_capacity_w - heat_leak_in
        rate_per_sec = net_cooling / (self.chamber_mass_kg * self.specific_heat)
        return rate_per_sec * 60.0

    def compressor_power_draw_w(self) -> float:
        """Electrical power draw (capacity / COP)."""
        return self.compressor_capacity_w / self.cop
