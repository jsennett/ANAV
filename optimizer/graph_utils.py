import sys
from heapq import heappop, heappush
import json
import numpy as np
from geographiclib.geodesic import Geodesic

sys.path.append("..")
from data.database_utils import nearest_node, edges_within_radius
from data.config import credentials

# infinity value, used in Dijkstra
inf = float('inf')

# Maximum distance allowed between input start and end points (meters)
MAX_DISTANCE = 50000


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


def optimize(A, B, preferences, debug=False):
    """
    Main driver of the graph optimization.

    @input
    A: tuple of floats - (lat, lon)
    B: tuple of floats - (lat, lon)
    preferences: tuple of floats -
                (flatness_val, bicycle_val, distance_val,
                 motorway_val, highway_val, residential_val)

    @return
    route - an ordered list of nodes [(lat, lon), (lat, lon)] from A to B
    """
    # Unpack values
    A_lat, A_lon = A
    B_lat, B_lon = B
    (flatness_val, bicycle_val, distance_val,
    motorway_val, highway_val, residential_val) = preferences

    # Validate input parameters
    if not valid_point(A_lat, A_lon):
        print("Invalid start point", A)
        return []
    if not valid_point(B_lat, B_lon):
        print("Invalid end point", B)
        return []
    if any([preference < 0 or preference > 100 for preference in preferences]):
        print("Invalid preferences", preferences)
        return []

    AB_dist = dist_2d(A, B)
    if AB_dist > MAX_DISTANCE:
        print("Start and end points are further than maximum allowed distance",
              AB_dist, "meters", MAX_DISTANCE, "allowed.")
        return []

    # Find nearest nodes in our database to A and B
    s = nearest_node(credentials, lat=A_lat, lon=A_lon)
    if s is None:
        print("No node found near", A)
        return []
    else:
        s_id, s_lat, s_lon = s

    t = nearest_node(credentials, lat=B_lat, lon=B_lon)
    if t is None:
        print("No node found near", B)
        return []
    else:
        t_id, t_lat, t_lon = t

    # Calculate midpoint
    m_lat, m_lon = midpoint((s_lat, s_lon), (t_lat, t_lon))

    # Calculate search radius
    r = search_radius((s_lat, s_lon), (t_lat, t_lon))

    # Get data from search radius
    edges_to_search = edges_within_radius(credentials, lat=m_lat, lon=m_lon, radius=r)

    # Print debug messages, if specified.
    if debug:
        print("Graph will be created with ", len(edges_to_search), "edges")
        print("radius:", r)
        print("midpoint:", m_lat, m_lon)
        print("s:", s)
        print("t:", t)
        print("AB_dist:", AB_dist)
        print("st_dist:", dist_2d((s_lat, s_lon), (t_lat, t_lon)))
        print("sample edges:", edges_to_search[:10])
        print("preferences:", preferences)

    # TODO: build the graph g, call g.dijkstra_path, and return the shortest path
    # g = Graph()
    # shortest_path = g.dijkstra_path(s, t))
    # return shortest_path


def midpoint(s, t):
    """
    Calculate the midpoint between points s and t.
    @input
    s: tuple of floats (lat, lon)
    t: tuple of floats (lat, lon)

    @return
    m: tuple of floats (lat, lon)
    """
    l = Geodesic.WGS84.InverseLine(*s, *t)
    # Compute the midpoint
    m = l.Position(0.5 * l.s13)
    return (m['lat2'], m['lon2'])


def search_radius(s, t):
    """
    Calculate the search radius between points s and t.
    The search radius should be the radius of a circle that
    includes points (s, t) plus some buffer area.

    @input
    s: tuple of floats - (lat, lon)
    t: tuple of floats - (lat, lon)

    @return
    r: float - radius, in meters
    """
    st_dist = dist_2d(s, t)

    # For a small search radius, we can afford a large buffer.
    # This will ensure we get edges that may be part of s-t path
    #
    # For a large search radius, we can't afford a large buffer;
    # the graph will have too many edges which is expensive to
    # retrieve and slow to find optimal route.
    if st_dist < 5000:
        buffer = .5
    elif 5000 <= st_dist < 10000:
        buffer = .25
    else:
        buffer = .1

    return (1 + buffer) * st_dist * .5


def dist_2d(A, B):
    """
    Calculate 2d distance, in meters, between A and B
    @input
    s: tuple of floats (lat, lon)
    t: tuple of floats (lat, lon)

    @return
    m: tuple of floats (lat, lon)
    """

    result = Geodesic.WGS84.Inverse(*A, *B)
    return result['s12']


def valid_point(lat, lon):
    if lon < -73.6 or lon > -69.8 or lat < 41.0 or lat > 43.0:
        return False
    else:
        return True


def heuristic(v, u):
    """ L2 distance of nodes (X, Y, )"""
    return (v[0] - u[0])**2 + (v[1]-u[1])**2
