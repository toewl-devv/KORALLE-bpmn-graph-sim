# KORALLE BPMN Graph Simulation

A simple Python-based simulator for processes modeled as **BPMN graphs**.

The project reads a BPMN 2.0 file, converts the process into a graph structure, and simulates the flow of work through the process.

## Features

* Parse `.bpmn` files
* Convert BPMN processes into a graph
* Simulate process execution
* Configure task processing time
* Support processing-time variance
* Model task capacity
* Model task failure probability
* Export simulation results to CSV
* Support gateway types such as `AND`, `OR`, and `XOR`

## Project Structure

```text
KORALLE-bpmn-graph-sim/
├── bpmn_parser.py       # Reads and parses BPMN files
├── graph_structure.py   # Graph and node data structures
├── graph_simulation.py  # Process simulation logic
├── process.py           # Process-related functionality
├── main.py              # Main entry point
├── complexdiagram.bpmn  # Example BPMN process
└── out.csv              # Example simulation output
```

## Usage

Clone the repository:

```bash
git clone https://github.com/toewl-devv/KORALLE-bpmn-graph-sim.git
```

Run the main program:

```bash
python main.py
```

An example BPMN process is provided in: `complexdiagram.bpmn`

## Results and Event Logs

After running a simulation, `simulate()` returns a `Results` object containing information about the simulation, including failures, waiting times, bottlenecks, and the event log.

```python
from graph_simulation import Simulation

simulation = Simulation("complexdiagram.bpmn", n=10)

results = simulation.simulate()

print(results.summary())
```

The `Results` object can also be used directly to inspect individual metrics:

```python
print(results.time_steps_taken)
print(results.fails)
print(results.node_times_spent_waiting)
print(results.edge_times_spent_waiting)

print(results.find_bottlenecks())
```

### Event Log

Every simulation produces an event log stored in `results.event_log`. Each event is represented as a dictionary containing information such as the simulation time, process, node, and event type.

```python
print(results.event_log)
```

For analysis with pandas, the event log can be converted directly into a DataFrame:

```python
import pandas as pd

event_log = pd.DataFrame(results.event_log)

print(event_log)
```

This produces a table similar to:

| time | process | node       | event   |
| ---: | ------: | ---------- | ------- |
|    1 |       0 | Start      | start   |
|    4 |       0 | Activity A | end     |
|    5 |       0 | Activity B | start   |
|    8 |       0 | Activity B | failure |
|   12 |       0 | Activity B | end     |

Some events contain additional information. For example, an `end` event records the waiting time and number of failures associated with that node. These are automatically included as additional columns when converting the log to a DataFrame.

The resulting DataFrame can then be used with the usual pandas functionality for filtering, grouping, plotting, and further analysis.

## BPMN Requirements
### BPMN Task Parameters

Task parameters can be stored in the BPMN element's `name` attribute using the following format:

```text
name;time;variance;capacity;fail_chance;gateway_type
```

For example:

```text
Process Order;5;1;2;0.05;AND
```

Where:

| Parameter      | Description                                          |
| -------------- | ---------------------------------------------------- |
| `name`         | Name of the task                                     |
| `time`         | Average processing time                              |
| `variance`     | Processing-time variance                             |
| `capacity`     | Number of tasks that can be processed simultaneously |
| `fail_chance`  | Probability of task failure, between `0` and `1`     |
| `gateway_type` | `AND`, `OR`, or `XOR`                                |

If these parameters are not specified, default values are used.

### BPMN Layout Requirements
The BPMN diagram requires a starting and ending node. This is so the simulation knows where to start and end a process.
The starting and ending node are automatically made to take 0 time and have infinite* capacity

Furthermore, the BPMN diagram must NOT have a possiblity of a process never reaching the ending node.
For example, if node A goes to B and C, and B goes to the end node, then A may not be an `XOR` node.

## Roadmap

Planned improvements include:

* Extend BPMN element support
* Improve process visualization
* Improve the simulation clock

