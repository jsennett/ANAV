import sys
from heapq import heappop, heappush
import json
import numpy as np

sys.path.append('../')
import cost
import amherst
from decimal import Decimal

inf = float('inf')


class Node:

    def __init__(self, id, coord):
        self.id = id
        self.lat = coord[0]
        self.lon = coord[1]

    def __repr__(self):
        return "\n Node %s: (%i, %i)" % (self.id, self.lat, self.lon)


class Graph:

    def __init__(self):
        self.nodes = {}
        self.adjacencyList = {}


    def add_node(self, node):
        #this node should not be in nodes
        self.nodes[node.id] = (node.lat, node.lon)
        self.adjacencyList[node.id] = []


    def add_edge(self, distance, incline, ElePriority, BLPriority, HWPriority):
        # Calculate edge weights
        cost_to_B = cost.cost(distance, incline, ElePriority, BLPriority, HWPriority)
        # ^^^ This is the method that needs fixing. It currently points to a preprocessing utility. It needs to be calculated dynamically.
        self.adjacencyList[A_id].append((B_id, cost_to_B))


    def dijkstra_path(self, A, B, use_a_star=True, debug=False):
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
                                      # neighbor_distances is an array of tuples containing the node name of a neighbor, the cost to that neighbor and euclidean distance between B and the neighbor
                                      # This means that element 2 is the cost to that neighbor. Stored in the adjacency list above.

                sorted_neighbors = sorted(neighbor_distances, key=lambda x:(x[int(use_a_star)]))
                # sorted neighbors is just the sorted list of neighbor_distances
                if debug: print(sorted_neighbors)

                if use_a_star:
                    if debug: print("checking sorted neighbors:", sorted_neighbors)
                else:
                    if debug: print("checking unsorted neighbors:", sorted_neighbors)
                for (u, ucost, udist) in sorted_neighbors:
                	# ucost comes from element 2 of each member of sorted neighbors
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
                    # based on this, ucost is the variable which we need to determine how it should be calculated
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


### need work
def optimize(area, lat1, lon1, lat2, lon2, ElePriority=0.5, BLPriority=0, HWPriority=0.5):

    # create a graph
    g = Graph()

    # initial the graph
    # area read in from DB
    # assume amherst.py is the data format

    #use amherst.amherst as mock data
    area = amherst.amherst

    # add nodes and edges
    # lat and lon are Decimal objs
    for way in area:
        start_node_id = way[0]
        if(g.nodes.get(start_node_id)==None):
            start_node_lat = way[1]
            start_node_lon = way[2]
            g.add_node(Node(start_node_id, (start_node_lat, start_node_lon))) #add start node to graph
        end_node_id = way[3]
        if(g.nodes.get(end_node_id)==None):
            end_node_lat = way[4]
            end_node_lon = way[5]
            g.add_node(Node(end_node_id, (end_node_lat, end_node_lon))) #add end node to graph, for closest_node() method
        distance = way[6]
        incline = way[10]
        g.add_edge(start_node_id, end_node_id, distance, incline, ElePriority, BLPriority, HWPriority)

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

    route = g.dijkstra_path(A_id, B_id)
    print("route found:")

    # format output:
    return route

    # g.dijkstra_path()
