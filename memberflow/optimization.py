"""Heuristic template search; not a global optimizer."""
from .staffing import roster
from .simulation import simulate,objective
FIXED=[0,0,240,240,480,480]
def optimize(training):
    if not training: raise ValueError("Training days required")
    # Every candidate has six 4h desk shifts: a constant 24 paid desk-hour budget.
    starts=FIXED.copy()
    def score(candidate):
        try: shifts=roster(candidate)
        except ValueError: return float("inf")
        return sum(objective(simulate(day,shifts)) for day in training)/len(training)
    best=score(starts)
    for _ in range(2):
        chosen=None; chosen_score=best
        for i in range(len(starts)):
            for new_start in range(0,481,60):
                trial=starts.copy(); trial[i]=new_start; trial.sort()
                if trial==starts: continue
                value=score(trial)
                if value<chosen_score-1e-9:
                    chosen,chosen_score=trial,value
        if chosen is None: break
        starts,best=chosen,chosen_score
    return starts
