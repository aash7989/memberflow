# Data Card
## Provenance
All records are generated from configurable probability distributions or explicit scheduling assumptions. No real member, employee, or institutional data are included. Employee identifiers label hypothetical workers. All example outputs are synthetic.

## Intended use
Controlled staffing-policy comparisons, sensitivity analysis, and queue-model validation. Outputs are not calibrated estimates of any particular facility's performance.

## Demand assumptions
A 12-hour day begins at 08:00. Expected hourly arrivals are 12, 18, 28, 42, 38, 26, 20, 30, 46, 40, 22, 12. Counts are Poisson; arrivals are uniform within each hour conditional on the count. Service durations are gamma distributed with shape 2.

| Request type | Probability | Mean desk service (min) | Escalation probability |
|---|---:|---:|---:|
| Access question | 0.40 | 1.5 | 0.01 |
| Registration | 0.15 | 7 | 0.05 |
| Account issue | 0.15 | 5 | 0.20 |
| Guest pass | 0.25 | 3 | 0.02 |
| Complex concern | 0.05 | 4 | 0.90 |

Supervisor service uses gamma shape 2 and mean 6 minutes. Demand and handling-time multipliers support stress tests. Probabilities and rates are illustrative assumptions, not empirical estimates.

## Request schema
| Field | Definition |
|---|---|
| request_id | Generated request identifier |
| arrival_min | Minutes since opening |
| request_type | Hypothetical service category |
| service_min | Required desk handling minutes |
| supervisor_required | Escalation indicator |
| supervisor_min | Additional supervisor handling minutes |
| synthetic | True for all generated arrivals |

## Employee schema
employee_id, role, available_start, available_end, hourly_rate, max_daily_hours, max_weekly_hours. Eight desk employees and three supervisors are defined. One desk employee is unavailable in the first four hours and another in the last four. Other availability spans the day. Daily limits are 8 paid hours and weekly limits 32; these are scenario parameters, not legal standards.

## Roster schema
employee_id, role, start, end, break_start, break_end, hourly_rate, day, paid_hours, active_hours, evening. Breaks are paid and last 15 minutes per four-hour shift. Evening means ending after minute 600 (18:00).

## Reproducibility and privacy
Seeds reproduce stochastic inputs within a fixed dependency environment. Training and evaluation seeds are disjoint. No personal information is collected. Scenario tables and synthetic labels should accompany exported results.
