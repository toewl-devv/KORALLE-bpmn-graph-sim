import time
import pandas as pd

import graph_simulation as gsim

my_sim = gsim.Simulation("complexdiagram.bpmn", n=1)

results = my_sim.simulate(time_step_length=0.1)
df = pd.DataFrame(results.event_log)
print(df.head(20))
print(results.find_bottlenecks())
print(results.summary())
