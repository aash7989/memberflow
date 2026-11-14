# MemberFlow
### Service Operations Analytics for Recreation and Hospitality

MemberFlow is a simulation-based decision-support project for evaluating front-desk staffing and supervisor coverage in recreation member services. It compares staffing policies under variable demand and quantifies trade-offs among waiting times, unresolved requests, paid staff-hours, and labor costs.

## Research questions
- How should front-desk coverage change when demand varies throughout the day?
- What happens when one paid staff-hour moves from one period to another?
- When does additional desk coverage offer more value than additional supervisor coverage?
- How do availability, protected breaks, and balanced shift assignments affect the roster?

## Features
- Reproducible synthetic arrivals with five request categories and variable handling times.
- Separate desk and supervisor queues with escalation after desk service.
- Named synthetic employees, role eligibility, availability windows, and daily/weekly hour limits.
- Four-hour shift templates with protected, staggered 15-minute paid breaks.
- Fixed, demand-aware, surge-buffer, and extra-supervisor policies.
- Constant-budget heuristic search for demand-aware desk coverage.
- Five-day assignment comparison using accumulated hours and evening-shift counts.
- Interactive Streamlit dashboard, roster exports, sensitivity analysis, and paired policy evaluation.
- Automated tests and continuous integration.

## Installation
Python 3.10 or later is required.
```bash
python -m venv .venv
```
Activate the environment:
```bash
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1
```
Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage
Launch the dashboard:
```bash
streamlit run app.py
```
Run a policy evaluation:
```bash
python -m memberflow.experiment --replications 20
```
Run tests:
```bash
python -m pytest -q
```
The dashboard generates inputs directly. Experiment outputs are written to `output/`.
The `examples/` directory contains a small reproducible demonstration run; larger experiments can use `--replications 100`.

## Data generation and provenance
All member-service requests, employee records, availability windows, handling times, and wage rates are synthetic. The model represents a hypothetical 12-hour service day beginning at 08:00. No University of Cincinnati operational records, employee details, or member information are used. Results describe configured scenarios rather than observed institutional performance.

See [the data card](docs/DATA_CARD.md) for distributions, schema, and provenance.

## Staffing policies
| Policy | Desk coverage | Supervisor coverage |
|---|---|---|
| Fixed | Six 4-hour shifts at fixed start times | Three 4-hour shifts |
| Demand-aware | Six 4-hour shifts selected through heuristic search | Three 4-hour shifts |
| Surge buffer | Demand-aware plus one 4-hour desk shift | Three 4-hour shifts |
| Extra supervisor | Demand-aware | Base coverage plus one 4-hour supervisor shift |

Fixed and demand-aware use equal paid hours and identical assumed wages. Buffer and extra-supervisor policies add capacity and cost. At the default rates, base scheduled labor costs $732 per day: 24 desk hours at $18 and 12 supervisor hours at $25. Paid breaks reduce active service capacity without reducing paid hours. Benefits, overhead, overtime, and employment taxes are excluded.

## Evaluation
Policy comparisons reuse identical arrival and service realizations within each synthetic day. Training seeds (0–2) are separate from evaluation seeds (1000 onward). Outputs include completed-request mean and 95th-percentile wait, unresolved requests, paid and active hours, wage cost, paired waiting-time differences, weekly rosters, and workload spreads.

Completed-only waiting metrics must be interpreted alongside unresolved counts. A policy that leaves more requests unresolved may appear artificially faster. Confidence intervals quantify simulation variability conditional on model assumptions, not real-world predictive accuracy.

## Scheduling balance
The assignment heuristic considers accumulated paid hours and, for evening shifts, accumulated evening assignments. Comparisons report weekly paid-hour spread and evening-shift-count spread by role. An evening shift ends after 18:00. These are transparent workload-balance indicators, not a complete or guaranteed measure of fairness.

## Repository structure
```text
app.py                     Interactive dashboard
memberflow/demand.py       Synthetic request generation
memberflow/staffing.py     Employee availability, breaks, assignments and coverage
memberflow/simulation.py   Desk and supervisor queue simulation
memberflow/optimization.py Coverage-template search
memberflow/experiment.py   Replicated experiments and exports
tests/                     Automated checks
docs/                      Data card, methods and architecture
examples/                  Synthetic demonstration outputs
```

## Scope and limitations
The model uses nonpreemptive service with hard break and shift boundaries. A service begins only when it can finish within an active interval. Request ordering follows arrival order, but a long request that cannot fit may be bypassed by a later shorter request; this is a fit-aware queue, not strict FCFS. Requests without a feasible remaining service slot are recorded as unresolved. Supervisors do not serve ordinary desk requests.

Coverage search and employee assignment are heuristics, not globally optimal schedules. Breaks are predefined and staggered within simultaneous templates, not jointly optimized. Wage rates, escalation rules, and employee availability are illustrative. The system does not establish labor-law compliance, incorporate employee preferences, model customer abandonment, forecast real demand, or validate customer satisfaction.

Detailed assumptions and extensions are documented in [methodology](docs/METHODOLOGY.md) and [architecture](docs/ARCHITECTURE.md).
