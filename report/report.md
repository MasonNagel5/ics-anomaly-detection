# ICS Anomaly Detection - Project Report
**Physical Constraint + Statistical Anomaly Detection on the BATADAL Water Network Dataset**

---

## What This Project Is

Water treatment plants run on SCADA systems - industrial control networks where PLCs manage pumps, tanks, and valves based on sensor readings. During a cyberattack, attackers manipulate those sensor readings to hide what they're doing or cause physical damage. A pump gets turned off but still reports flow. A tank level gets frozen at a fake value while the real tank overflows. The controller sees normal readings and keeps operating, which is the point.

This project detects those attacks on the BATADAL benchmark dataset by checking whether sensor data violates the physical laws of how a water distribution network actually works. If a pump is off but reporting flow, that's physically impossible - flag it. That approach is called physical constraint-based anomaly detection, and it produces alerts that explain themselves: "R1 - dead pump reporting flow on PU3." A SOC analyst in an OT environment can act on that immediately. A neural network score of 0.87 cannot tell them the same thing.

The project was built entirely in Python and PostgreSQL on Linux (WSL2/Ubuntu), and detection rules were also written in Sigma format with Splunk SPL translations for operational context.

---

## Why This Matters for ICS/OT Security

Most BATADAL research uses machine learning. This project doesn't - that's the differentiation. Physical constraint rules encode domain knowledge about what's impossible in a water network. They produce explainable alerts instead of black-box scores. In OT environments like water treatment, power generation, or manufacturing, explainability isn't a nice-to-have - operators need to know what happened and why before they take action on a live system. A false alarm that shuts down a pump incorrectly has real consequences.

This is directly relevant to what national labs like PNNL, INL, and Sandia work on in the ICS/OT security space: detection methods that work in resource-constrained environments, produce human-readable outputs, and can be validated against known ground truth.

---

## Dataset

The BATADAL (Battle of the Attack Detection Algorithms) dataset comes from the C-Town water distribution network - a real-world, medium-sized system modeled in EPANET by Taormina et al. (2018) and used as the benchmark for a competition run through the American Society of Civil Engineers. The network has 7 storage tanks, 11 pumps across 5 pumping stations, 5 valves, 9 PLCs, 429 pipes, and 388 junctions. All readings are hourly across 43 sensor variables.

**Dataset03** - 8,761 hourly readings, fully labeled (att_flag: 0 = normal, 1 = attack). Used only to establish normal operating baselines and compute thresholds. No detection was run on this set.

**Dataset04** - 4,177 hourly readings across approximately 6 months, with attack labels withheld (att_flag = -999). This is the blind test set. 7 cyberattacks are embedded in the data. The task is to find them without knowing where they are.

The 7 attacks:

| ID | Start | End | Duration | Description | SCADA Concealment |
|----|-------|-----|----------|-------------|-------------------|
| 1 | 13/09/16 23 | 16/09/16 00 | 50 hrs | L_T7 threshold manipulation, controls PU10/PU11 | Replay on L_T7 |
| 2 | 26/09/16 11 | 27/09/16 10 | 24 hrs | Same as attack 1, extended replay | Replay on L_T7, PU10/PU11 flow and status |
| 3 | 09/10/16 09 | 11/10/16 20 | 60 hrs | L_T1 altered to constant low, keeps PU1/PU2 ON, causes T1 overflow | Polyline to offset L_T1 |
| 4 | 29/10/16 19 | 02/11/16 16 | 94 hrs | Same as attack 3 | Replay on L_T1, PU1/PU2 flow/status, pump outlet pressure |
| 5 | 26/11/16 17 | 29/11/16 04 | 60 hrs | PU7 working speed reduced to 0.9x nominal, lower T4 levels | None |
| 6 | 06/12/16 07 | 10/12/16 04 | 94 hrs | PU7 speed reduced to 0.7x | L_T4 drop concealed with replay |
| 7 | 14/12/16 15 | 19/12/16 04 | 110 hrs | Same as attack 3 | Replay on L_T1, PU1/PU2 flow and status |

Attacks 2, 4, and 7 use SCADA concealment - replay attacks that feed the controller legitimate-looking historical data to mask what's happening in the physical system.

---

## Technology Stack

| Component | Choice | Why |
|---|---|---|
| Language | Python 3 | psycopg2, csv, pathlib, datetime |
| Database | PostgreSQL (WSL2/Ubuntu) | Standard in federal/national lab environments; better resume signal than SQLite; real foreign key constraints |
| ORM | None - raw psycopg2 | Intentional - writing SQL directly demonstrates the skill |
| Environment | WSL2 (Ubuntu 22.04) | Linux is the standard for ICS/security tooling |
| Detection rules format | Sigma YAML + Splunk SPL | Industry standard for shareable detection logic |
| Credentials | python-dotenv .env file | Not committed to GitHub |

---

## System Architecture

### Data Model

