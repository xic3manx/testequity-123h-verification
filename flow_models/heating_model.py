"""Heating Subsystem Model — TestEquity 123H
Standalone model for Flow Engineering analysis.
No external dependencies.

Inputs (from Flow design values):
  - heater_power_w: Resistive heater rated power (W)

Outputs (push back to Flow):
  - max_temp_achieved_c: Maximum achievable workspace temperature (°C)
  - heat_ramp_rate_actual: Average ramp rate 25→200°C (°C/min)
"""

import math

# ── Design parameters (overridden by Flow values at runtime) ──
heater_power_w = 2500.0
chamber_mass_kg = 8.0
specific_heat_j_kg_k = 500.0
heat_loss_w_per_k = 12.0
ambient_c = 25.0
target_c = 200.0

# ── Calculations ──
max_temp_achieved_c = ambient_c + heater_power_w / heat_loss_w_per_k

midpoint_c = (ambient_c + target_c) / 2
loss_at_midpoint = heat_loss_w_per_k * (midpoint_c - ambient_c)
net_power = heater_power_w - loss_at_midpoint
heat_ramp_rate_actual = (net_power / (chamber_mass_kg * specific_heat_j_kg_k)) * 60.0

time_to_target_min = (target_c - ambient_c) / heat_ramp_rate_actual
total_power_heater_w = heater_power_w

# ── Results ──
print(f"Max Temperature: {max_temp_achieved_c:.1f} °C")
print(f"Heat Ramp Rate: {heat_ramp_rate_actual:.2f} °C/min")
print(f"Time to {target_c}°C: {time_to_target_min:.1f} min")
print(f"Heater Power: {total_power_heater_w:.0f} W")
