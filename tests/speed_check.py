import sys

sys.path.append('../')
from data.database_utils import edges_within_radius, nearest_node
from data.config import credentials
from optimizer.graph_utils import optimize, midpoint, search_radius

import time

def time_radius_queries():

    amherst = ('amherst', 42.375582, -72.519629)
    boston = ('boston', 42.356417, -71.067728)
    shutesbury = ('shutesbury', 42.454855, -72.410792)

    # Test different towns (sparse, medium, dense)
    for point in [shutesbury, amherst, boston]:

        # Unpack values
        name, lat, lon = point
        print("*****" , name , "*****")

        # Test different radii
        for meters in [1000 * x for x in range(50)]:
            start = time.time()
            edges = edges_within_radius(credentials, radius=meters, lat=lat, lon=lon, limit=5000000)
            end = time.time()
            print("%d, %f, %d" % (len(edges), end - start, meters))


def time_nearest_node_queries():

    amherst = ('amherst', 42.375582, -72.519629)
    boston = ('boston', 42.356417, -71.067728)
    shutesbury = ('shutesbury', 42.454855, -72.410792)

    # Test different towns (sparse, medium, dense)
    for point in [shutesbury, amherst, boston]:

        # Unpack values
        name, lat, lon = point

        start = time.time()
        nodes = nearest_node(credentials, lat=lat, lon=lon)
        end = time.time()
        print("%s: nearest node found in %f sec" % (name, end - start))

def time_random_nearest_nodes():

    x_dim = 100
    y_dim = 50
    count = 0

    for i in range(x_dim):
        for j in range(y_dim):

            lon = -73.2 + (-71.5 - -73.2) * 1.0 * i /x_dim
            lat = 42.1 + (42.6 - 42.1) * 1.0 * j /y_dim

            count += 1
            start = time.time()
            nodes = nearest_node(credentials, lat=lat, lon=lon)
            end = time.time()
            print("%i, %f, %f, %f" % (count, lat, lon, end - start))


def time_nearest_node_not_found():

    nodes_not_found = [(42.39801801801802, -72.50198198198198),
                       (42.425045045045046, -72.47495495495495),
                       (42.605225225225226, -72.29477477477477)]

    for point in nodes_not_found:

        lat, lon = point

        start = time.time()
        nodes = nearest_node(credentials, lat=lat, lon=lon)
        end = time.time()
        print("searching for", point, "took %f sec" % (end - start))


def time_optimize():

    # Defualt, valid preferences
    preferences = (50, 50, 50, 50, 50, 50)

    A = (42.3416991, -71.1004189)
    for meter_shift in [500, 1000, 2000, 5000, 10000, 25000, 50000]:

        # Set point B to various distances away from A
        degree_shift = meter_shift / 111000.0
        B = (A[0] + degree_shift, A[1] - degree_shift)
        dist = search_radius(A, B)
        m = midpoint(A, B)
        edges = edges_within_radius(credentials, radius=dist, lat=m[0], lon=m[1], limit=5000000)

        start = time.time()
        optimize(A, B, preferences)
        end = time.time()
        print("Optimization for distance %f & edges %i complete in %f sec" % (dist, len(edges), end - start))


if __name__ == '__main__':

    # time_radius_queries()
    # time_nearest_node_queries()
    time_optimize()
    # time_nearest_node_not_found()
    # time_random_nearest_nodes()
