#!/usr/bin/env python3
"""Orchestrator: run pytest, then push results to Flow and Jira.

Usage:
    python run_tests.py                  # full run
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


def print_banner(text: str):
    bar = "=" * 60
    print(f"\n{bar}\n  {text}\n{bar}")


def run_simulation() -> dict[int, float]:
    """Run the system model and return measured values for all requirements."""
    print_banner("Running TestEquity 123H Chamber Simulation")
    system = ChamberSystem()
    results = system.run_all()

    print(f"\n{'Req':>4}  {'Name':<30}  {'Measured':>12}  {'Threshold':>10}  {'Unit':<6}  {'Result'}")
    print("-" * 90)
    for req_id, measured in sorted(results.items()):
        r = config.REQUIREMENTS[req_id]
        passed = config.passes(req_id, measured)
        mark = "PASS" if passed else "FAIL"
        print(
            f"  {req_id:>2}  {r['name']:<30}  {measured:>12.4g}  "
            f"{r['op']} {r['threshold']:<8g}  {r['unit']:<6}  {mark}"
        )
    return results


def run_pytest(verbose: bool = False) -> int:
    """Execute the pytest suite and return the exit code."""
    print_banner("Running Unit Tests (pytest)")
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"]
    if not verbose:
        cmd.append("-q")
    result = subprocess.run(cmd, cwd="/home/xic3manx/Temporary/JiraFlowTest")
    return result.returncode


def push_to_flow(results: dict[int, float], dry_run: bool):
    """Create test runs and push computed values to Flow."""
    print_banner("Pushing Results to Flow Engineering")
    flow = FlowClient(dry_run=dry_run)

    # Push test run results
    for tc_id, tc_info in config.TEST_CASE_MAP.items():
        req_ids = tc_info["req_ids"]
        all_passed = all(config.passes(rid, results[rid]) for rid in req_ids)
        status = "PASS" if all_passed else "FAIL"
        print(f"  TC {tc_id} ({tc_info['name'][:40]}): {status}")
        flow.create_test_run(tc_id, status)

    # Push computed R90/C90 back to Flow design value #7
    r90c90 = results.get(39, 0)
    print(f"\n  Pushing R90/C90 = {r90c90:.0f} hrs → Flow design value #7")
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

    # 1. Run the simulation models
    results = run_simulation()

    # 2. Run the pytest suite
    exit_code = run_pytest(verbose=args.verbose)

    # 3. Push results to Flow and Jira
    if not args.skip_api:
        push_to_flow(results, dry_run=args.dry_run)
        push_to_jira(results, dry_run=args.dry_run)

    # 4. Summary
    print_banner("Summary")
    total = len(config.REQUIREMENTS)
    passed = sum(1 for rid, val in results.items() if config.passes(rid, val))
    print(f"  Requirements: {passed}/{total} passed")
    print(f"  Pytest exit code: {exit_code}")
    if exit_code != 0:
        print("  ⚠ Some unit tests failed — check output above")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
