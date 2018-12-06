import pytest
import sys
import time

sys.path.append('../')
from data.database_utils import edges_within_radius, nearest_node
from data.config import credentials


def test_nearest_node():
    """ Test if a nearest node can be found """
    sample_lat, sample_lon = 42.299944, -72.588062
    nn = nearest_node(credentials, lat=sample_lat, lon=sample_lon, meters=100)

    # make sure we get the right return type
    assert(type(nn) == tuple)

    # make sure each node is a row with (id, lat, lon)
    assert(len(nn) == 3)

    # make sure we are within .1 degree of latitude and longitude
    assert(abs(float(nn[1]) - sample_lat) < .1 and abs(float(nn[2]) - sample_lon) < .1)


def test_nearest_node_not_found():

    # These are three points with no nodes in a 100 meter vicinity.
    vicinity = 100
    nodes_not_found = [(42.39801801801802, -72.50198198198198),
                       (42.425045045045046, -72.47495495495495),
                       (42.605225225225226, -72.29477477477477)]

    for point in nodes_not_found:
        lat, lon = point
        node = nearest_node(credentials, lat=lat, lon=lon, meters=vicinity)
        assert(node is None)

def test_nodes_in_radius():
    """ Test a standard query for nodes in a radius """
    sample_lat, sample_lon = 42.299944, -72.588062
    nodes = edges_within_radius(credentials, lat=sample_lat, lon=sample_lon, radius=5000)

    # make sure we get the right return type
    assert(type(nodes) == list)

    # make sure we get a reasonable amount of nodes
    assert(len(nodes) > 1000)

    # make sure we get the right row return type
    assert(type(nodes[0]) == tuple)

    # make sure each node is a row from edges
    assert(len(nodes[0]) == 10)
