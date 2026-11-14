import pandas as pd
import pytest
from memberflow.demand import generate
from memberflow.staffing import Shift,employees,roster,weekly_roster,coverage
from memberflow.simulation import simulate,metrics
from memberflow.optimization import FIXED

def request(times,durations,escalation=None):
    return pd.DataFrame(dict(request_id=range(len(times)),arrival_min=times,
        service_min=durations,supervisor_required=escalation or [False]*len(times),
        supervisor_min=[2.]*len(times),synthetic=[True]*len(times)))
def shift(): return Shift("D01","desk",0,240,90,105,18)
def test_seed(): pd.testing.assert_frame_equal(generate(4),generate(4))
def test_invalid_demand():
    with pytest.raises(ValueError): generate(volume=-1)
def test_basic_queue():
    e=simulate(request([0,0],[3,2]),[shift()])
    assert list(e.desk_wait_min)==[0,3]
def test_break_is_protected():
    e=simulate(request([89],[4]),[shift()])
    assert e.iloc[0].desk_start_min==105
def test_hard_end():
    e=simulate(request([239],[3]),[shift()])
    assert e.iloc[0].status=="unserved_desk"
def test_no_supervisor():
    e=simulate(request([0],[1],[True]),[shift()])
    assert e.iloc[0].status=="unserved_supervisor"
def test_escalation_ready_order():
    d2=Shift("D02","desk",0,240,90,105,18)
    sup=Shift("S01","supervisor",0,240,90,105,25)
    e=simulate(request([0,1],[10,1],[True,True]),[shift(),d2,sup])
    assert list(e.completion_min)==[12,4]
def test_empty():
    assert metrics(simulate(generate(0,0),[]),[])['arrivals']==0
def test_paid_break_cost():
    m=metrics(simulate(request([],[]),[shift()]),[shift()])
    assert m['paid_staff_hours']==4 and m['active_staff_hours']==3.75 and m['labor_cost']==72
def test_availability_and_daily_limit():
    people=employees(); shifts=roster(FIXED,people)
    for e in people:
        own=[s for s in shifts if s.employee_id==e.employee_id]
        assert sum(s.paid_hours for s in own)<=e.max_daily_hours
        assert all(s.start>=e.available_start and s.end<=e.available_end for s in own)
def test_weekly_limits_and_nonoverlap():
    for balanced in [False,True]:
        shifts,loads=weekly_roster(FIXED,balanced=balanced)
        assert (loads.weekly_hours<=32).all()
        for day in range(5):
            for e in employees():
                own=sorted([s for s in shifts if s.day==day and s.employee_id==e.employee_id],key=lambda s:s.start)
                assert all(a.end<=b.start for a,b in zip(own,own[1:]))
def test_coverage_break():
    c=coverage([shift()]).set_index("minute")
    assert c.loc[90,"desk_active"]==0 and c.loc[90,"desk_scheduled"]==1
def test_equal_budget():
    assert sum(s.paid_hours for s in roster(FIXED) if s.role=="desk")==24
