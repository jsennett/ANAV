from cost_utils import *


def test_cost(distance, highway, bicycle, incline, preferences):
    return cost()

def display_bike():
    array = [0, 0.5, 1]
    for pref in array:
        print("mutiplier", 1+bike_multiplier('Yes', pref))

def display_incline_multipliers():
    for incline in range(-45, 45):
        print(str(incline) + "%:", incline_multiplier(incline))

def display_road_multiplier():
    arr1 = ["cycleway", "tertiary", "residential", "service", "motorway", "primary", "secondary", "other"]
    arr2 = [0, .5 ,1]
    for way in arr1:
        for pref in arr2:
            muli = road_multiplier(way, pref, pref, pref, pref)
            print(way, pref, ": ", 1+muli)

def disp_cost():
    arr1 = ["cycleway", "tertiary", "residential", "service", "motorway", "primary", "secondary", "other"]
    arr2 = [0, .5 ,1]
    for incl in range(-10, 21):
        for way in arr1:
            for pref in arr2:
                c = cost(100, way, 'No', incl, (pref, pref, pref, pref, pref, pref))
                print(way, pref, incl, ": ", c)


if __name__ == '__main__':
    #display_bike()
    #display_incline_multipliers()
    #display_road_multiplier()
    disp_cost()

