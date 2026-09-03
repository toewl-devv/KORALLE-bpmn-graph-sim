import time

import bpmn_parser
import process
from copy import deepcopy
import random
from time import sleep
from collections import defaultdict

class Simulation():
    def __init__(self, file_name, n=1, t=0.0, timescale=1.0, time_step_length=1.0):
        if timescale <= 0:
            raise ValueError("timescale must be positive")
        if n < 1:
            raise ValueError("n must be >= 1")
        if t < 0.0:
            raise ValueError("t must be >= 0.0f")
        
        bpmn_xml = bpmn_parser.BpmnFile(file_name)
        process_graph = bpmn_xml.get_graph_structure()

        # need to find starting and ending nodes still (they have special ids!)
        # hence make the simulation start at the start, and end if all nodes are only on the end

        self.graph = process_graph 
        self.timescale = timescale
        self.time_step_length = time_step_length
        self.number_processes = n
        self.stagger = t
        self.results = Results(self.graph)
        self.processes = [process.Process(self.graph, i, start_time=i*self.time_step_length) for i in range(self.number_processes)]


    def reset_simulation(self):
        self.processes = [process.Process(self.graph, i, start_time=i*self.time_step_length) for i in range(self.number_processes)]

    def _step_simulation(self, time=None):
        finished_nodes = [[] for _ in self.processes]

        occupied = {}

        for process in self.processes:
            for running_node in process.current_running_nodes:
                occupied[running_node.id] = occupied.get(running_node.id, 0) + 1

        for process, finished in zip(self.processes, finished_nodes):
            nodes_added = []
            for node, time_left in zip(process.current_running_nodes, process.time_left_on_nodes):
                if node.id == self.graph.end.id:
                    if process.end_time is None:
                        process.end_time = time
                    pass
                elif time_left <= 0:
                    # does it fail at the end?
                    if random.random() < node.fail_chance:
                        time_left = node.given_time
                        self.results.fails[node.id] += 1
                        self.results.event_log.append(
                                {"time": time, "process": process.process_id, "node": node.name, "event": "failure"})
                    else:
                        if all(
                                occupied.get(child.id, 0) < child.capacity
                                for child in node.outgoing
                                ):
                            finished.append(node)
                            if time is not None:
                                self.results.event_log.append(
                                        {"time": time, "process": process.process_id, "node": node.name, "event": "end", "waited": self.results.node_times_spent_waiting[node.id], "fails": self.results.fails[node.id]})

                            # reserve slot for each outgoing
                            if node.gateway_type == "AND":
                                for out in node.outgoing:
                                    occupied[out.id] = occupied.get(out.id, 0) + 1
                                    nodes_added.append(out)
                            elif node.gateway_type == "XOR" or node.gateway_type == "OR":
                                next_node = random.choice(node.outgoing)
                                occupied[next_node.id] = occupied.get(next_node.id, 0) + 1
                                nodes_added.append(next_node)

                        else:
                            self.graph.time_spent_waiting += self.time_step_length

                            for out in node.outgoing:
                                if occupied.get(out.id, 0) >= out.capacity:
                                    self.results.edge_times_spent_waiting[(node.id, out.id)] += self.time_step_length

                            self.results.node_times_spent_waiting[node.id] += self.time_step_length
                else:
                    time_left -= self.time_step_length

            for node in finished:
                process.current_running_nodes.remove(node)
                for out in node.outgoing:
                    self.results.event_log.append(
                            {"time": time, "process": process.process_id, "node": out.name, "event": "start"})

            process.current_running_nodes.extend(nodes_added)

    def simulate(self, visualise=False):
        if self.graph.start == None:
            raise Exception("No starting node was found")
        if self.graph.end == None:
            raise Exception("No end node was found")

        self.results.reset()
        self.graph.reset_time_lefts() # randomise node.given_time
        self.reset_simulation()

        if visualise:
            print("Visualisation not yet implemented :(")

        end_node_id = self.graph.end.id

        # start the simulation
        time_step = 0.0
        while True:
            # check if all nodes are at the end
            self._step_simulation(time=time_step)

            if all(process.current_running_nodes == [self.graph.end] for process in self.processes):
                break


            time_step += self.time_step_length

        self.results.time_steps_taken = time_step
        self.results.processes_ran = self.processes

        return self.results

class Results():
    def __init__(self, graph):
        self.fails = {node_id: 0 for node_id in graph.nodes}
        self.time_steps_taken = 0.0
        self.node_times_spent_waiting = {node_id: 0.0 for node_id in graph.nodes}
        self.edge_times_spent_waiting = defaultdict(float)
        self.event_log = []
        self.graph = graph
        self.processes_ran = []

    def reset(self):
        self.__init__(self.graph)

    def find_bottlenecks(self):
        # We will score the bottleneck of a node by
        # two parameters: how much time it wastes, and how many times it failed.
        # We compute: fails * sum_{sources in node.incoming} (source.time_spent_waiting)
        bottlenecks = []
        for node in self.graph.nodes.values():
            fails = self.fails[node.id]

            time_wasted = sum(
                self.edge_times_spent_waiting.get((source.id, node.id), 0)
                for source in node.incoming
            )

            bottlenecks.append({"node_id": node.id, "node": node.name, "score": ((fails+1) * time_wasted + fails) / 100.0})

        return sorted(bottlenecks, key=lambda x: x["score"], reverse=True)

    def summary(self):
        return {
            "simulation_time": self.time_steps_taken,
            "total_failures": sum(self.fails.values()),
            "total_waiting_time": sum(self.edge_times_spent_waiting.values()),
            "top 3 bottlenecks": [bn["node"] for bn in self.find_bottlenecks()[:3]]
        }
