"""Jira Cloud REST API v3 client."""

import requests
import config


class JiraClient:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.base_url = f"{config.JIRA_BASE_URL}/rest/api/3"
        self.session = requests.Session()
        self.session.auth = (config.JIRA_EMAIL, config.JIRA_API_TOKEN)
        self.session.headers.update({"Content-Type": "application/json"})

    def get_transitions(self, issue_key: str) -> list[dict]:
        resp = self.session.get(f"{self.base_url}/issue/{issue_key}/transitions")
        resp.raise_for_status()
        return resp.json()["transitions"]

    def transition_issue(self, issue_key: str, target_status: str) -> bool:
        """Transition an issue to the named status."""
        transitions = self.get_transitions(issue_key)
        match = next(
            (t for t in transitions if t["to"]["name"].lower() == target_status.lower()),
            None,
        )
        if not match:
            # Try partial match
            match = next(
                (t for t in transitions if target_status.lower() in t["name"].lower()),
                None,
            )
        if not match:
            print(f"  [WARN] No transition to '{target_status}' for {issue_key}")
            return False
        if self.dry_run:
            print(f"  [DRY RUN] Would transition {issue_key} -> {target_status}")
            return True
        resp = self.session.post(
            f"{self.base_url}/issue/{issue_key}/transitions",
            json={"transition": {"id": match["id"]}},
        )
        return resp.status_code == 204

    def add_comment(self, issue_key: str, text: str) -> bool:
        """Add a comment in Atlassian Document Format."""
        body = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": text}],
                    }
                ],
            }
        }
        if self.dry_run:
            print(f"  [DRY RUN] Would comment on {issue_key}: {text[:80]}...")
            return True
        resp = self.session.post(
            f"{self.base_url}/issue/{issue_key}/comment", json=body
        )
        return resp.status_code == 201

    def update_on_result(
        self, issue_key: str, passed: bool, measured: float, req_name: str, threshold: float, unit: str
    ) -> None:
        """Transition issue and add result comment."""
        status = "Done" if passed else "To Do"
        verdict = "PASSED" if passed else "FAILED"
        comment = (
            f"[Automated Test] {req_name}: {verdict}\n"
            f"Measured: {measured:.4g} {unit} | Threshold: {threshold} {unit}\n"
        )
        self.transition_issue(issue_key, status)
        self.add_comment(issue_key, comment)
