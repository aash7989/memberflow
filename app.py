from dataclasses import asdict
import pandas as pd
import streamlit as st
from memberflow.demand import generate
from memberflow.staffing import employees,roster,roster_frame,coverage,weekly_roster
from memberflow.simulation import simulate,metrics
from memberflow.optimization import FIXED,optimize
st.set_page_config(page_title="MemberFlow",layout="wide")
st.title("MemberFlow")
st.subheader("Service operations analytics for recreation and hospitality")
st.caption("Synthetic demand and employee scenarios. Results describe model assumptions, not observed facility performance.")
volume=st.sidebar.slider("Demand multiplier",.2,2.,1.,.1)
scale=st.sidebar.slider("Service-duration multiplier",.5,2.,1.,.1)
seed=st.sidebar.number_input("Synthetic day seed",0,100000,1000)
desk_rate=st.sidebar.number_input("Desk hourly rate (USD)",min_value=1.,value=18.)
sup_rate=st.sidebar.number_input("Supervisor hourly rate (USD)",min_value=1.,value=25.)
@st.cache_data
def optimized_starts(): return optimize([generate(s) for s in range(3)])
with st.spinner("Preparing staffing templates..."):
    best=optimized_starts()
people=employees(desk_rate,sup_rate)
policies={"Fixed":roster(FIXED,people),"Demand-aware":roster(best,people),
    "Surge buffer":roster(best+[420],people),"Extra supervisor":roster(best,people,extra_supervisor=True)}
arrivals=generate(int(seed),volume,scale)
rows=[dict(policy=name,**metrics(simulate(arrivals,shifts),shifts)) for name,shifts in policies.items()]
st.header("Policy comparison")
st.dataframe(pd.DataFrame(rows),use_container_width=True)
st.caption("Fixed and demand-aware use equal paid hours. Surge buffer adds 4 desk hours; extra supervisor adds 4 supervisor hours. Wages are assumptions; benefits and overhead are excluded.")
name=st.selectbox("Inspect policy",list(policies)); selected=policies[name]
st.line_chart(coverage(selected).set_index("minute"))
st.dataframe(roster_frame(selected),use_container_width=True)
st.header("One staff-hour transfer")
st.caption("This isolated sensitivity test shifts an existing employee's whole shift by one hour. It is not a reoptimized roster.")
frame=roster_frame(selected); desk_options=[i for i,s in enumerate(selected) if s.role=="desk"]
idx=st.selectbox("Desk shift to move",desk_options,format_func=lambda i:f"{selected[i].employee_id}: {selected[i].start/60:g}–{selected[i].end/60:g} hours after opening")
direction=st.radio("Shift direction",[-60,60],format_func=lambda x:"One hour earlier" if x<0 else "One hour later",horizontal=True)
from dataclasses import replace
trial=selected.copy(); s=trial[idx]
moved=replace(s,start=s.start+direction,end=s.end+direction,break_start=s.break_start+direction,break_end=s.break_end+direction)
e=next(e for e in people if e.employee_id==s.employee_id)
conflict=any(i!=idx and other.employee_id==s.employee_id and moved.start<other.end and moved.end>other.start for i,other in enumerate(trial))
if moved.start<e.available_start or moved.end>e.available_end or conflict:
    st.info("This transfer violates availability or overlaps another shift. Select a different shift/direction.")
else:
    trial[idx]=moved
    st.dataframe(pd.DataFrame([dict(scenario="Original",**metrics(simulate(arrivals,selected),selected)),
        dict(scenario="Transferred",**metrics(simulate(arrivals,trial),trial))]),use_container_width=True)
st.header("Weekly assignment balance")
mode=st.checkbox("Balance accumulated hours and evening shifts",value=True)
weekly,workloads=weekly_roster(best,people,balanced=mode)
st.dataframe(workloads,use_container_width=True)
st.caption("Evening shift: ends after 18:00, assuming an 08:00 opening. Workload balance is not a complete measure of employee fairness.")
st.download_button("Download weekly roster",roster_frame(weekly).to_csv(index=False),"synthetic_weekly_roster.csv","text/csv")
st.header("Synthetic requests")
st.dataframe(arrivals.head(100),use_container_width=True)
st.download_button("Download arrivals",arrivals.to_csv(index=False),"synthetic_arrivals.csv","text/csv")
st.caption("Completed-request wait summaries exclude unresolved requests; inspect unserved counts alongside waits. Protected breaks and hard shift ends can leave long requests unresolved.")
