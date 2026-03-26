"""Power Budget Model — TestEquity 123H
Standalone model for Flow Engineering analysis.
No external dependencies.

Inputs (from Flow design values):
  - heater_power_w
  - compressor_capacity_w

Outputs:
  - total_power_actual_w: Total system power consumption
"""

# ── Design parameters ──
heater_power_w = 2500.0
compressor_capacity_w = 1800.0
cop = 4.0
controls_power_w = 50.0  # PID controller + sensors + HMI

# ── Calculations ──
compressor_electrical_w = compressor_capacity_w / cop
total_power_actual_w = heater_power_w + compressor_electrical_w + controls_power_w

# ── Results ──
print(f"Heater: {heater_power_w:.0f} W")
print(f"Compressor: {compressor_electrical_w:.0f} W (COP={cop})")
print(f"Controls: {controls_power_w:.0f} W")
print(f"Total: {total_power_actual_w:.0f} W")
print(f"Budget: 3000 W")
print(f"Margin: {3000 - total_power_actual_w:.0f} W")
print(f"{'PASS' if total_power_actual_w <= 3000 else 'FAIL'}")
