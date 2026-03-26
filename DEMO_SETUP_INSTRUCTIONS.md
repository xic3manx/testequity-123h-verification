# TestEquity 123H Demo — Manual Setup Instructions

These steps must be done in the Flow UI (the API cannot do them).

---

## 1. Delete Rivian Leftovers

### Test Plans (cannot delete via API)
Go to **Test Plans** and delete:
- TP 1: "Vehicle Range"
- TP 2: "Powertrain Efficiency Verification"

### Configurations (cannot delete via API)
Go to **Configurations** and delete:
- Variant 1
- Variant 2
- Variant 3

(Or rename Variant 1 → "TestEquity 123H" and Variant 2 → "TestEquity 123C" if you want to demo product variants.)

---

## 2. Fix Design Value Names and Units

Go to **Parameters → Design Values** and update each:

| ID | Current Name | Rename To | Set Unit To | Current Value |
|----|-------------|-----------|-------------|---------------|
| 1 | Charge Time | heater_power_w | W | **1500** (intentionally low for demo) |
| 2 | range_nominal | compressor_capacity_w | W | 1800 |
| 3 | v_Nom | max_temp_target_c | °C | 200 |
| 4 | v_Min | sensor_mtbf_hrs | hrs | 50000 |
| 5 | v_Max | relay_mtbf_hrs | hrs | 100000 |
| 6 | I_rated_cont | compressor_mtbf_hrs | hrs | 30000 |
| 7 | range_cold | system_r90c90_hrs | hrs | 54174 |

---

## 3. Set Up Requirement Checks (TARGET type)

For each requirement, click the requirement → **Check** section → set type to **Target** and link to the corresponding design value.

This enables Flow's native PASS/FAIL comparison (green/red indicator).

| Requirement | Check Type | Link to Design Value |
|---|---|---|
| Req 26: Temperature Range (High) | Target | heater_power_w (ID 1) — *or create a new "max_temp_achieved" value* |
| Req 36: Temp Sensor MTBF | Target | sensor_mtbf_hrs (ID 4) |
| Req 38: Control Relay MTBF | Target | relay_mtbf_hrs (ID 5) |
| Req 39: System R90/C90 Life | Target | system_r90c90_hrs (ID 7) |

For the remaining requirements, set check type to **Manual** — the Python runner will update their values and statuses automatically.

---

## 4. Upload Models and Test Profiles

### Excel Test Profiles
Go to each test case and attach the corresponding Excel file from `test_profiles/`:

| Test Case | Upload File |
|---|---|
| TC9: Temperature Range Verification | `temperature_ramp_profile.xlsx` |
| TC10: Humidity Accuracy Test | `humidity_test_matrix.xlsx` |
| TC12: Temperature Uniformity Mapping | `uniformity_thermocouple_map.xlsx` |

Also upload `reliability_mtbf_data.xlsx` to Document "Reliability Analysis Report".

### Python Models
The Python models are in the GitHub repo. In Flow, you can reference them by adding a link to the GitHub repo URL in each system's description or in the documents section:
- `https://github.com/xic3manx/testequity-123h-verification`

### CAD Models (Onshape)
If you have an Onshape account, create a simple chamber model and link it to:
- "Chamber Enclosure" system
- "Heating Subsystem" system

Alternatively, link to the TestEquity 123H product page or datasheet as a reference document.

---

## 5. Demo Script — The "Money Shot"

### Starting State
- `heater_power_w` = **1500 W** in Flow (intentionally low)
- Req 26 (Temperature Range High) = **FAIL** (max temp only 150°C)
- Jira KAN-20 has a FAIL comment

### Demo Steps

1. **Show the failure in Flow**
   - Open Requirements view → Req 26 is RED
   - Click into it → see measured value 150°C vs threshold ≥ 200°C
   - See it's linked to Heating Subsystem

2. **Trace the root cause**
   - Click Heating Subsystem → see design value `heater_power_w = 1500 W`
   - "The heater isn't powerful enough"

3. **Fix the design value**
   - Change `heater_power_w` from **1500** → **2500** in Flow's design values

4. **Run the verification suite**
   ```bash
   python3 run_tests.py
   ```

5. **Watch the cascade**
   - Python reads `heater_power_w = 2500` from Flow
   - Model recomputes: max temp = 233°C
   - Req 26 → PASS (value pushed back to Flow)
   - TC9 test run → PASS
   - Jira KAN-20 → PASS comment added
   - Flow shows all GREEN

6. **Show the traceability**
   - Requirement → System → Design Value → Python Model → Test Case → Test Run → Jira Task
   - "One change, full chain verified automatically"

---

## 6. Bonus: Break Something Else

To show a different failure chain, try these in Flow's design values:

| Change | What breaks |
|---|---|
| `compressor_capacity_w`: 1800 → 800 | Req 33 (Cool-Down Rate) FAILS |
| `sensor_mtbf_hrs`: 50000 → 30000 | Req 36 (Sensor MTBF) FAILS |
| `relay_mtbf_hrs`: 100000 → 50000 | Req 38 (Relay MTBF) FAILS, Req 39 (R90/C90) drops |
| `compressor_mtbf_hrs`: 30000 → 10000 | Req 39 (R90/C90) FAILS |
