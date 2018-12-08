from cost_utils import *


def test_cost(A, B):
    return cost(A, B)

def test_all(A, B):
    print("cost", cost(A, B))
    print("incline_multiplier", incline_multiplier(incline(A, B)))

def display_incline_multipliers():
    for incline in range(-45, 45):
        print(str(incline) + "%:", incline_multiplier(incline))


if __name__ == '__main__':

    A = {'lat': 42.3489178,
         'lon': -72.5686607,
         'elev': 150}

    B = {'lat':42.3489313,
         'lon': -72.5679691,
         'elev': 175}

    C = {'lat':42.3489313,
         'lon': -72.5679691,
         'elev': 152}

    D = {'lat':42.3489313,
         'lon': -72.5679691,
         'elev': 150}
"""
    print("*" * 80)
    print("Two points on a very steep uphill: ")
    test_all(A, B)


    print("*" * 80)
    print("Two points on a very slight uphill: ")
    test_all(A, C)

    print("*" * 80)
    print("Two points on a very slight downhill: ")
    test_all(C, A)

    print("*" * 80)
    print("Two points on a flat: ")
    test_all(A, D)

    print("*" * 80)

    display_incline_multipliers()
"""
