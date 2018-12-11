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
    preferences = (0, 0, 0, 0, 0, 0)

    A = (42.3600949, -71.0963487)
    B = (42.3632679, -71.1061316)
    Art_museum = (42.3355989, -71.1013107)
    Exhibition_Center = (42.3471625,-71.0881894)
    Airport = (42.3673204,-71.024456) #no path found
    South_bay_center = (42.3313662,-71.0783914)
    JFK_lib_mus = (42.3088871,-71.0889916)
    havard = (42.3698432,-71.0983546)
    TF_University = (42.3756961,-71.1122189)
    points = [TF_University]
    for dest in points:
        start = time.time()
        optimize(A, dest, preferences)
        end = time.time()
        print("Optimization complete in %f sec" % (end - start))


if __name__ == '__main__':

    # time_radius_queries()
    # time_nearest_node_queries()
    time_optimize()
    # time_nearest_node_not_found()
    # time_random_nearest_nodes()
