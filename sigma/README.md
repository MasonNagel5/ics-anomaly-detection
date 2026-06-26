# Sigma Rules

Sigma is an open, vendor-neutral format for writing detection rules that can be converted to queries for any SIEM platform. Rather than writing rules directly in a platform-specific query language, Sigma lets you define detection logic once and translate it to Splunk, Elastic, Microsoft Sentinel, or any other supported backend.

These rules translate the physical constraint checks from this project (R1-R4) into Sigma format so they could be deployed in a real SOC environment. Each rule was then manually converted to Splunk SPL, documented in `splunk_queries.spl`. R5 and R6 are not included as Sigma rules. R5 is a correlation rule requiring cross-event logic that Sigma cannot natively express, and R6 requires per-hour statistical baselines computed from training data, which falls outside the scope of a static detection rule.
