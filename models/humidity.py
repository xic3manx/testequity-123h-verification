"""Humidity control subsystem model for the TestEquity 123H.

Computes achievable RH range and accuracy from steam injection
rate and sensor characteristics.
"""

import math


class HumidityModel:
    def __init__(
        self,
        steam_rate_g_per_min: float = 5.0,
        workspace_volume_l: float = 42.5,
        sensor_accuracy_pct: float = 1.5,
        control_band_pct: float = 0.8,
    ):
        self.steam_rate = steam_rate_g_per_min
        self.volume_l = workspace_volume_l
        self.sensor_accuracy = sensor_accuracy_pct
        self.control_band = control_band_pct

    @staticmethod
    def _saturation_pressure_kpa(temp_c: float) -> float:
        """Antoine equation for water saturation vapour pressure."""
        return 0.61078 * math.exp(17.27 * temp_c / (temp_c + 237.3))

    def max_rh_at_temp(self, temp_c: float = 25.0) -> float:
        """Maximum achievable RH (%) from steam injection."""
        sat_p = self._saturation_pressure_kpa(temp_c)
        # Steam can deliver ~97% at 25°C; drops at higher temps
        return min(97.0, 97.0 * (3.17 / sat_p))

    def min_rh_at_temp(self, temp_c: float = 25.0) -> float:
        """Minimum achievable RH (%) using desiccant drying."""
        return 18.0  # desiccant limited

    def humidity_accuracy_pct(self) -> float:
        """Combined accuracy (RSS of sensor + control band)."""
        return math.sqrt(self.sensor_accuracy ** 2 + self.control_band ** 2)
