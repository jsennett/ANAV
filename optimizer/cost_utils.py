import math
from decimal import Decimal

def cost(distance, highway, bicycle, incline, preferences):
    """
    Calculate a 'cost' for traveling from A to B, where
    cost is a dynamic function dependant on the priority
    preferences defined by the user.
    """

    #unpack preferences
    (flatness_pref, bicycle_pref, distance_pref,
            motorway_pref, highway_pref, residential_pref) = preferences
    multiplier = 1 + bike_multiplier(bicycle, bicycle_pref) + road_multiplier(highway, bicycle_pref, motorway_pref, highway_pref, residential_pref)
    if multiplier <= 0:
        multiplier = 0.01
    incl = incline_multiplier(float(incline))*flatness_pref
    cost = float(distance) * multiplier + incl
    if cost <= 0:
        cost = 0.01
    return cost

def incline_multiplier(incline, hard_cap=20, neg_cap=-10,
                       damp=.01, exp_damp=.05):
    """
    Calculate a cost multiplier for a given incline, representing relative effort.

    The multiplier is exponential for positive numbers, with a hard cap.
    This represents all downhills being "rests".
    The default parameters give pretty good approximations of "effort".
    """
    # default should be 0
    # Apply caps
    if incline > hard_cap:
        return incline_multiplier(hard_cap, hard_cap=hard_cap)
    elif incline < neg_cap:
        return incline_multiplier(neg_cap, neg_cap=neg_cap)

    # Calculate differently for uphills and downhills
    if incline < 0:
        # Downhill effort:
        return math.exp(incline * exp_damp)
    else:
        return damp * (incline + 1)**3 + 1 - damp

def bike_multiplier(bikelane, bicycle_pref):
    #default = 0
    result = bicycle_pref * 0.8
    if bikelane=='Yes':
        return -result
    return 0.0

def road_multiplier(highway, bicycle_pref, motorway_pref, highway_pref, residential_pref):
    """
    default 0
    """
    if highway == 'motorway':
        result = -motorway_pref*0.5
    elif highway == 'primary':
        result = -highway_pref*0.5
    elif highway == 'residential' or highway == 'service':
        result = -residential_pref*0.5
    elif highway == 'cycleway':
        result = -bicycle_pref * 0.8
    else:
        result = 0
    return result
