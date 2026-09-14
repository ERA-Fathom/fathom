# Changelog

## 0.3.0 (2026-09-14)

The expiry read now carries covariates that cannot run off the end of their own calibration, and it refuses rather than
guesses where a read does not apply.

Covariates. The read scores on the share of steps the agent has committed on and the share of its live facts, both
derived from the ledger the adapters already build, replacing a cumulative write count that grew without bound on any
agent that keeps committing. Each covariate's fitted range is now its structural bound, so a long run stays inside the
region its calibration was fitted on. Scored across every trace we hold, 3552 runs over seven agent frameworks, none
leaves that region; the previous covariates covered the first 18 steps of a 514-step run.

Refusals. When more than a fifth of a run's steps fall outside the range its calibration was fitted on, the read
returns that condition in place of a life estimate and an alarm, and names the covariate, the step it left at and how
far the calibration carries the run. When the reported life falls below a quarter of the stretch a run has already
survived since its last contradiction, the read withholds the life estimate alone and says so, since the run itself
refutes the number.

The load alarm. This release withdraws it. Across our traces it fired within the first few steps of every run of every
commit-heavy workload regardless of when that run actually contradicted itself, so it tracked the step count rather than
the run. The exposure alarm stays, and the covariates behind the withdrawn alarm still feed the hazard and the life
estimate. `fathom expiry` exits 3 when the exposure alarm fired, and 0 when it did not or when the read does not apply.

Calibrations. All three are refitted on the op streams the adapters produce rather than on harness-recorded counts. The
pooled default and the relational calibration ship a first-contradiction fit only, because on the recurring-event
definition neither beat a plain step counter and a calibration that loses to counting steps does not ship.

## 0.2.0 (2026-09-13)

The expiry read. `fathom expiry trace.json` and `fathom_read.expiry(ops)` send the same op stream to the hosted service and get back, per step, the hazard that the agent's committed state spoils, the survival curve, the functional life remaining in steps, and two alarms, one that fires while a rejected action stands in the record and one that fires on committed load alone. Calibrations are named per workload and listed by the service; with none named the read scores under a pooled default and labels the result a shape rather than a number. Exit code 3 when an alarm fired. The contradiction read is unchanged and its verdict rides along in the expiry response.

## 0.1.0 (2026-09-02)

First release. Adapters and a CLI for the committed-state read, which reports six findings (stale reference, superseded value, authored contradiction, residual, duplicate commit, post-commit mutation), the `fathom` command, and adapters for native op streams, coding-agent edit logs, OpenInference spans, LangGraph state history, CrewAI event logs, Letta memory exports, and DBOS step streams.
