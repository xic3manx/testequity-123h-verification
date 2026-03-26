"""Flow Engineering API client."""

import requests
import config


class FlowClient:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.base_url = config.FLOW_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        if not dry_run:
            self._authenticate()

    def _authenticate(self):
        resp = requests.post(
            config.FLOW_AUTH_URL,
            json={"refreshToken": config.FLOW_REFRESH_TOKEN},
            headers={"Content-Type": "application/json"},
        )
        resp.raise_for_status()
        token = resp.json()["accessToken"]
        self.session.headers["Authorization"] = f"Bearer {token}"

    # ----- Read -------------------------------------------------------------

    def get_requirements(self) -> list[dict]:
        resp = self.session.get(f"{self.base_url}/requirements/paged?page=0&size=100")
        resp.raise_for_status()
        return resp.json()["results"]

    def get_test_cases(self) -> list[dict]:
        resp = self.session.get(f"{self.base_url}/testCases/paged?page=0&size=100")
        resp.raise_for_status()
        return resp.json()["results"]

    # ----- Write ------------------------------------------------------------

    def create_test_run(self, test_case_id: int, status: str = "PASS", name: str = "") -> dict | None:
        """Create a test run for a test case.

        status: "PASS", "FAIL", "SKIP", or "PENDING"
        """
        if self.dry_run:
            print(f"  [DRY RUN] Would create test run for TC {test_case_id}: {status}")
            return None
        run_name = name or f"Automated Run – TC{test_case_id}"
        resp = self.session.post(
            f"{self.base_url}/testCase/{test_case_id}/testRun",
            json={"status": status, "name": run_name},
        )
        if resp.status_code == 200:
            return resp.json()
        print(f"  [WARN] Test run creation returned {resp.status_code}: {resp.text[:200]}")
        return None

    def get_design_values(self) -> dict[int, float]:
        """Fetch all design values. Returns {id: numeric_value}."""
        resp = self.session.get(f"{self.base_url}/values/number")
        resp.raise_for_status()
        return {item["id"]: item["value"] for item in resp.json()}

    def update_design_value(self, value_id: int, value: float) -> bool:
        """Push a computed value back to Flow."""
        if self.dry_run:
            print(f"  [DRY RUN] Would update value {value_id} = {value}")
            return True
        resp = self.session.put(
            f"{self.base_url}/value/{value_id}/number",
            json={"value": value},
        )
        return resp.status_code == 200

    def update_requirement_stage(self, req_id: int, stage_id: str) -> bool:
        """Move a requirement to a new stage."""
        if self.dry_run:
            print(f"  [DRY RUN] Would update req {req_id} to stage {stage_id}")
            return True
        resp = self.session.put(
            f"{self.base_url}/requirements/stage",
            json=[{"requirementId": req_id, "stageId": stage_id}],
        )
        return resp.status_code == 200
