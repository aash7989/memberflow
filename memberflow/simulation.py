"""Nonpreemptive two-stage queue with protected breaks and hard shift ends."""
import math
import pandas as pd

def reserve(ready,duration,shifts,free):
    if duration < 0: raise ValueError("Service durations must be nonnegative")
    options=[]
    for i,s in enumerate(shifts):
        for a,b in s.windows():
            start=max(ready,free[i],a)
            if start+duration<=b and start<b:
                options.append((start,i,start+duration)); break
    if not options: return None
    start,i,end=min(options)
    free[i]=end
    return start,end,shifts[i].employee_id

def simulate(arrivals,shifts):
    desk=[s for s in shifts if s.role=="desk"]
    supervisors=[s for s in shifts if s.role=="supervisor"]
    da=[s.start for s in desk]; sa=[s.start for s in supervisors]
    rows=[]; pending=[]
    for row in arrivals.sort_values(["arrival_min","request_id"]).to_dict("records"):
        r=dict(row,status="unserved_desk",desk_start_min=math.nan,desk_end_min=math.nan,
               supervisor_start_min=math.nan,completion_min=math.nan,desk_wait_min=math.nan,
               supervisor_wait_min=math.nan,total_wait_min=math.nan,desk_employee=None,supervisor_employee=None)
        slot=reserve(row["arrival_min"],row["service_min"],desk,da)
        if slot:
            start,end,eid=slot
            r.update(desk_start_min=start,desk_end_min=end,desk_wait_min=start-row["arrival_min"],desk_employee=eid)
            if row["supervisor_required"]:
                r["status"]="unserved_supervisor"; pending.append((end,len(rows)))
            else:
                r.update(status="completed",completion_min=end,supervisor_wait_min=0.,total_wait_min=r["desk_wait_min"])
        rows.append(r)
    for ready,idx in sorted(pending):
        r=rows[idx]; slot=reserve(ready,r["supervisor_min"],supervisors,sa)
        if slot:
            start,end,eid=slot
            r.update(status="completed",supervisor_start_min=start,completion_min=end,
                     supervisor_wait_min=start-ready,total_wait_min=r["desk_wait_min"]+start-ready,supervisor_employee=eid)
    cols=list(arrivals.columns)+["status","desk_start_min","desk_end_min","supervisor_start_min","completion_min",
         "desk_wait_min","supervisor_wait_min","total_wait_min","desk_employee","supervisor_employee"]
    return pd.DataFrame(rows,columns=cols)

def metrics(events,shifts):
    done=events[events.status=="completed"]; waits=done.total_wait_min
    return dict(arrivals=len(events),completed=len(done),unserved=len(events)-len(done),
        mean_wait_min=float(waits.mean()) if len(done) else None,
        p95_wait_min=float(waits.quantile(.95)) if len(done) else None,
        within_5min_fraction_all=float((waits<=5).sum()/len(events)) if len(events) else None,
        paid_staff_hours=sum(s.paid_hours for s in shifts),
        active_staff_hours=sum(s.active_minutes for s in shifts)/60,
        labor_cost=sum(s.paid_hours*s.hourly_rate for s in shifts))

def objective(events):
    return float(events.total_wait_min.fillna(0).sum()+120*(events.status!="completed").sum())
