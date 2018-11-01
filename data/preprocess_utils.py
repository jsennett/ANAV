from geographiclib.geodesic import Geodesic
import math



def dist_2d(A, B):
    """ Calculate 2d distance (meters) between A and B """
    result = Geodesic.WGS84.Inverse(A['lat'], A['lon'], B['lat'], B['lon'])
    return result['s12']


def elev_gain(A, B):
    """ Calculate elevation gain (meters) from A to B """
    return B['elev'] - A['elev']


def dist_3d(A, B):
    """ Calculate 3d distance (meters) between A and B """
    dist_3d = (dist_2d(A, B)**2 + elev_gain(A, B)**2) ** (.5)
    return dist_3d


def incline(A, B):
    """ Calculate incline (meters) between A and B """
    return math.degrees(math.atan(elev_gain(A, B) / dist_2d(A, B)))

def cost(A, B):
    """
    Calculate a 'cost' for traveling from A to B, where
    cost = (distance * incline_multiplier)
    """
    return dist_3d(A, B) * incline_multiplier(incline(A, B))

def incline_multiplier(incline, hard_cap=20, neg_cap=-10,
                       damp=.01, exp_damp=.05):
    """
    Calculate a cost multiplier for a given incline, representing relative effort.

    The multiplier is exponential for positive numbers, with a hard cap.
    This represents all downhills being "rests".
    The default parameters give pretty good approximations of "effort".
    """
    # Apply caps
    if incline > hard_cap:
        return incline_multiplier(hard_cap)
    elif incline < neg_cap:
        return incline_multiplier(neg_cap)

    # Calculate differently for uphills and downhills
    if incline < 0:
        # Downhill effort:
        return math.exp(incline * exp_damp)
    else:
        return damp * (incline + 1)**3 + 1 - damp
