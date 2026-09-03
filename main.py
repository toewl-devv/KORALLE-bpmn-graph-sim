import time
import pandas as pd

import graph_simulation as gsim

my_sim = gsim.Simulation("complexdiagram.bpmn", n=8, time_step_length=0.1)

results = my_sim.simulate()
df = pd.DataFrame(results.event_log)
print(df.head(20))
print([(process.start_time, process.end_time) for process in results.processes_ran])
