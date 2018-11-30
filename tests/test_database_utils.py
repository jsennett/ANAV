import pytest
from data.database_utils import nodes_within_radius, nearest_node


def test_nearest_node():
    """ Placeholder test """
    nn = nearest_node(credentials, lat=42.359055, lon=-71.093500, meters=100)
    assert(nn != None)
