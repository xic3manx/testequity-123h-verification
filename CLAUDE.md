# CLAUDE.md — TestEquity 123H Verification Suite

## Project Overview
TestEquity 123H environmental test chamber demo for Flow Engineering.
Integrates Flow (requirements/systems), Jira (sprint tasks), GitHub (code), and Python (models/tests).

## Flow Engineering API — Lessons Learned

### Authentication
- Exchange refresh token for access token: `POST /rest/v1/auth/exchange` with `{"refreshToken": "..."}`
- Access tokens expire in 24 hours
- All subsequent calls use `Authorization: Bearer <token>`

### Requirement Stages Block Edits
**CRITICAL:** Requirements in "Released" or "In Review" stage **silently reject** PATCH updates and value pushes. You MUST move them to "Draft" first:
```
PUT /requirements/stage → [{"requirementId": X, "stageId": "79415350-249e-44a8-a233-4d18672e36ec"}]
```
Stage IDs:
- Draft: `79415350-249e-44a8-a233-4d18672e36ec`
- In Review: `accc5d14-b230-4f44-b244-384419d06944`
- Released: `fe5051a5-d736-46a3-99d6-769fcd9082c9`

Also: Requirements in "Released" stage cannot be deleted — returns 204 but doesn't delete. Must move to Draft first.

### Check System (Target vs Actual)
- `check.type`: MANUAL, TARGET, TESTCASE, SUMMARY, DOCUMENT, EQUALITY, CUTOFF
- `check.targetDataId`: links to a design value (the spec/goal)
- `check.actualDataId`: links to a design value (the measured result)
- **Check type CANNOT be set or changed via API** — must use the Flow UI
- PATCHING a requirement that has a TARGET check may reset it to MANUAL

### Design Values
- **Cannot create, delete, or rename via API** — UI only
- Update numeric values: `PUT /value/{id}/number` with `{"value": 123}`
- Read all: `GET /values/number` returns `[{"id": 1, "name": "...", "value": 123}]`
- No description field exists on design values
- Have a `version` field that auto-increments

### Requirements
- Create: `POST /requirements` with JSON array
- PATCH: `PATCH /requirements` — can update `statement_raw`, `reviewers`, `verificationMethod`, `customFields`, `owner`, `name` — but **NOT** `check`, `systemIds`, or `value`
- Push computed values: `PUT /requirements/value` with `[{"requirementId": X, "value": {"type": "NUMBER", "value": Y}}]`
- Link parent-child: `POST /requirement/{parentId}/links/child` with `{"id": childId}`

### System Links (the correct way)
- Link requirements to systems: `POST /system/{sysId}/links/requirements` with `[{"requirementId": X}]`
- Link test cases to systems: `POST /system/{sysId}/links/testCases` with `[{"testCaseId": X}]`
- Link documents to systems: `POST /system/{sysId}/links/documents` with `[{"documentId": X}]`
- Do NOT try to set `systemIds` via requirement PATCH — it gets ignored

### Systems
- Create: `POST /system` (singular, one at a time, NOT array)
- Bulk update descriptions: `PUT /systems` with `[{"systemId": "uuid", "description": "..."}]`
- Delete: `DELETE /system/{uuid}` — must delete children before parents

### Test Cases
- Create: `POST /testCases` with JSON array
- PATCH: `PATCH /testCases` — field name is `testCaseId`, not `id`
- Test case descriptions and steps may require the test case to be in a specific stage

### Test Plans
- **Cannot create or delete via API** — returns 405 on POST, 404 on DELETE
- Read only: `GET /testPlans`

### Interfaces
- Create: `POST /interfaces` — needs `sourceId` (singular) and `targetIds` (array)
- Update: `PATCH /interfaces` — uses `interfaceId` field

### Configurations
- **Cannot rename, create, or delete via API**
- Assignment requires parent-child configuration consistency

### Jira Integration
- Link requirement to Jira: `POST /requirement/{id}/jiraIssues`
- Body requires BOTH issue key AND full Jira credentials:
  ```json
  {"issueKeyOrId": "KAN-7", "JiraCredentials": {"email": "...", "token": "...", "subdomain": "..."}}
  ```
- Same pattern for test cases: `POST /testCase/{id}/jiraIssues`

### File Uploads
- `POST /requirement/{id}/uploadFile` — requires a File-type custom field to exist first
- Custom fields must be created in UI before upload works
- `POST /testCase/{id}/file/{fileId}` — returns temporary download URL

### Jira API (saladikm.atlassian.net)
- Uses REST API v3 with basic auth (email:token)
- Old search endpoint removed — use `GET /rest/api/3/search/jql?jql=...`
- Issue types for KAN project: Epic (10005), Subtask (10006), Feature (10007), Task (10008)
- Transition IDs: To Do (11), In Progress (21), Done (31), Blocked (41), Cancelled (51)

## Project IDs Quick Reference
See memory/project_context.md for full system/requirement/value ID mapping.

## Running the Suite
```bash
python3 run_tests.py                  # full run: Flow → Python → Flow + Jira
python3 run_tests.py --dry-run        # no API writes
python3 run_tests.py --skip-api       # tests only
python3 run_tests.py -v               # verbose
```

## Demo: Change Propagation
1. In Flow UI, change `heater_power_w` from 1500 → 2500
2. Run `python3 run_tests.py`
3. Python reads value from Flow, recomputes, pushes results back
4. Req 26 flips FAIL → PASS, Jira updates
