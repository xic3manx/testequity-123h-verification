"""R90/C90 Reliability Model — TestEquity 123H
Standalone model for Flow Engineering analysis.
"""

# ── Component MTBFs (hours) ──
sensor_mtbf = 50000.0
humidity_sensor_mtbf = 40000.0
relay_mtbf = 100000.0
compressor_mtbf = 30000.0
heater_mtbf = 60000.0

# ── Test data ──
total_test_hours = 2000000.0
observed_failures = 1

# ── Series reliability: system failure rate = sum of component rates ──
system_failure_rate = (1.0/sensor_mtbf + 1.0/humidity_sensor_mtbf + 1.0/relay_mtbf + 1.0/compressor_mtbf + 1.0/heater_mtbf)
system_mtbf = 1.0 / system_failure_rate

# ── Chi-squared lower bound on MTBF (90% confidence, 1 failure) ──
# chi2.ppf(0.90, dof=4) = 7.7794
chi2_val = 7.7794
mtbf_lower_bound = (2.0 * total_test_hours) / chi2_val

# ── R90/C90 life ──
# R(t) = 0.90 → t = -MTBF * ln(0.90) = MTBF * 0.10536
r90c90_factor = 0.10536
system_r90c90_hrs = mtbf_lower_bound * r90c90_factor
