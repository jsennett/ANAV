import sys

sys.path.append('../')
from data.database_utils import edges_within_radius, nearest_node
from data.config import credentials
from optimizer.graph_utils import optimize, dist_2d

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
        for degrees in [.01, .05, .1, .15, .2, .3, .4, .5]:
            radius = degrees * 111000
            start = time.time()
            nodes = edges_within_radius(credentials, radius=radius, lat=lat, lon=lon, limit=5000000)
            end = time.time()
            print("%d nodes found in %f sec (radius %fm)" %
                  (len(nodes), end - start, radius ))


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

    # Random, valid preferences
    preferences = (10, 20, 30, 40, 50, 60)

    A = (42.38, -72.52)
    for meter_shift in [500, 1000, 2000, 5000, 10000, 25000, 50000]:

        # Set point B to various distances away from A
        degree_shift = meter_shift / 111000.0
        B = (A[0] + degree_shift, A[1] + degree_shift)
        AB_dist = dist_2d(A, B)

        start = time.time()
        optimize(A, B, preferences)
        end = time.time()
        print("Optimization for distance %f complete in %f sec" % (AB_dist, end - start))


if __name__ == '__main__':

    # time_radius_queries()
    # time_nearest_node_queries()
    # time_optimize()
    time_nearest_node_not_found()
