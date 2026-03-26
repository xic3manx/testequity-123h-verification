"""R90/C90 Reliability Model — TestEquity 123H
Standalone model for Flow Engineering analysis.
No external dependencies (uses manual chi-squared lookup instead of scipy).

Inputs (from Flow design values):
  - sensor_mtbf_hrs
  - relay_mtbf_hrs
  - compressor_mtbf_hrs

Outputs (push back to Flow):
  - system_r90c90_hrs: System R90/C90 life prediction
"""

import math

# ── Design parameters (overridden by Flow values at runtime) ──
component_mtbfs = {
    "Temperature Sensor": 50000.0,
    "Humidity Sensor": 40000.0,
    "Control Relay": 100000.0,
    "Compressor": 30000.0,
    "Heater Element": 60000.0,
}

total_system_test_hours = 2000000.0
observed_failures = 1
confidence = 0.90
reliability_target = 0.90

# ── Chi-squared lookup (avoids scipy dependency) ──
# chi2.ppf(0.90, dof) for common dof values
CHI2_TABLE_90 = {
    2: 4.6052,   # 0 failures: dof = 2*(0+1) = 2
    4: 7.7794,   # 1 failure:  dof = 2*(1+1) = 4
    6: 10.6446,  # 2 failures
    8: 13.3616,  # 3 failures
    10: 15.9872, # 4 failures
}

# ── Calculations ──

# Series model: system failure rate = sum of component failure rates
system_failure_rate = sum(1.0 / m for m in component_mtbfs.values())
system_mtbf_hrs = 1.0 / system_failure_rate

# R90 life (nominal): time where R(t) = 0.90
r90_nominal_hrs = -system_mtbf_hrs * math.log(reliability_target)

# Chi-squared lower bound on MTBF from test data
dof = 2 * (observed_failures + 1)
chi2_val = CHI2_TABLE_90.get(dof, 4.6052)
mtbf_lower_bound = (2 * total_system_test_hours) / chi2_val

# R90/C90: R90 using the lower-bound MTBF
system_r90c90_hrs = -mtbf_lower_bound * math.log(reliability_target)

# ── Results ──
print(f"System MTBF (series): {system_mtbf_hrs:,.0f} hrs")
print(f"MTBF Lower Bound (90% CL): {mtbf_lower_bound:,.0f} hrs")
print(f"R90 Life (nominal): {r90_nominal_hrs:,.0f} hrs")
print(f"R90/C90 Life: {system_r90c90_hrs:,.0f} hrs")
print(f"Target: 20,000 hrs")
print(f"{'PASS' if system_r90c90_hrs >= 20000 else 'FAIL'}")
