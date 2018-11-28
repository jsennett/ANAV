import sys
from heapq import heappop, heappush
import json
import numpy as np

sys.path.append('../')
from data.Utility import preprocess_utils

inf = float('inf')


class Node:

    def __init__(self, name, coord, elev):
        self.name = name
        self.lat = coord[0]
        self.lon = coord[1]
        self.elev = elev

    def __repr__(self):
        return "\n Node %s: (%i, %i), %im" % (self.name, self.lat, self.lon, self.elev)


class Graph:

    def __init__(self):
        self.nodes = {}
        self.adjacencyList = {}


    def add_node(self, node):
        assert(node not in self.nodes)
        self.nodes[node.name] = (node.lat, node.lon, node.elev)
        self.adjacencyList[node.name] = []


    def add_edge(self, A_name, B_name):
        """
        Convert names 'A' to 'B' to points our functions can use, then
        add an edge from A to B with weight equal to the distance.
        """
        # Get nodes from node names
        A_fields = self.nodes.get(A_name)
        B_fields = self.nodes.get(B_name)

        # Convert to expected dictionaries
        A = {'lat':A_fields[0],
                  'lon':A_fields[1],
                  'elev':A_fields[2]}

        B = {'lat':B_fields[0],
                  'lon':B_fields[1],
                  'elev':B_fields[2]}

        # Calculate edge weights
        cost_to_B = preprocess_utils.cost(A, B)
        self.adjacencyList[A_name].append((B_name, cost_to_B))


    def dijkstra_path(self, A, B, DisPriority, ElePriority, BLPriority, HWPriority, use_a_star=True, debug=False):
        """ Return the shortest path from A to B using Dijkstra algo """

        if debug: print("nodes:", self.nodes)

        # Initial values
        cost = { V: inf for V in self.nodes.keys() }
        cost[A] = 0
        visited = set()

        # [(node, cost, path), ...]
        heap = [(A, cost[A], [])]

        # Dijkstra's
        while len(heap) > 0:

            (v, vcost, path) = heappop(heap)
            if v not in visited:
                visited.add(v)
                path = path + [v]

                # In A*, we return the shortest path once we find B, even if
                # we have not fully explored all of the remaining neighbors.
                if use_a_star and v == B:
                    return [(self.adjacencyList[nodeid][0:2]) for nodeid in path]

                if debug: print('v in adjlist:', self.adjacencyList.get(v))

                # A* uses heuristics (like Euclidean Distance) to prioritize
                # which nodes to explore. Sort neighbors by
                # Instead of iterating over elements of adjlist.get(v),
                # iterate over the sorted elements.
                # Sort based on minimum cost.

                # Instead of sorting by weight, sort by L2 distance.
                neighbors = [neighbor for neighbor in self.adjacencyList.get(v)]

                distances = [heuristic(self.nodes.get(B),
                                             self.nodes.get(neighbor[0]))
                             for neighbor in self.adjacencyList.get(v)]
                neighbor_distances = [(neighbor[0], neighbor[1], distance)
                                      for (neighbor, distance)
                                      in zip(neighbors, distances)]

                sorted_neighbors = sorted(neighbor_distances, key=lambda x:(x[int(use_a_star)]))
                if debug: print(sorted_neighbors)

                if use_a_star:
                    if debug: print("checking sorted neighbors:", sorted_neighbors)
                else:
                    if debug: print("checking unsorted neighbors:", sorted_neighbors)
                for (u, ucost, udist) in sorted_neighbors:
                    if u == B:
                        if debug: print("paths searched:", onsidered)
                        # TODO: make sure this is returning at the right time.
                        path = path + [B]
                        print("Shortest path found!")
                        # for p in path: print(p)
                        formatted_path = [(self.nodes[nodeid][0:2]) for nodeid in path]

                        return formatted_path
                    if u in visited: continue
                    prev_cost = cost.get(u)
                    next_cost = vcost + ucost
                    # Update cost, if taking this path is optimal
                    if next_cost < prev_cost:
                        cost[u] = next_cost
                        if debug: print((heap, (u, next_cost, path)))
                        heappush(heap, (u, next_cost, path))

        print("No path found.")
        return [A]



def closest_node(node, nodes):
    """ return the node closest to a node you give me """
    nodes = np.asarray(nodes)
    dist_2 = np.sum((nodes - node)**2, axis=1)
    return np.argmin(dist_2)


def heuristic(v, u):
    """ L2 distance of nodes (X, Y, )"""
    return (v[0] - u[0])**2 + (v[1]-u[1])**2



def optimize(lat1, lon1, lat2, lon2, DisPriority=1, ElePriority=1, BLPriority=1, HWPriority=1):

    node_filename = "data/nodes.txt"
    edge_filename = "data/edges.txt"

    # create a graph
    g = Graph()

    # read in data
    with open(node_filename, 'r') as f:
        nodes = json.load(f)

    with open(edge_filename, 'r') as f:
        edges = json.load(f)

    # add nodes and edges
    print("Loading in", len(nodes.keys()), "nodes.")
    for n in nodes.keys():
        id = n
        ele = nodes[n][0]
        lat, lon = nodes[n][1]
        g.add_node(Node(id, (lat, lon), ele))

    print("Loading in edges of ", len(edges.keys()), "nodes.")
    for node in edges.keys():
        for neighbor in edges[node]:
            g.add_edge(node, str(neighbor))

    # find closest node to start and end
    graph_nodes = g.nodes.values()
    graph_nodes = [node[0:2] for node in graph_nodes]

    A = closest_node((lat1, lon1), graph_nodes)
    B = closest_node((lat2, lon2), graph_nodes)

    # Get the point that has that closest value
    A_id = list(g.nodes.keys())[A]
    B_id = list(g.nodes.keys())[B]

    print("Closest A found!", A_id)
    print("Closest B found!", B_id)

    route = g.dijkstra_path(A_id, B_id, DisPriority, ElePriority, BLPriority, HWPriority)
    print("route found:")

    # format output:
    return route

    # g.dijkstra_path()
