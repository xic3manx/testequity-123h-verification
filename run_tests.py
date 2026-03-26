#!/usr/bin/env python3
"""Orchestrator: pull design values from Flow, run models + pytest,
push results back to Flow and Jira.

Usage:
    python run_tests.py                  # full run (reads from Flow, pushes results)
    python run_tests.py --dry-run        # no API writes
    python run_tests.py --skip-api       # tests only, no API calls
    python run_tests.py -v               # verbose pytest output
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Load .env file if present
_env_path = Path(__file__).resolve().parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())

import config
from models.chamber_system import ChamberSystem
from api.flow_client import FlowClient
from api.jira_client import JiraClient

# Flow design value IDs → model INPUT parameter names
FLOW_INPUT_MAP = {
    1: "heater_power_w",
    2: "compressor_capacity_w",
    3: "max_temp_target_c",
    4: "sensor_mtbf_hrs",
    5: "relay_mtbf_hrs",
    6: "compressor_mtbf_hrs",
}

# Requirement ID → Flow design value ID for pushing computed OUTPUTS
FLOW_OUTPUT_MAP = {
    26: 13,  # max_temp_achieved_c
    27: 14,  # min_temp_achieved_c
    28: 15,  # temp_accuracy_measured_c
    29: 16,  # max_rh_achieved_pct
    30: 17,  # min_rh_achieved_pct
    31: 18,  # humidity_accuracy_measured_pct
    32: 19,  # heat_ramp_rate_actual
    33: 20,  # cool_rate_actual
    34: 21,  # uniformity_delta_c
    35: 22,  # total_power_actual_w
    37: 23,  # humidity_sensor_mtbf_actual
    39: 24,  # r90c90_actual_hrs
}


def print_banner(text: str):
    bar = "=" * 60
    print(f"\n{bar}\n  {text}\n{bar}")


def pull_design_values(dry_run: bool) -> dict[str, float]:
    """Read input design values from Flow and return as named parameters."""
    if dry_run:
        print("  [DRY RUN] Using default model parameters")
        return {}
    try:
        flow = FlowClient(dry_run=False)
        raw = flow.get_design_values()
        params = {}
        for vid, param_name in FLOW_INPUT_MAP.items():
            if vid in raw:
                params[param_name] = raw[vid]
                print(f"  VAL-{vid} ({param_name}) = {raw[vid]}")
        return params
    except Exception as e:
        print(f"  [WARN] Could not read Flow values: {e}")
        print("  Using default model parameters")
        return {}


def run_simulation(flow_params: dict) -> dict[int, float]:
    """Run the system model using Flow-sourced parameters."""
    print_banner("Running TestEquity 123H Chamber Simulation")

    # Build system with Flow-sourced overrides
    system = ChamberSystem()
    if flow_params.get("heater_power_w"):
        system.heating.heater_power_w = flow_params["heater_power_w"]
    if flow_params.get("compressor_capacity_w"):
        system.cooling.compressor_capacity_w = flow_params["compressor_capacity_w"]
    if flow_params.get("sensor_mtbf_hrs"):
        system.reliability.component_mtbfs["Temperature Sensor"] = flow_params["sensor_mtbf_hrs"]
    if flow_params.get("relay_mtbf_hrs"):
        system.reliability.component_mtbfs["Control Relay"] = flow_params["relay_mtbf_hrs"]
    if flow_params.get("compressor_mtbf_hrs"):
        system.reliability.component_mtbfs["Compressor"] = flow_params["compressor_mtbf_hrs"]

    results = system.run_all()

    print(f"\n{'Req':>4}  {'Name':<30}  {'Measured':>12}  {'Threshold':>10}  {'Unit':<8}  {'Result'}")
    print("-" * 92)
    for req_id, measured in sorted(results.items()):
        r = config.REQUIREMENTS[req_id]
        passed = config.passes(req_id, measured)
        mark = "PASS" if passed else "** FAIL **"
        print(
            f"  {req_id:>2}  {r['name']:<30}  {measured:>12.4g}  "
            f"{r['op']} {r['threshold']:<8g}  {r['unit']:<8}  {mark}"
        )
    return results


def run_pytest(verbose: bool = False) -> int:
    """Execute the pytest suite and return the exit code."""
    print_banner("Running Unit Tests (pytest)")
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"]
    if not verbose:
        cmd.append("-q")
    result = subprocess.run(cmd, cwd=str(Path(__file__).resolve().parent))
    return result.returncode


def push_to_flow(results: dict[int, float], dry_run: bool):
    """Push computed values, test runs, and requirement values to Flow."""
    print_banner("Pushing Results to Flow Engineering")
    flow = FlowClient(dry_run=dry_run)

    # Push computed outputs back to Flow design values (VAL-13 through VAL-24)
    print("  Pushing computed outputs to Flow design values...")
    for req_id, val_id in FLOW_OUTPUT_MAP.items():
        if req_id in results:
            measured = round(results[req_id], 4)
            print(f"    Req {req_id} → VAL-{val_id} = {measured}")
            flow.update_design_value(val_id, measured)

    # Also update requirement values directly
    print("  Updating requirement values...")
    if not dry_run:
        value_updates = [
            {"requirementId": rid, "value": {"type": "NUMBER", "value": round(val, 4)}}
            for rid, val in results.items()
        ]
        flow.session.put(
            f"{flow.base_url}/requirements/value",
            json=value_updates,
        )

    # Push test run results
    print("  Creating test runs...")
    for tc_id, tc_info in config.TEST_CASE_MAP.items():
        req_ids = tc_info["req_ids"]
        all_passed = all(config.passes(rid, results[rid]) for rid in req_ids)
        status = "PASS" if all_passed else "FAIL"
        print(f"    TC {tc_id} ({tc_info['name'][:40]}): {status}")
        flow.create_test_run(tc_id, status)

    # Also push R90/C90 to the original system_r90c90_hrs value (VAL-7)
    r90c90 = results.get(39, 0)
    print(f"\n  Pushing R90/C90 = {r90c90:.0f} hrs → VAL-7")
    flow.update_design_value(7, round(r90c90))


def push_to_jira(results: dict[int, float], dry_run: bool):
    """Update Jira issues with test results."""
    print_banner("Updating Jira Issues")
    jira = JiraClient(dry_run=dry_run)

    for req_id, jira_key in config.REQ_JIRA_MAP.items():
        r = config.REQUIREMENTS[req_id]
        measured = results[req_id]
        passed = config.passes(req_id, measured)
        print(f"  {jira_key} ({r['name']}): {'PASS' if passed else 'FAIL'}")
        jira.update_on_result(
            jira_key,
            passed=passed,
            measured=measured,
            req_name=r["name"],
            threshold=r["threshold"],
            unit=r["unit"],
        )


def main():
    parser = argparse.ArgumentParser(description="TestEquity 123H Verification Suite")
    parser.add_argument("--dry-run", action="store_true", help="No API writes")
    parser.add_argument("--skip-api", action="store_true", help="Skip all API calls")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    # 1. Pull design values from Flow
    if not args.skip_api:
        print_banner("Reading Design Values from Flow")
        flow_params = pull_design_values(dry_run=args.dry_run)
    else:
        flow_params = {}

    # 2. Run the simulation models (with Flow-sourced parameters)
    results = run_simulation(flow_params)

    # 3. Run the pytest suite
    exit_code = run_pytest(verbose=args.verbose)

    # 4. Push results to Flow and Jira
    if not args.skip_api:
        push_to_flow(results, dry_run=args.dry_run)
        push_to_jira(results, dry_run=args.dry_run)

    # 5. Summary
    print_banner("Summary")
    total = len(config.REQUIREMENTS)
    passed = sum(1 for rid, val in results.items() if config.passes(rid, val))
    failed = total - passed
    print(f"  Requirements: {passed}/{total} passed")
    if failed:
        print(f"  FAILING:")
        for rid, val in results.items():
            if not config.passes(rid, val):
                r = config.REQUIREMENTS[rid]
                print(f"    Req {rid} ({r['name']}): {val:.4g} {r['unit']} — needs {r['op']} {r['threshold']}")
    print(f"  Pytest exit code: {exit_code}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
