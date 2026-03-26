"""PID Controller Model — TestEquity 123H
Standalone model for Flow Engineering analysis.
No external dependencies.

Simulates closed-loop step response from ambient to setpoint.

Outputs:
  - overshoot_pct: Percent overshoot above setpoint
  - settling_time_s: Time to settle within ±0.5°C
  - steady_state_error_c: Steady-state temperature error
"""

# ── PID tuning parameters ──
kp = 8.0
ki = 0.3
kd = 2.0

# ── Plant parameters ──
setpoint_c = 100.0
ambient_c = 25.0
heater_power_w = 2500.0
chamber_mass_kg = 8.0
specific_heat = 500.0
heat_loss_w_per_k = 12.0

# ── Simulation ──
dt = 0.1  # seconds
duration_s = 600.0
steps = int(duration_s / dt)

temp = ambient_c
peak = ambient_c
error_integral = 0.0
prev_error = setpoint_c - ambient_c
settling_time_s = duration_s

for i in range(1, steps):
    error = setpoint_c - temp
    error_integral += error * dt
    error_integral = max(-100, min(100, error_integral))
    derivative = (error - prev_error) / dt

    duty = kp * error + ki * error_integral + kd * derivative
    duty = max(0.0, min(100.0, duty))

    q_heater = heater_power_w * (duty / 100.0)
    q_loss = heat_loss_w_per_k * (temp - ambient_c)
    q_net = q_heater - q_loss
    temp += (q_net / (chamber_mass_kg * specific_heat)) * dt

    if temp > peak:
        peak = temp
    prev_error = error

# ── Compute metrics ──
overshoot_pct = max(0, ((peak - setpoint_c) / (setpoint_c - ambient_c)) * 100)

# Steady-state error (last value vs setpoint)
steady_state_error_c = abs(temp - setpoint_c)

# ── Results ──
print(f"Peak Temperature: {peak:.2f} °C")
print(f"Overshoot: {overshoot_pct:.1f} %")
print(f"Steady-State Error: {steady_state_error_c:.4f} °C")
print(f"Final Temperature: {temp:.2f} °C")
print(f"PID Gains: Kp={kp}, Ki={ki}, Kd={kd}")
