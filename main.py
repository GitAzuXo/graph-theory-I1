import numpy as np
import networkx as nx
from tabulate import tabulate

class SchedulingGraph:
    def __init__(self, file_path):
        self.tasks = {}
        self.graph = nx.DiGraph()
        self.load_constraints(file_path)
        self.add_virtual_vertices()

    #Loading the constraint files
    def load_constraints(self, file_path):
        with open(file_path, 'r') as f:
            for line in f:
                values = list(map(int, line.split()))
                task, duration, *predecessors = values
                self.tasks[task] = {'duration': duration, 'predecessors': predecessors}
                for pred in predecessors:
                    self.graph.add_edge(pred, task, weight=duration)

    #Adding the alphas and omegas
    def add_virtual_vertices(self):
        self.graph.add_node("α")
        for task in self.tasks:
            if not self.tasks[task]['predecessors']:
                self.graph.add_edge("α", task, weight=0)
        
        self.graph.add_node("ω")
        for task in self.tasks:
            if not list(self.graph.successors(task)):
                self.graph.add_edge(task, "ω", weight=self.tasks[task]['duration'])

    #Displaying the graph as an adjacency matrix
    def display_graph_matrix(self):
        nodes = ["α"] + sorted([node for node in self.graph.nodes() if isinstance(node, int)]) + ["ω"]
        size = len(nodes)
        matrix = np.full((size, size), "*", dtype=object)
        node_indices = {node: idx for idx, node in enumerate(nodes)}
        
        for u, v, data in self.graph.edges(data=True):
            matrix[node_indices[u]][node_indices[v]] = data['weight']
        
        headers = [" "] + nodes
        table_data = [[nodes[i]] + list(row) for i, row in enumerate(matrix)]
        
        print("\nGraph as Adjacency Matrix:")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    #Checking the presence of a cycle
    def check_cycles(self):
        try:
            nx.find_cycle(self.graph, orientation='original')
            print("Cycle detected! The graph is not a valid scheduling graph.")
            return True
        except nx.NetworkXNoCycle:
            print("No cycles detected.")
            return False
    
    #Calculations of earliest dates, latest dates, floats
    def compute_scheduling(self):
        if self.check_cycles():
            return
        
        topological_order = list(nx.topological_sort(self.graph))
        earliest_start = {node: 0 for node in self.graph.nodes()}
        latest_start = {node: float('inf') for node in self.graph.nodes()}
        
        for node in topological_order:
            for successor in self.graph.successors(node):
                earliest_start[successor] = max(earliest_start[successor], earliest_start[node] + self.graph[node][successor]['weight'])
        
        project_end = earliest_start["ω"]
        latest_start["ω"] = project_end
        
        for node in reversed(topological_order):
            for predecessor in self.graph.predecessors(node):
                latest_start[predecessor] = min(latest_start[predecessor], latest_start[node] - self.graph[predecessor][node]['weight'])
        
        scheduling_data = []
        for node in self.graph.nodes():
            float_time = latest_start[node] - earliest_start[node]
            scheduling_data.append([node, earliest_start[node], latest_start[node], float_time])
        
        print("\nTask Scheduling:")
        print(tabulate(scheduling_data, headers=["Task", "Earliest Start", "Latest Start", "Float"], tablefmt="grid"))
        
        self.find_critical_path(earliest_start, latest_start)
        
    def find_critical_path(self, earliest, latest):
        critical_path = [node for node in self.graph.nodes() if earliest[node] == latest[node] and node not in ["α", "ω"]]
        print("\nCritical Path:", " -> ".join(map(str, ["α"] + critical_path + ["ω"])))

#Main loop of the program
if __name__ == "__main__":
    while True:
        print("Welcome to this Graph Theory Scheduling program !")
        choice = input("Please enter the number of your constraint file (1-14) or quit: ")
        if choice == "quit":
            exit()
        else:
            file_path = "constraints/table " + choice + ".txt"
            scheduler = SchedulingGraph(file_path)
            scheduler.display_graph_matrix()
            scheduler.compute_scheduling()
            input("Please press enter to restart the program")
