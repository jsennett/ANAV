import sys

sys.path.append('../')
from data.database_utils import nodes_within_radius, nearest_node
from data.config import credentials

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
        for radius in [.01, .05, .1, .15, .2, .3, .4, .5]:
            start = time.time()
            nodes = nodes_within_radius(credentials, radius=radius, lat=lat, lon=lon, limit=5000000)
            end = time.time()
            print("%d nodes found in %f sec (radius %fm)" %
                  (len(nodes), end - start, radius * 111195))


def time_nearest_node_queries():

    amherst = ('amherst', 42.375582, -72.519629)
    boston = ('boston', 42.356417, -71.067728)
    shutesbury = ('shutesbury', 42.454855, -72.410792)

    # Test different towns (sparse, medium, dense)
    for point in [shutesbury, amherst, boston]:

        # Unpack values
        name, lat, lon = point

        # Test different radii
        start = time.time()
        nodes = nearest_node(credentials, lat=lat, lon=lon)
        end = time.time()
        print("%s: nearest node found in %f sec" % (name, end - start))


if __name__ == '__main__':

    time_radius_queries()
    time_nearest_node_queries()
