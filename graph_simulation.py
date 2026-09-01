import bpmn_parser
from copy import deepcopy
import random
from time import sleep
from graphviz import Digraph
import pygame

class Simulation():
    def __init__(self, file_name, n=1, t=0.0, timescale=1.0):
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
        self.processes = n
        self.stagger = t
        self.results = self.Results(self.graph)

    class Results():
        def __init__(self, graph):
            self.fails = {node_id: 0 for node_id in graph.nodes}
            self.time_steps_taken = 0
            self.node_times_spent_waiting = {node_id: 0 for node_id in graph.nodes}
            self.event_log = []
            self.graph = graph

        def reset(self):
            self.__init__(self.graph)


    def _step_simulation(self, current_running_nodes,
                         simulated_graphs, ends, time=None):
        finished_nodes = [[] for _ in current_running_nodes]

        occupied = {}

        for process in current_running_nodes:
            for running_node in process:
                occupied[running_node.id] = occupied.get(running_node.id, 0) + 1

        for i, (process, graph, end, finished) in enumerate(zip(current_running_nodes,
                                                                simulated_graphs,
                                                                ends,
                                                                finished_nodes)):
            for node in process:
                if node == end[0]:
                    pass
                elif node.time_left <= 0:
                    # does it fail at the end?
                    if random.random() < node.fail_chance:
                        node.time_left = node.sample_time
                        self.results.fails[node.id] += 1
                        self.results.event_log.append(
                                {"time": time, "process": i, "node": node.name, "event": "failure"})
                    else:
                        if all(
                                occupied.get(child.id, 0) < child.capacity
                                for child in node.outgoing
                                ):
                            finished.append(node)
                            if time is not None:
                                self.results.event_log.append(
                                        {"time": time, "process": i, "node": node.name, "event": "end"})

                            # reserve slot for each outgoing
                            for out in node.outgoing:
                                occupied[out.id] = occupied.get(out.id, 0) + 1
                        else:
                            graph.time_spent_waiting += 1
                            self.results.node_times_spent_waiting[node.id] += 1
                else:
                    node.time_left -= 1
            for node in finished:
                process.remove(node)
                process.extend(node.outgoing)
                for out in node.outgoing:
                    self.results.event_log.append(
                            {"time": time, "process": i, "node": out.name, "event": "start"})

    def simulate(self, visualise=False):
        if self.graph.start == None:
            raise Exception("No starting node was found")
        if self.graph.end == None:
            raise Exception("No end node was found")

        self.results.reset()

        if visualise:
            pygame.init()
            screen = pygame.display.set_mode((1200, 800))

        simulated_graphs = [deepcopy(self.graph) for _ in range(self.processes)]

        for graph in simulated_graphs:
            graph.reset_time_lefts()

        current_running_nodes = [[graph.start] for graph in simulated_graphs]

        for i, nodes in enumerate(current_running_nodes):
            nodes[0].time_left += self.stagger * i


        time_step = 0
        ends = [[graph.end] for graph in simulated_graphs]

        # start the simulation
        time_step = 0
        while True:
            if visualise:
                self._visualise_graph(
                    current_running_nodes,
                    simulated_graphs[0], screen
                    )
                sleep(1.0 / self.timescale)

            if all(process == [graph.end] for process, graph in zip(current_running_nodes, simulated_graphs)):
                break
            self._step_simulation(current_running_nodes,
                                  simulated_graphs,
                                  ends,
                                  time=time_step + 1)
            time_step += 1

        self.results.time_steps_taken = time_step


    def _visualise_graph(self, current_running_nodes, simulated_graph, screen):
        dot = Digraph()

        # Find which processes are currently on each node
        running = {}

        for process_id, nodes in enumerate(current_running_nodes):
            for node in nodes:
                running.setdefault(node.id, []).append(process_id)

        # Add nodes
        for node_id, node in simulated_graph.nodes.items():
            if node_id in running:
                processes = ", ".join(
                    f"P{p}" for p in running[node_id]
                )

                dot.node(
                    str(node_id),
                    f"{node.name}\n[{processes}]",
                    style="filled",
                    fillcolor="lightblue"
                )
            else:
                dot.node(str(node_id), node.name)

        # Add edges
        for node in simulated_graph.nodes.values():
            for child in node.outgoing:
                dot.edge(str(node.id), str(child.id))

        dot.render("simulation", format="png", cleanup=True)
        image = pygame.image.load("simulation.png")
        screen.fill((255,255,255))
        screen.blit(image, (0,0))
        pygame.display.flip()
