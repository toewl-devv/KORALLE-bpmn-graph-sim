import numpy as np

class Node:
    def __init__(self, 
                 name,
                 node_id,
                 sample_time,
                 sample_variance,
                 capacity, 
                 fail_chance,
                 gateway_type
                 ):
        """ Initialises the Node object """

        self.name = name
        self.id = node_id
        self.sample_time = sample_time
        self.sample_variance = sample_variance
        self.capacity = capacity
        self.fail_chance = fail_chance
        self.gateway_type = gateway_type
        self.given_time = sample_time

        self.outgoing = []
        self.incoming = []
        
class Graph:
    def __init__(self):
        self.nodes = {}
        self.start: Node | None = None
        self.end: Node | None = None

        self.time_spent_waiting = 0.0
        self.reset_time_lefts()

    def reset_time_lefts(self, randomise=True):
        for node in self.nodes.values():
            # Randomise the time given according to mean and variance given,
            # and ensure it isn't negative
            if randomise:
                node.given_time = max(0, 
                            np.random.normal(node.sample_time, np.sqrt(node.sample_variance))
                            )
                        
            else:
                node.given_time = node.sample_time

    def order(self):
        return len(self.nodes)

    def add_node(self, node: Node):
        self.nodes[node.id] = node

    def add_edge(self, a: Node, b: Node):
        a.outgoing.append(b)
        b.incoming.append(a)

    def get_node(self, node_id: str):
        return self.nodes[node_id]