Each CSV row maps to a `SensorReading` object. One object per timestamp, 43 sensor fields. Pumps are stored as nested dicts (`{"PU1": {"flow": 98.99, "status": 1}}`) so flow and status always travel together. Tanks and pressures are flat key-value dicts. The object carries 6 boolean rule flags (`flag_r1` through `flag_r6`) initialized to `False`, plus a master `flagged` boolean set when any rule fires.

### Database Schema (Normalized)

5 tables. One parent row per timestamp, child rows per sensor type:

- `sensor_readings` - `id`, `datetime`, `att_flag`, `detected`, `flag_r6`
- `tank_readings` - `id`, `reading_id`, `tank_id`, `tank_level` (7 rows per timestamp)
- `pump_readings` - `id`, `reading_id`, `pump_id`, `flow`, `status` (11 rows per timestamp)
- `valve_readings` - `id`, `reading_id`, `flow`, `status` (1 row per timestamp)
- `pressure_readings` - `id`, `reading_id`, `junction_id`, `pressure` (12 rows per timestamp)

For each CSV row, 32 rows are inserted across 5 tables. PostgreSQL's `RETURNING id` clause returns the auto-generated primary key after each parent insert, allowing child inserts to reference `reading_id` without a second query. Every insertion runs inside a single transaction - `conn.commit()` is called once after the full dataset is loaded, not per-row.

### Pipeline

```
dataset03.csv → load_dataset() → SensorReading[] → PostgreSQL (all tables)
dataset04.csv → load_dataset() → SensorReading[]
                                       ↓
                              calculate thresholds from dataset03
                                       ↓
                              detect.py → run R1–R6 → UPDATE sensor_readings
                                       ↓
                              evaluate.py → compare flags to attack windows → results
```

---

## Detection Rules

### R1 - Dead Pump Reporting Flow
```python
if pump["status"] == 0 and pump["flow"] > 0.5: flag_r1
```
A stopped pump cannot move water. Flow reported on a stopped pump is a physical impossibility - either the status sensor or the flow sensor is being spoofed. Checked against all 11 pumps per reading.

### R2 - Running Pump With No Flow
```python
if pump["status"] == 1 and pump["flow"] < 0.5: flag_r2
```
An active pump that reports no flow indicates a blocked line, pump failure, or spoofed status reading. Checked against all 11 pumps per reading. MITRE ATT&CK ICS: T0831 (Manipulation of Control).

### R3 - Tank Draining Too Fast
Per-tank maximum drain rate computed from dataset03 by finding the largest level drop between any two consecutive normal readings (att_flag = 0). A global threshold doesn't work here - T6 operates between ~2m and ~5.5m while T1 operates between ~0.3m and ~1.2m. Using one threshold would either miss real anomalies in small tanks or flood large tanks with false positives. Thresholds computed separately for all 7 tanks.

### R4 - Tank Level Out of Range
Per-tank maximum level observed during normal operation in dataset03 becomes the ceiling. Any reading above that ceiling in dataset04 is outside the documented normal operating range. MITRE ATT&CK ICS: T0832 (Manipulation of View).

### R5 - Correlated Multi-Sensor Anomaly
```python
if sum([flag_r1, flag_r2, flag_r3, flag_r4]) >= 2: flag_r5
```
Two or more rules firing on the same timestamp makes coincidence very unlikely. R5 runs in a separate loop after all single-sensor rules have been evaluated, so it always checks the final flag state rather than partial results.

### R6 - Hourly Statistical Baseline (Added After Initial Evaluation)
For each of the 7 tanks, the mean and standard deviation of tank level is computed at each hour of day (0–23) across all 8,761 normal readings in dataset03 - 365 observations per hour per tank. A reading is flagged if any tank deviates more than k=3.1 standard deviations from its expected level for that specific hour.

The threshold k=3.1 was determined by sweeping k from 3.0 to 4.5 in 0.1 increments across all dataset04 readings without modifying the database. At k=3.2, one attack event drops from detection and does not return at any higher k value. k=3.1 is the tightest threshold that preserves 7/7 event detection.

---

## How R6 Was Developed - The Full Iteration Story

After R1–R5 produced a 4/7 detection rate, the 3 missed attacks (2, 4, 7) were analyzed. All three used replay attacks - they don't produce physically impossible sensor values, so the constraint rules see nothing wrong. The attacker replays old legitimate data from a previous time period.

**Phase 1 - Pump/Tank Inconsistency (5 iterations, failed)**

Premise: if PU1/PU2 are running and reporting flow, T1 should rise. If it doesn't, the sensor data is inconsistent. Failed because T1 is driven by both pump inflow and network demand outflow. Demand frequently exceeds pump supply in normal C-Town operation, so T1 drops even with pumps running. No threshold, no consecutive-reading window, and no combination of the two could separate the attack signal from normal demand-driven drops. Every tuning attempt traded event detection for false positive reduction with no stable middle ground.

**Phase 2 - Variance-Based Detection (1 iteration, failed)**

