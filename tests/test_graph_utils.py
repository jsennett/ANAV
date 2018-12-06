import sys
sys.path.append('../')
from optimizer.graph_utils import optimize, midpoint, search_radius, dist_2d, valid_point

def test_optimize_good_values():

    # A, B are .1 degree (~ 1km) away in each direction
    A = (42.38, -72.52)
    B = (42.48, -72.62)

    # Random, valid preferences
    preferences = (10, 20, 30, 40, 50, 60)

    result = optimize(A, B, preferences, debug=True)
    assert(result != []) # Assert that we did not fail to find a path


def test_optimize_bad_values():

    valid_preferences = (0.0, 50, 0, 100, 25, 100.0)
    invalid_preferences = (-10, 20, 30, 40, 50, 120)

    valid_A, valid_B = (42.38, -72.52), (42.48, -72.62)
    invalid_A, invalid_B = (20, 30), (80, 80) # out of range for MA

    # Expected return is an empty list instead
    # of a list of nodes in an optimal route
    expected = []

    assert(optimize(valid_A, valid_B, invalid_preferences) == expected)
    assert(optimize(invalid_A, valid_B, valid_preferences) == expected)
    assert(optimize(valid_A, invalid_B, valid_preferences) == expected)


def test_other_utils():
    # Sample point
    A, B = (42.00, -72.52), (43.00, -72.52) # A is 1 degree north of B

    # Calculate utils
    m = midpoint(A, B)
    dist = dist_2d(A, B)
    r = search_radius(A, B)

    assert(abs(m[0] - 42.5) < 0.0001 and abs(m[1] - -72.52) < 0.0001)
    assert(dist > 111000 and dist < 111500)
    assert(r > 60000 and r < 62000)


def test_valid_point():
    assert(valid_point(30, 50) is False)
    assert(valid_point(42, -71) is True)
