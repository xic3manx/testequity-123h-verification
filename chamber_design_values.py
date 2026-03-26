"""Design values for TestEquity 123H Environmental Test Chamber.

Each value represents a measurable design parameter that can be
synced with Flow Engineering via the values API.
"""

# -- Temperature --
max_temperature_c = 200.0           # °C  — heater design target
min_temperature_c = -40.0           # °C  — compressor design target
temperature_accuracy_c = 0.5        # ±°C — controller steady-state band

# -- Humidity --
humidity_range_min_pct = 20.0       # %RH — desiccant-limited floor
humidity_range_max_pct = 95.0       # %RH — steam-injection ceiling
humidity_accuracy_pct = 2.0         # ±%RH — sensor + control band

# -- Performance --
heater_power_w = 2500.0             # W   — resistive heater rating
compressor_capacity_w = 1800.0      # W   — refrigeration cooling capacity
workspace_volume_cuft = 1.5         # ft³ — usable test volume
pid_setpoint_resolution_c = 0.1     # °C  — controller display resolution