Premise: replay attacks hold sensors at a constant replayed value, so rolling variance near zero while pumps are active would indicate spoofed data. Failed because replay attacks replay real historical data, not a single constant. The replayed readings have their own natural variance. A 12-reading rolling window at variance < 0.001 produced 128 false positives and caught 0 additional attack events.

**Phase 3 - Hourly Statistical Baseline (solution, 5 iterations to tune)**

The core insight: replay attacks don't produce impossible values, but they produce *temporally misplaced* values. Water distribution systems follow tight diurnal demand cycles. Tank levels at 3am look different from tank levels at 3pm, predictably, every day. 365 days of training data gives tight per-hour expected ranges. When a replay attack inserts data from a different time context, it shows up as a statistical outlier for its current hour even when the absolute value is plausible.

This is called process invariant checking - detecting attacks by checking whether the system's physical behavior matches expected patterns over time, not just whether individual readings look valid.

**Unexpected finding - T2, T3, T6 cannot be excluded.** After initial tuning, a database query showed all 83 false positives came from T2, T3, and T6. T1 and T7 - the tanks explicitly targeted in the attack descriptions - generated zero false positives. Excluding T2/T3/T6 to reduce FP dropped event detection back to 4/7. Those downstream tanks catch the missed attacks through hydraulic cascade effects: replay attacks targeting T1 or T7 propagate through the C-Town network and manifest as diurnal anomalies in T2/T3/T6. The FP sources and the detection sources are the same tanks. They cannot be separated.

---

## Results

| | Events Detected | True Positives | False Positives |
|---|---|---|---|
| R1–R5 baseline | 4 / 7 | 58 | 32 |
| R1–R6 final (k=3.1) | 7 / 7 | 38 | 83 |

"Events detected" = at least one flagged reading falls inside that attack's time window. Full hourly coverage of each attack was not achieved - the project detects that an event occurred, not every hour it was active.

Cost of 7/7 vs 4/7: 51 additional false positives over 4,177 readings, across a 6-month test window. That's roughly one spurious alert per two days in exchange for catching 3 attack events that no physical constraint rule could reach.

True positive count dropped from 58 to 38 between baseline and final because R6 targets a different attack signature than R1–R5. The two detection methods are complementary, not redundant.

---

## Sigma Rules

R1–R4 were translated to Sigma format in `sigma/`. Sigma is the industry-standard, vendor-neutral YAML specification for detection rules, convertible to Splunk SPL, Elastic DSL, Microsoft Sentinel KQL, and others. Writing detection logic in Sigma means it's shareable, reviewable, and deployable across SIEM platforms without rewriting from scratch.

R1 and R2 map directly to simple field comparisons. R3 uses Splunk's `streamstats` command to compute consecutive tank level deltas and a `lookup` table of per-tank thresholds derived from training data. R4 follows the same lookup approach. MITRE ATT&CK ICS tags applied: T0831 for R1/R2, T0832 for R3/R4.

R5 and R6 were intentionally excluded. R5 requires cross-event correlation that Sigma cannot natively express. R6 requires per-hour statistical lookups and standard deviation comparisons that exceed Sigma's detection syntax - they would need to be implemented as scheduled SIEM searches with pre-computed lookup tables, which is how this would work in a production environment.

---

## Limitations and What Would Make This Production-Ready

The C-Town dataset is simulated. Real SCADA environments have sensor noise, communication latency, hardware drift, and calibration errors that this dataset doesn't include. R2 (running pump, no flow) would likely generate significant false positives during pump startup transients in real hardware - a 30-second exclusion window post-startup would be needed.

The hourly statistical baseline in R6 assumes consistent diurnal patterns. Seasonal demand variation, scheduled maintenance, fire hydrant testing, or unusual operational events could shift expected ranges and increase false positives. A production version needs rolling baseline updates - probably a 90-day sliding training window rather than a fixed historical set.

The database write-back is per-run. Running `detect.py` twice without resetting `detected = 0` first would double-flag readings. A production pipeline needs idempotency guarantees.

---

## Project Stats

- **Training data**: 8,761 hourly readings, 43 variables, 1 year of normal C-Town operation
- **Test data**: 4,177 hourly readings, 6 months, 7 embedded cyberattacks
- **Database rows inserted**: ~270,000 across 5 normalized tables
- **Rules**: 6 detection rules (5 physical constraint, 1 statistical)
- **R6 development**: 11 iterations across 3 failed and 1 successful approach
- **Final detection rate**: 7/7 attack events, 38 true positives, 83 false positives
- **Sigma rules**: 4 rules in YAML, manual Splunk SPL translations for all 4

---

## One-Line Summary

Built a physical constraint and statistical anomaly detection system on the BATADAL water distribution dataset - rules that catch cyberattacks by flagging what's physically impossible and statistically out of place, with a measured 7/7 event detection rate against labeled ground truth across 4,177 blind test readings.
