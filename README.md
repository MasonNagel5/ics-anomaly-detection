# ICS Anomaly Detection

Rule-based intrusion detection system for a simulated water distribution network using the BATADAL dataset.

## Detection Rules

Six physical constraint and statistical rules detect cyberattacks in SCADA sensor readings. Rules R1-R4 check for physically impossible sensor states. R5 flags multi-sensor correlation anomalies. R6 uses per-hour statistical baselines derived from normal training data to catch replay attacks that evade individual sensor checks.

Sigma rule definitions for R1-R4 and their Splunk SPL conversions are in the [sigma/](sigma/) folder.
