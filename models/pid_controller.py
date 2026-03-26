"""PID controller simulation for the TestEquity 123H.

Models the closed-loop temperature control response including:
- PID tuning parameters (Kp, Ki, Kd)
- Step response with overshoot and settling time
- Steady-state accuracy from integral action
"""

import math


class PIDController:
    def __init__(
        self,
        kp: float = 8.0,
        ki: float = 0.3,
        kd: float = 2.0,
        setpoint_c: float = 100.0,
        dt_s: float = 0.1,
        heater_power_w: float = 2500.0,
        chamber_mass_kg: float = 8.0,
        specific_heat: float = 500.0,
        heat_loss_w_per_k: float = 12.0,
    ):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint_c
        self.dt = dt_s
        self.heater_power = heater_power_w
        self.mass = chamber_mass_kg
        self.cp = specific_heat
        self.heat_loss = heat_loss_w_per_k

    def step_response(self, duration_s: float = 600.0, ambient_c: float = 25.0) -> dict:
        """Simulate closed-loop step response from ambient to setpoint.

        Returns time series and performance metrics.
        """
        steps = int(duration_s / self.dt)
        temp = [ambient_c]
        output = [0.0]
        error_integral = 0.0
        prev_error = self.setpoint - ambient_c

        for i in range(1, steps):
            error = self.setpoint - temp[-1]
            error_integral += error * self.dt
            # Anti-windup: clamp integral
            error_integral = max(-100, min(100, error_integral))
            derivative = (error - prev_error) / self.dt

            # PID output as heater duty cycle (0-100%)
            duty = self.kp * error + self.ki * error_integral + self.kd * derivative
            duty = max(0.0, min(100.0, duty))

            # Plant model: heater power modulated by duty cycle
            q_heater = self.heater_power * (duty / 100.0)
            q_loss = self.heat_loss * (temp[-1] - ambient_c)
            q_net = q_heater - q_loss
            dt_temp = (q_net / (self.mass * self.cp)) * self.dt
            temp.append(temp[-1] + dt_temp)
            output.append(duty)
            prev_error = error

        # Compute metrics
        peak = max(temp)
        overshoot_pct = ((peak - self.setpoint) / (self.setpoint - ambient_c)) * 100
        overshoot_pct = max(0, overshoot_pct)

        # Settling time: time to stay within ±0.5°C of setpoint
        settling_time = duration_s
        band = 0.5
        for i in range(len(temp) - 1, -1, -1):
            if abs(temp[i] - self.setpoint) > band:
                settling_time = (i + 1) * self.dt
                break

        # Steady-state error: average of last 10% of readings
        ss_window = temp[int(0.9 * len(temp)):]
        ss_error = abs(sum(ss_window) / len(ss_window) - self.setpoint)

        return {
            "time_s": [i * self.dt for i in range(len(temp))],
            "temperature_c": temp,
            "duty_pct": output,
            "peak_c": peak,
            "overshoot_pct": overshoot_pct,
            "settling_time_s": settling_time,
            "steady_state_error_c": ss_error,
            "steady_state_accuracy_c": ss_error,
        }

    def tuning_summary(self) -> dict:
        """Return PID tuning parameters and expected performance."""
        resp = self.step_response()
        return {
            "Kp": self.kp,
            "Ki": self.ki,
            "Kd": self.kd,
            "setpoint_c": self.setpoint,
            "overshoot_pct": resp["overshoot_pct"],
            "settling_time_s": resp["settling_time_s"],
            "steady_state_error_c": resp["steady_state_error_c"],
        }
