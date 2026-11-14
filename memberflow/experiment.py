from pathlib import Path
from dataclasses import asdict
import argparse
import pandas as pd
from .demand import generate
from .staffing import employees,roster,roster_frame,weekly_roster,coverage
from .simulation import simulate,metrics
from .optimization import FIXED,optimize

def run(output="output",replications=20):
    if replications<2: raise ValueError("At least two replications required")
    out=Path(output); out.mkdir(parents=True,exist_ok=True)
    training=[generate(s) for s in range(3)]
    optimized=optimize(training)
    policies={"fixed":roster(FIXED),"demand_aware":roster(optimized),
        "surge_buffer":roster(optimized+[420]),
        "extra_supervisor":roster(optimized,extra_supervisor=True)}
    pd.DataFrame([asdict(e) for e in employees()]).to_csv(out/"synthetic_employees.csv",index=False)
    generate(1000).to_csv(out/"synthetic_arrivals.csv",index=False)
    rows=[]
    for name,shifts in policies.items():
        roster_frame(shifts).to_csv(out/f"roster_{name}.csv",index=False)
        coverage(shifts).to_csv(out/f"coverage_{name}.csv",index=False)
    for seed in range(1000,1000+replications):
        for scenario,volume,scale in [("base",1.,1.),("surge",1.4,1.),("slow_service",1.,1.3)]:
            day=generate(seed,volume,scale)
            for name,shifts in policies.items():
                events=simulate(day,shifts)
                rows.append(dict(seed=seed,scenario=scenario,policy=name,**metrics(events,shifts)))
                if seed==1000 and scenario=="base":
                    events.to_csv(out/f"synthetic_events_{name}.csv",index=False)
    results=pd.DataFrame(rows); results.to_csv(out/"replications.csv",index=False)
    summary=results.groupby(["scenario","policy"]).agg(
        mean_wait_min=("mean_wait_min","mean"),mean_daily_p95_wait_min=("p95_wait_min","mean"),
        mean_unserved=("unserved","mean"),mean_paid_hours=("paid_staff_hours","mean"),
        mean_labor_cost=("labor_cost","mean"))
    summary.to_csv(out/"summary.csv")
    wide=results.pivot(index=["scenario","seed"],columns="policy",values="mean_wait_min")
    delta=wide.demand_aware-wide.fixed
    ci=delta.groupby(level="scenario").agg(["mean","std","count"])
    ci["approx_95ci_low"]=ci["mean"]-1.96*ci["std"]/ci["count"]**.5
    ci["approx_95ci_high"]=ci["mean"]+1.96*ci["std"]/ci["count"]**.5
    ci.to_csv(out/"paired_wait_differences.csv")
    fairness=[]
    for balanced in [False,True]:
        shifts,workloads=weekly_roster(optimized,balanced=balanced)
        label="balanced" if balanced else "id_order"
        roster_frame(shifts).to_csv(out/f"weekly_roster_{label}.csv",index=False)
        workloads.to_csv(out/f"weekly_workloads_{label}.csv",index=False)
        for role,group in workloads.groupby("role"):
            fairness.append(dict(assignment=label,role=role,
                hour_spread=group.weekly_hours.max()-group.weekly_hours.min(),
                evening_shift_spread=group.evening_shifts.max()-group.evening_shifts.min()))
    pd.DataFrame(fairness).to_csv(out/"fairness_comparison.csv",index=False)
    return summary

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--output",default="output")
    p.add_argument("--replications",type=int,default=20); args=p.parse_args()
    print(run(args.output,args.replications).to_string())
