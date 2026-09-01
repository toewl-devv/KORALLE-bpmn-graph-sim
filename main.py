import time

import graph_simulation as gsim

my_sim = gsim.Simulation("diagram.bpmn", timescale=8, n=3, t=2)

my_sim.simulate(visualise=True)
for line in my_sim.results.event_log:
    print(line)
