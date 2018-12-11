import sys
import time

sys.path.append('../')
from optimizer.graph_utils import Graph, Node

def test_create_node():
	node = Node(1, 1, 1)
	assert(node!=None)

def test_create_graph():
	g = Graph()
	g.add_node(Node(1,(1.0,1.0)))
	g.add_node(Node(2,(2.0,2.0)))
	g.add_edge(1, 2, 10, 'motoway', 'Yes', 0, (0,0,0,0,0,0))

	assert(g.adjacencyList[1] == [(2, 9.5)])

def find_path():
	g = Graph()
	g.add_node(Node(1,(1.0,1.0)))
	g.add_node(Node(2,(2.0,2.0)))
	g.add_node(Node(3,(3.0,3.0)))
	g.add_edge(1, 2, 10, 'motoway', 'Yes', 0, (0,0,0,0,0,0))
	g.add_edge(1, 3, 20, 'cycleway', 'No', 1, (1,1,0,0,0,0))
	g.add_edge(2, 3, 30, 'primary', 'Yes', 1, (0,0,0,1,1,1))
	g.add_edge(3, 1, 15, 'residential', 'No', 10, (1,0,0,0,0,0))
	assert(g.dijkstra_path(1, 2, use_a_star=True) == [(1.0, 1.0), (2.0, 2.0)])
