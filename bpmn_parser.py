from os import wait
import xml.etree.ElementTree as ET
from pathlib import Path

import graph_structure as gs

def check_file(file_name):
    path = Path(file_name)

    if path.suffix != ".bpmn":
        raise ValueError("file must end with .bpmn")

    if not path.is_file():
        raise ValueError("file not found")

class BpmnFile:
    def __init__(self, file_name):
        # raise an error if the file is invalid
        check_file(file_name)
        
        # tree is a ElementTree object which makes it easy to read the xml file
        parser = ET.XMLParser(encoding="utf-8")
        tree = ET.parse(file_name, parser=parser)
        
        if tree is None:
            raise Exception("no tree found in bpmn file")
        # root <==> <definitions/> for a BPMN file
        root = tree.getroot()
        if root.tag.startswith("{"):
            namespace = root.tag[root.tag.find("{") + 1 : root.tag.find("}")]
        else:
            raise Exception("no namespace found in BPMN file")

        ns = {"bpmn" : namespace}
        process = root.find("bpmn:process", ns)

        if process is None:
            raise Exception("no process element found in bpmn")
        
        self.process = process
        self.tree = tree
        self.root = root

    def get_graph_structure(self):
        process_nodes = []
        graph = gs.Graph()
        for child in self.process:
            if child.tag.endswith("sequenceFlow"):
                continue
            
            node_data = child.get("name")

            # move below into new function
            if node_data:
                try:
                    name, time, variance, capacity, fail_chance = node_data.split(";")
                    time = float(time)
                    variance = float(variance)
                    capacity = int(capacity)
                    fail_chance = float(fail_chance)
                    gatetype = str("OR")
                except ValueError:
                    raise ValueError(f'Invalid task format: "{node_data}". Expected "name;time;variance;capacity;failchance"')
            else:
                name = child.tag.split("}")[-1]
                time = 1.0
                variance = 0.0
                capacity = 1
                fail_chance = 0.0
                gatetype = "OR"

            # TODO validate values

            node_id = child.get("id") or ""
            node_to_add = gs.Node(
                         name,
                         node_id,
                         time,
                         variance,
                         capacity, 
                         fail_chance,
                         gatetype)

            graph.add_node(node_to_add)
            if child.tag.endswith("startEvent"):
               graph.start = node_to_add 
            elif child.tag.endswith("endEvent"):
                graph.end = node_to_add
            
        for child in self.process:
            if not child.tag.endswith("sequenceFlow"):
                continue
            
            source_node = graph.nodes[child.get("sourceRef")]
            target_node = graph.nodes[child.get("targetRef")]

            if source_node is None or target_node is None:
                raise Exception("sequenceFlow references an unknown node")
            
            graph.add_edge(source_node, target_node)

        
        return graph

