# Changelog

## 0.2.0 (unreleased)

The expiry read. `fathom expiry trace.json` and `fathom_read.expiry(ops)` send the same op stream to the hosted service and get back, per step, the hazard that the agent's committed state spoils, the survival curve, the functional life remaining in steps, and two alarms, one that fires while a rejected action stands in the record and one that fires on committed load alone. Calibrations are named per workload and listed by the service; with none named the read scores under a pooled default and labels the result a shape rather than a number. Exit code 3 when an alarm fired. The contradiction read is unchanged and its verdict rides along in the expiry response.

## 0.1.0 (2026-09-02)

First release. Adapters and a CLI for the committed-state read, which reports six findings (stale reference, superseded value, authored contradiction, residual, duplicate commit, post-commit mutation), the `fathom` command, and adapters for native op streams, coding-agent edit logs, OpenInference spans, LangGraph state history, CrewAI event logs, Letta memory exports, and DBOS step streams.
