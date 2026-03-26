"""Humidity Control Model — TestEquity 123H
Standalone model for Flow Engineering analysis.
No external dependencies.

Outputs (push back to Flow):
  - max_rh_achieved_pct: Maximum achievable RH at 25°C
  - min_rh_achieved_pct: Minimum achievable RH at 25°C
  - humidity_accuracy_measured_pct: Combined accuracy (sensor + control band)
"""

import math

# ── Design parameters ──
steam_rate_g_per_min = 5.0
workspace_volume_l = 42.5
sensor_accuracy_pct = 1.5
control_band_pct = 0.8
temp_c = 25.0

# ── Calculations ──

# Antoine equation for saturation vapor pressure
sat_pressure_kpa = 0.61078 * math.exp(17.27 * temp_c / (temp_c + 237.3))

# Max RH from steam injection capacity
max_rh_achieved_pct = min(97.0, 97.0 * (3.17 / sat_pressure_kpa))

# Min RH from desiccant drying
min_rh_achieved_pct = 18.0

# Combined accuracy (RSS)
humidity_accuracy_measured_pct = math.sqrt(sensor_accuracy_pct**2 + control_band_pct**2)

# ── Results ──
print(f"Max RH: {max_rh_achieved_pct:.1f} %RH")
print(f"Min RH: {min_rh_achieved_pct:.1f} %RH")
print(f"Humidity Accuracy: ±{humidity_accuracy_measured_pct:.2f} %RH")
