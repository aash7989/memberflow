"""Named synthetic employees, paid breaks, availability and roster balancing."""
from dataclasses import dataclass, asdict
import pandas as pd

@dataclass(frozen=True)
class Employee:
    employee_id: str
    role: str
    available_start: float = 0
    available_end: float = 720
    hourly_rate: float = 18
    max_daily_hours: float = 8
    max_weekly_hours: float = 32

@dataclass(frozen=True)
class Shift:
    employee_id: str
    role: str
    start: float
    end: float
    break_start: float
    break_end: float
    hourly_rate: float
    day: int = 0
    @property
    def paid_hours(self): return (self.end-self.start)/60
    @property
    def active_minutes(self): return self.end-self.start-(self.break_end-self.break_start)
    @property
    def evening(self): return self.end>600
    def windows(self):
        return [(a,b) for a,b in [(self.start,self.break_start),(self.break_end,self.end)] if b>a]

def employees(desk_rate=18.,supervisor_rate=25.):
    # Identifiers and availability describe hypothetical employees only.
    return [Employee(f"D{i+1:02}","desk",0 if i!=6 else 240,720 if i!=7 else 480,desk_rate) for i in range(8)]+[
        Employee(f"S{i+1:02}","supervisor",hourly_rate=supervisor_rate) for i in range(3)]

def assign(starts, role, people, day=0, history=None, balanced=True):
    """Assign 4h templates. Candidate score balances accumulated hours and evenings."""
    history=history or {}; assigned=[]
    for start in sorted(starts):
        end=start+240
        eligible=[]
        for e in people:
            if e.role!=role or start<e.available_start or end>e.available_end: continue
            own=[s for s in assigned if s.employee_id==e.employee_id]
            if any(start<s.end and end>s.start for s in own): continue
            hours=sum(s.paid_hours for s in own)
            previous=history.get(e.employee_id,{"hours":0,"evenings":0})
            if hours+4>e.max_daily_hours or previous["hours"]+hours+4>e.max_weekly_hours: continue
            evening_load=previous["evenings"]+sum(s.evening for s in own)
            score=(previous["hours"]+hours+4*evening_load if end>600 else previous["hours"]+hours) if balanced else 0
            eligible.append((score,e.employee_id,e))
        if not eligible:
            raise ValueError(f"No available {role} employee for day {day}, start {start}")
        _,_,e=min(eligible)
        # Stagger breaks for templates starting together; breaks remain within each shift.
        simultaneous=sum(s.start==start for s in assigned)
        bs=start+90+15*(simultaneous%4)
        assigned.append(Shift(e.employee_id,role,start,end,bs,bs+15,e.hourly_rate,day))
    return assigned

def roster(desk_starts,people=None,day=0,history=None,balanced=True,extra_supervisor=False):
    people=people if people is not None else employees()
    sup=[0,240,480]+([480] if extra_supervisor else [])
    return assign(desk_starts,"desk",people,day,history,balanced)+assign(sup,"supervisor",people,day,history,balanced)

def roster_frame(shifts):
    return pd.DataFrame([dict(asdict(s),paid_hours=s.paid_hours,active_hours=s.active_minutes/60,evening=s.evening) for s in shifts])

def weekly_roster(starts,people=None,days=5,balanced=True):
    people=people if people is not None else employees()
    history={e.employee_id:{"hours":0.,"evenings":0} for e in people}
    all_shifts=[]
    for day in range(days):
        shifts=roster(starts,people,day,history,balanced)
        for s in shifts:
            history[s.employee_id]["hours"]+=s.paid_hours
            history[s.employee_id]["evenings"]+=int(s.evening)
        all_shifts.extend(shifts)
    rows=[dict(employee_id=e.employee_id,role=e.role,weekly_hours=history[e.employee_id]["hours"],
               evening_shifts=history[e.employee_id]["evenings"]) for e in people]
    return all_shifts,pd.DataFrame(rows)

def coverage(shifts):
    rows=[]
    for t in range(0,720,15):
        row={"minute":t}
        for role in ["desk","supervisor"]:
            relevant=[s for s in shifts if s.role==role]
            row[role+"_scheduled"]=sum(s.start<=t<s.end for s in relevant)
            row[role+"_active"]=sum(any(a<=t<b for a,b in s.windows()) for s in relevant)
        rows.append(row)
    return pd.DataFrame(rows)
