"""Synthetic demand. All times are minutes since an illustrative 08:00 opening."""
import numpy as np
import pandas as pd
RATES = [12,18,28,42,38,26,20,30,46,40,22,12]
TYPES = ["access_question","registration","account_issue","guest_pass","complex_concern"]
PROBS = [.40,.15,.15,.25,.05]
MEANS = [1.5,7,5,3,4]
ESCALATION = [.01,.05,.20,.02,.90]
COLUMNS = ["request_id","arrival_min","request_type","service_min","supervisor_required","supervisor_min","synthetic"]
def generate(seed=0, volume=1.0, service_scale=1.0):
    if volume < 0 or service_scale <= 0:
        raise ValueError("Volume must be nonnegative and service scale positive")
    rng=np.random.default_rng(seed)
    rows=[]
    for h,rate in enumerate(RATES):
        times=np.sort(rng.uniform(60*h,60*(h+1),rng.poisson(rate*volume)))
        for t in times:
            k=int(rng.choice(5,p=PROBS)); escalation=bool(rng.random()<ESCALATION[k])
            rows.append(dict(arrival_min=float(t),request_type=TYPES[k],
                service_min=float(rng.gamma(2,MEANS[k]*service_scale/2)),
                supervisor_required=escalation,
                supervisor_min=float(rng.gamma(2,3*service_scale)) if escalation else 0.,synthetic=True))
    df=pd.DataFrame(rows,columns=COLUMNS[1:]).sort_values("arrival_min").reset_index(drop=True)
    df.insert(0,"request_id",range(len(df)))
    return df
