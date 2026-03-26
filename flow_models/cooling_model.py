"""Cooling Subsystem Model — TestEquity 123H
Standalone model for Flow Engineering analysis.
No external dependencies.

Inputs (from Flow design values):
  - compressor_capacity_w: Cooling capacity (W)

Outputs (push back to Flow):
  - min_temp_achieved_c: Minimum achievable workspace temperature (°C)
  - cool_rate_actual: Average cool-down rate (°C/min)
"""

# ── Design parameters ──
compressor_capacity_w = 1800.0
chamber_mass_kg = 8.0
specific_heat_j_kg_k = 500.0
ambient_heat_leak_w_per_k = 10.0
cop = 4.0
ambient_c = 25.0
start_c = 25.0
target_c = -40.0

# ── Calculations ──
min_temp_achieved_c = ambient_c - compressor_capacity_w / ambient_heat_leak_w_per_k

midpoint_c = (start_c + target_c) / 2
heat_leak_in = ambient_heat_leak_w_per_k * max(0, ambient_c - midpoint_c)
net_cooling = compressor_capacity_w - heat_leak_in
cool_rate_actual = (net_cooling / (chamber_mass_kg * specific_heat_j_kg_k)) * 60.0

compressor_power_draw_w = compressor_capacity_w / cop

# ── Results ──
print(f"Min Temperature: {min_temp_achieved_c:.1f} °C")
print(f"Cool-Down Rate: {cool_rate_actual:.2f} °C/min")
print(f"Compressor Power Draw: {compressor_power_draw_w:.0f} W")
