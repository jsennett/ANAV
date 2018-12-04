from graph_utils import *
import json
from time import time
from pprint import pprint
import amherst

def test_graph():
    g = Graph()

    #          name, x, y, elev
    g.add_node(Node('A', (0, 0), 0))
    g.add_node(Node('B', (1, 0), 1))
    g.add_node(Node('C', (0, 1), 2))
    g.add_node(Node('D', (1, 1), -1))
    g.add_node(Node('E', (2, 2), 0))

    g.add_edge('A', 'B')
    g.add_edge('A', 'C')
    g.add_edge('B', 'A')
    g.add_edge('B', 'D')
    g.add_edge('C', 'A')
    g.add_edge('C', 'D')
    g.add_edge('D', 'B')
    g.add_edge('D', 'C')
    g.add_edge('D', 'E')
    g.add_edge('E', 'D')

    return g

def test_a_star():

    g = Graph()

    g.add_node(Node('A', (0, 0), 0))
    g.add_node(Node('B', (-1, -1), 0))
    g.add_node(Node('C', (-2, -2), 0))
    g.add_node(Node('D', (1, 1), 0))
    g.add_node(Node('E', (2, 2), 0))

    g.add_edge('A', 'B')
    g.add_edge('B', 'C')
    g.add_edge('C', 'E')
    g.add_edge('A', 'D')
    g.add_edge('D', 'E')

    path = g.dijkstra_path('A', 'E', use_a_star=True)

    print(path)
    return g


def test_dijkstra():
    g = test_graph()
    path = g.dijkstra_path('A', 'E')
    print(path)


def test_graph_amherst_data():

    with open(node_filename, 'r') as f:
        nodes = json.load(f)

    with open(edge_filename, 'r') as f:
        edges = json.load(f)

    g = Graph()

    for n in nodes.keys():
        id = n
        ele = nodes[n][0]
        lat, lon = nodes[n][1]
        g.add_node(Node(id, (lat, lon), ele))

    for node in edges.keys():
        for neighbor in edges[node]:
            g.add_edge(node, str(neighbor))

    print('Nodes in g:', len(g.nodes))
    print('Nodes in adjList:', len(g.adjacencyList))

    return g


def test_short_path(node_filename, edge_filename):

    g = test_graph_real_data(node_filename, edge_filename)
    shortest_path = g.dijkstra_path("4602188751", "64050988", use_a_star=True)
    print(shortest_path)

def test_short_path_2(node_filename, edge_filename):

    g = test_graph_real_data(node_filename, edge_filename)
    shortest_path = g.dijkstra_path("66739574", "66728173", use_a_star=True)
    print(shortest_path)

def test_medium_short_path(node_filename, edge_filename):

    t1 = time()
    g = test_graph_real_data(node_filename, edge_filename)
    t2 = time()
    shortest_path = g.dijkstra_path("66764370", "66626598", use_a_star=True)
    t3 = time()
    pprint(shortest_path)
    print("Time taken to load graph: ", t2 - t1)
    print("Time taken to process route: ", t3 - t2)


def test_medium_path(node_filename, edge_filename):

    t1 = time()
    g = test_graph_real_data(node_filename, edge_filename)
    t2 = time()
    shortest_path = g.dijkstra_path("66767575", "66774086", use_a_star=True)
    t3 = time()
    pprint(shortest_path)
    print("Time taken to load graph: ", t2 - t1)
    print("Time taken to process route: ", t3 - t2)

if __name__ == '__main__':

    # test_graph()
    # test_dijkstra()
    # test_a_star()
    # test_graph_real_data("../data/nodes.txt", "../data/edges.txt")
    # test_short_path_2("../data/nodes.txt", "../data/edges.txt")
    test_medium_short_path("../data/nodes.txt", "../data/edges.txt")
    # test_medium_path("../data/nodes.txt", "../data/edges.txt")

    # g.calculate_costs()
