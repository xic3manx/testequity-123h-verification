# Temperature Uniformity Model — TestEquity 123H
# Inputs: Flow design values (VAL)
# Outputs: Model values (MOD) — Flow captures these automatically

# ── INPUTS (mapped from Flow Design Values) ──
airflow_speed_m_s = 2.0       # could be linked to a VAL
chamber_height_m = 0.35       # from Onshape CAD model
heater_symmetry = 0.85        # design parameter

# ── CALCULATION ──
base_gradient = 2.0 * (chamber_height_m / airflow_speed_m_s)
uniformity_delta_c = base_gradient * (1.0 - heater_symmetry) + 0.3

# ── OUTPUTS (Flow captures as MOD values) ──
# uniformity_delta_c → this becomes a MOD value
# Flow checks: uniformity_delta_c <= 1.0°C (Req 34)
