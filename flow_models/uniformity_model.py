"""Temperature Uniformity Model — TestEquity 123H
Standalone model for Flow Engineering analysis.
No external dependencies.

Outputs (push back to Flow):
  - uniformity_delta_actual_c: Max temperature spread across 9-point grid
"""

# ── Design parameters ──
airflow_speed_m_s = 2.0
chamber_height_m = 0.35
heater_symmetry = 0.85  # 1.0 = perfect symmetry
setpoint_c = 100.0

# ── Calculations ──
base_gradient = 2.0 * (chamber_height_m / airflow_speed_m_s)
uniformity_delta_actual_c = base_gradient * (1.0 - heater_symmetry) + 0.3

# ── Results ──
print(f"Uniformity Delta: {uniformity_delta_actual_c:.2f} °C")
print(f"Requirement: <= 1.0 °C")
print(f"PASS" if uniformity_delta_actual_c <= 1.0 else "FAIL")
