import sys
import time

sys.path.append('../')
from optimizer.cost_utils import cost, incline_multiplier, bike_multiplier, road_multiplier


def test_cost(distance, highway, bicycle, incline, preferences):
    return cost()

def test_bike():
    assert(bike_multiplier('Yes', 1)==-0.8)
    assert(bike_multiplier('No', 1)==0)

def test_incline_multipliers():
    assert(incline_multiplier(10)==14.3)
    assert(incline_multiplier(-10)==0.6065306597126334)
    assert(incline_multiplier(-20)==0.6065306597126334)

def test_road_multiplier():
    assert(road_multiplier('motorway', 0, 1, 0, 0)==-0.5)
    assert(road_multiplier('cycleway', 0, 1, 0, 0)==0.0)
    assert(road_multiplier('not valid', 0, 1, 0, 0)==0.0)
    assert(road_multiplier('cycleway', 1, 0, 0, 0)==-0.8)

def test_cost():
    assert(cost(100, 'cycleway', 'Yes', 10, (1, 1, 1, 0, 0, 0.5))==15.3)
    assert(cost(100, 'cycleway', 'Yes', 0, (1, 1, 1, 0, 0, 0.5))==2.0)
    assert(cost(100, 'cycleway', 'Yes', 0, (1, 0, 1, 0, 0, 0.5))==101)
