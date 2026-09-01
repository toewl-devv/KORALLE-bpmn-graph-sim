import time

import graph_simulation as gsim

my_sim = gsim.Simulation("complexdiagram.bpmn", timescale=1, n=1, t=2)

my_sim.simulate(visualise=True)
for line in my_sim.results.event_log:
    print(line)
