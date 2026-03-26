"""Hardware reliability model — R90/C90 roll-up.

Computes system-level reliability from component MTBF values using:
  1. Exponential reliability: R(t) = e^(-t/MTBF)
  2. Series model: 1/MTBF_sys = Σ(1/MTBF_i)
  3. Chi-squared confidence bound: MTBF_lower = 2T / χ²(2r+2, α)
  4. R90/C90: time where system R(t) ≥ 0.90 with 90% confidence
"""

import math
from scipy.stats import chi2


class ReliabilityModel:
    def __init__(
        self,
        component_mtbfs: dict[str, float] | None = None,
        total_system_test_hours: float = 2_000_000.0,
        observed_failures: int = 1,
        confidence: float = 0.90,
        reliability_target: float = 0.90,
    ):
        self.component_mtbfs = component_mtbfs or {
            "Temperature Sensor":  50_000.0,
            "Humidity Sensor":     40_000.0,
            "Control Relay":      100_000.0,
            "Compressor":          30_000.0,
            "Heater Element":      60_000.0,
        }
        self.total_test_hours = total_system_test_hours
        self.observed_failures = observed_failures
        self.confidence = confidence
        self.reliability_target = reliability_target

    # -- Component level ---------------------------------------------------

    def component_reliability(self, mtbf: float, time_hrs: float) -> float:
        """R(t) = e^(-t/MTBF)."""
        return math.exp(-time_hrs / mtbf)

    # -- System level (series) ---------------------------------------------

    def system_failure_rate(self) -> float:
        """λ_sys = Σ(1/MTBF_i) — series model."""
        return sum(1.0 / m for m in self.component_mtbfs.values())

    def system_mtbf(self) -> float:
        """MTBF_sys = 1 / λ_sys."""
        return 1.0 / self.system_failure_rate()

    def system_reliability(self, time_hrs: float) -> float:
        """R_sys(t) = e^(-λ_sys * t)."""
        return math.exp(-self.system_failure_rate() * time_hrs)

    # -- Confidence bounds -------------------------------------------------

    def system_mtbf_lower_bound(self) -> float:
        """Lower confidence bound on system MTBF from test data.

        MTBF_lower = 2T / χ²(2r+2, α)
        T = total system test hours, r = observed failures.
        """
        dof = 2 * (self.observed_failures + 1)
        chi2_val = chi2.ppf(self.confidence, dof)
        return (2 * self.total_test_hours) / chi2_val

    # -- R90/C90 -----------------------------------------------------------

    def r90_life_hours(self) -> float:
        """R90: time where R(t) = 0.90 using nominal MTBF."""
        return -self.system_mtbf() * math.log(self.reliability_target)

    def r90_c90_life_hours(self) -> float:
        """R90/C90: R90 using the lower-bound MTBF at 90% confidence.

        "We are 90% confident that 90% of units will survive
        at least this many hours."
        """
        mtbf_lower = self.system_mtbf_lower_bound()
        return -mtbf_lower * math.log(self.reliability_target)

    # -- Summary -----------------------------------------------------------

    def summary(self) -> dict:
        sys_mtbf = self.system_mtbf()
        mtbf_lower = self.system_mtbf_lower_bound()
        r90 = self.r90_life_hours()
        r90c90 = self.r90_c90_life_hours()
        return {
            "component_mtbfs": dict(self.component_mtbfs),
            "system_mtbf_hrs": sys_mtbf,
            "system_mtbf_lower_bound_hrs": mtbf_lower,
            "r90_life_hrs": r90,
            "r90_c90_life_hrs": r90c90,
            "r90_c90_target_hrs": 20_000.0,
            "test_hours": self.total_test_hours,
            "observed_failures": self.observed_failures,
            "passed": r90c90 >= 20_000.0,
        }
