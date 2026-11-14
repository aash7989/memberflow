# Methodology
## Decision model
The decision variables are the start times of six four-hour desk coverage templates and the assignment of role-qualified synthetic employees to those templates. The base policy includes three four-hour supervisor shifts. Template search holds paid desk hours constant at 24.

## Service model
Requests are processed in arrival order at the desk. For each request, the simulator chooses the earliest feasible active interval across staff, considering previous reservations, breaks, and shift ends. Service is nonpreemptive and must finish before the active interval ends. A request that cannot fit is marked unresolved; later shorter requests may still fit. Consequently this is fit-aware arrival-order dispatch rather than strict head-of-line FCFS. Future feasible starts are reserved and not reconsidered, so short requests may also wait behind an earlier future reservation.

Desk capacity is released before escalation. Supervisor requests are ordered by desk completion time and use the same fit-aware reservation rule. Roles are separate and supervisors do not provide desk coverage. There is no abandonment, service priority, shared handling, or carryover to a subsequent day. No overtime is permitted. All work completes within the configured day or remains unresolved. Long handling times relative to active windows can increase unresolved counts.

## Availability and protected breaks
Assignments must fit employee availability, may not overlap for the same employee, and respect the configured paid-hour limits. Every template includes a protected paid 15-minute break, normally 90 minutes after starting; simultaneous starts stagger breaks by 15 minutes. Breaks remove service capacity. The model does not guarantee a minimum active headcount at every moment: reduced or zero coverage is represented explicitly and visible in the coverage export.

The scheduling system does not claim legal compliance. Daily rest, contractual rules, employee preferences, weekly rest, and jurisdiction-specific regulations are outside scope.

## Coverage search
Local search begins with fixed starts [0, 0, 240, 240, 480, 480]. In each of up to two passes, it evaluates relocating one template start to an hourly boundary between minute 0 and 480. The best improving feasible candidate is retained. Training consists of seeds 0, 1, and 2. Assignment infeasibility receives an infinite candidate score.

Objective = total completed waiting minutes + 120 × unresolved request count. The penalty is a configurable design choice in code, not an estimated economic loss. Constant labor cost is imposed through equal template counts, not optimized in the objective. Global optimality is not guaranteed.

## Assignment balance
Role-qualified candidates are ranked by accumulated weekly and current-day hours. Evening assignments additionally weight accumulated evening counts by four. Ties use synthetic employee IDs. The baseline assigns by ID subject to the same availability and hour constraints. Five-day comparisons use the demand-aware coverage template every day; the coverage template is not reoptimized for weekly fairness.

Reported measures are paid-hour spread (maximum minus minimum) and evening-assignment-count spread within each role, including employees with no assignments. Lower spread represents balance only under these definitions; unequal availability and preferences may justify unequal assignments. The heuristic does not guarantee that every spread improves.

## Scenarios and costs
Base: volume 1.0, handling-time multiplier 1.0. Surge: volume 1.4. Slow service: handling-time multiplier 1.3. Policies reuse the same day realization within each scenario.

Fixed and demand-aware: 24 paid desk hours + 12 paid supervisor hours. Surge buffer adds 4 paid desk hours at minute 420; extra supervisor adds 4 paid supervisor hours at minute 480. These two additions have different wage costs and are not equal-cost treatments. Cost uses illustrative hourly wages and includes paid breaks; overhead and fringe costs are excluded.

## Metrics and uncertainty
Wait excludes service time and includes desk plus supervisor queue time for completed requests. Daily 95th-percentile waits are computed from completed requests, then averaged across replications. A mean of daily percentiles is not a pooled percentile. Unresolved counts, cost and hours must accompany waiting metrics.

Paired differences are demand-aware mean wait minus fixed mean wait for each day. Negative values indicate lower completed-request wait. Approximate intervals use mean ± 1.96 × standard error across independent simulated days. Small example runs are demonstrations, not stable estimates. Missing wait comparisons are excluded; the exported count records available paired observations. Parameter uncertainty and real-world validity are not represented by these intervals.

## Extensions
Parameter calibration using authorized data; explicit abandonment; joint break placement; longer shift templates; employee preferences; hard minimum service coverage; legal constraints; solver-based weekly rostering; and sensitivity analysis over fairness and unresolved-request penalties.
