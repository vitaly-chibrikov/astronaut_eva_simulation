"""
simulate_eva.py
Run an EVA sequence and log astronaut state minute-by-minute
to a CSV file.

H = hard work           -> eva_work_hard_1min()
N = normal work         -> eva_work_normal_1min()
L = low physical work   -> eva_work_low_1min()
C = cognitive tasks     -> eva_task_cognitive_1min()
E = emergency response  -> eva_emergency_response_1min()
R = rest                -> eva_rest_drift_1min()

The CSV layout:

    ┌────┬──────┬─── Minute-1 ───┬─── Minute-2 ───┬ ... ┬ Minute-14 ┐
    │    │   B  │   1│ Task=H    │   2│ Task=H    │ ... │ 14│ Task=N │
    ├────┼──────┼────────────────┼────────────────┼─────┼───────────┤
    │task│  B   │        H       │        H       │ ... │     N     │
    │heart_rate│ 70   │   ...    │       ...      │     │    ...    │
    │... │                                    (all other variables) │
    └────┴──────┴────────────────┴────────────────┴─────┴───────────┘
"""

import pandas as pd
from astronaut import Astronaut

# -----------------------------------------------------------------
# 1. Task sequence 
# -----------------------------------------------------------------  
tasks = list("NNNNNNNNNNRRRRRLLLLLRRRRRHHHRRRRRRRCCCCCRRRRR")  

# -----------------------------------------------------------------
# 2. Initialise astronaut and logging table
# -----------------------------------------------------------------
astro = Astronaut()

# Use baseline keys + mission_elapsed_time for logging order
param_names = ["task"] + list(astro._BASELINE.keys()) + ["mission_elapsed_time"]

# DataFrame with these rows, columns added dynamically
log_df = pd.DataFrame(index=param_names)

# Helper to snapshot current astronaut state into a Series
def snapshot(label: str, task_letter: str) -> pd.Series:
    data = {"task": task_letter}
    # dynamic physio values
    for k in astro._BASELINE.keys():
        data[k] = getattr(astro, k)
    # mission time
    data["mission_elapsed_time"] = astro.mission_elapsed_time
    return pd.Series(data, name=label)

# Record baseline column "B"
log_df["B"] = snapshot("B", "B")

# -----------------------------------------------------------------
# Insert limit columns directly after baseline
# -----------------------------------------------------------------
log_df["MIN"] = pd.Series(
    {"task": "MIN", **{k: astro._LIMITS[k][0] for k in astro._BASELINE}, "mission_elapsed_time": 0.0}
)
log_df["MAX"] = pd.Series(
    {"task": "MAX", **{k: astro._LIMITS[k][1] for k in astro._BASELINE}, "mission_elapsed_time": 0.0}
)

# -----------------------------------------------------------------
# Main loop
# -----------------------------------------------------------------
for minute, letter in enumerate(tasks, start=1):
    if letter == "H":
        astro.eva_work_hard_1min()
    elif letter == "N":
        astro.eva_work_normal_1min()
    elif letter == "R":
        astro.eva_rest_drift_1min()
    elif letter == "L":
        astro.eva_work_low_1min()
    elif letter == "C":
        astro.eva_task_cognitive_1min()
    elif letter == "E":
        astro.eva_emergency_response_1min()
    else:
        raise ValueError(f"Unknown task letter: {letter}")

    column_label = str(minute)            # "1", "2", ...
    log_df[column_label] = snapshot(column_label, letter)

# -----------------------------------------------------------------
# Write to CSV
# -----------------------------------------------------------------

log_df = log_df.applymap(lambda v: round(float(v), 4) if isinstance(v, (int, float)) else v)
log_df.to_csv("eva_log.csv")           # no need for float_format now
print("Simulation complete. Log written to eva_log.csv")
