"""Central configuration for TestEquity 123H Environmental Chamber."""
import os

# ---------------------------------------------------------------------------
# Flow Engineering API
# ---------------------------------------------------------------------------
FLOW_REFRESH_TOKEN = os.environ["FLOW_REFRESH_TOKEN"]  # set via .env or export
FLOW_ORG = "candidate-2"
FLOW_PROJECT = "candidate-2-demo-project~1"
FLOW_BASE_URL = f"https://api.flowengineering.com/rest/v1/org/{FLOW_ORG}/project/{FLOW_PROJECT}"
FLOW_AUTH_URL = "https://api.flowengineering.com/rest/v1/auth/exchange"
FLOW_USER_ID = "88aadaa4-23f0-49bc-a9ee-8cc81ca6276a"

# ---------------------------------------------------------------------------
# Jira API
# ---------------------------------------------------------------------------
JIRA_SUBDOMAIN = "saladikm"
JIRA_BASE_URL = f"https://{JIRA_SUBDOMAIN}.atlassian.net"
JIRA_EMAIL = os.environ.get("JIRA_EMAIL", "saladikm@gmail.com")
JIRA_API_TOKEN = os.environ["JIRA_API_TOKEN"]  # set via .env or export

# ---------------------------------------------------------------------------
# Requirement definitions
# ---------------------------------------------------------------------------
REQUIREMENTS = {
    26: {"name": "Temperature Range (High)",  "threshold": 200.0,  "unit": "°C",     "op": ">="},
    27: {"name": "Temperature Range (Low)",   "threshold": -40.0,  "unit": "°C",     "op": "<="},
    28: {"name": "Temperature Accuracy",      "threshold": 0.5,    "unit": "°C",     "op": "<="},
    29: {"name": "Humidity Range (High)",      "threshold": 95.0,   "unit": "%RH",    "op": ">="},
    30: {"name": "Humidity Range (Low)",       "threshold": 20.0,   "unit": "%RH",    "op": "<="},
    31: {"name": "Humidity Accuracy",          "threshold": 2.0,    "unit": "%RH",    "op": "<="},
    32: {"name": "Heat Ramp Rate",             "threshold": 5.0,    "unit": "°C/min", "op": ">="},
    33: {"name": "Cool-Down Rate",             "threshold": 3.0,    "unit": "°C/min", "op": ">="},
    34: {"name": "Temperature Uniformity",     "threshold": 1.0,    "unit": "°C",     "op": "<="},
    35: {"name": "Power Consumption",          "threshold": 3000.0, "unit": "W",      "op": "<="},
    # Reliability
    36: {"name": "Temp Sensor MTBF",           "threshold": 50000,  "unit": "hrs",    "op": ">="},
    37: {"name": "Humidity Sensor MTBF",        "threshold": 40000,  "unit": "hrs",    "op": ">="},
    38: {"name": "Control Relay MTBF",          "threshold": 100000, "unit": "hrs",    "op": ">="},
    39: {"name": "System R90/C90 Life",         "threshold": 20000,  "unit": "hrs",    "op": ">="},
}

# ---------------------------------------------------------------------------
# Test case → Jira → requirement mapping
# ---------------------------------------------------------------------------
TEST_CASE_MAP = {
    9:  {"jira_key": "KAN-14", "req_ids": [26, 27, 28], "name": "Temperature Range Verification"},
    10: {"jira_key": "KAN-19", "req_ids": [29, 30, 31], "name": "Humidity Accuracy Test"},
    11: {"jira_key": "KAN-17", "req_ids": [32, 33],     "name": "Ramp Rate Performance Test"},
    12: {"jira_key": "KAN-18", "req_ids": [34],          "name": "Temperature Uniformity Mapping"},
}

REQ_JIRA_MAP = {
    26: "KAN-20",  # Safety interlock → high temp
    27: "KAN-16",  # Refrigeration assembly → low temp
    28: "KAN-14",  # Sensor calibration → accuracy
    31: "KAN-19",  # Humidity sensor verification
    32: "KAN-17",  # Ramp rate test
    33: "KAN-17",  # Cool-down rate (same task)
    34: "KAN-18",  # Uniformity test
    35: "KAN-20",  # Safety interlock → power limit
    39: "KAN-22",  # Reliability analysis
}


def passes(req_id: int, measured: float) -> bool:
    """Check whether *measured* satisfies the requirement."""
    r = REQUIREMENTS[req_id]
    if r["op"] == ">=":
        return measured >= r["threshold"]
    return measured <= r["threshold"]
