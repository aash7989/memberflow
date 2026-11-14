# Architecture
## Flow
Synthetic demand → coverage-template selection → named employee assignments → two-stage queue simulation → policy metrics and exports.

## Modules
- demand: stochastic inputs, seeded generation, request schema.
- staffing: employee/shift records, eligibility checks, break windows, weekly balance and coverage tables.
- simulation: protected-window reservations, escalation processing, operational and cost metrics.
- optimization: constant-budget local search over feasible desk templates.
- experiment: held-out replications, stress scenarios, paired comparisons, weekly workload reports.
- app: interactive scenario comparison and roster inspection.

## Dashboard hour transfer
Moving a four-hour shift one hour later removes one hour of headcount from its original leading edge and adds one hour at its new trailing edge. Total paid hours and pay rates remain unchanged. The break shifts with the template, so some intermediate active coverage also changes. A transfer is rejected if it violates availability or overlaps another assignment for the same employee.

## Testing
Tests cover deterministic generation, input validation, basic queue waits, protected breaks, hard shift ends, missing escalation coverage, supervisor ready-order handling, zero arrivals, paid-break costs, availability, weekly limits, overlapping assignments, and active coverage reporting.

## Output interpretation
Per-policy rosters expose names and breaks; coverage files distinguish paid headcount from actively available headcount at 15-minute boundaries. Synthetic event logs expose service starts, completions and unresolved statuses. Replication records preserve seeds and scenario labels. Workload files preserve employee-level hours and evening counts rather than reporting a fairness score without its basis.
