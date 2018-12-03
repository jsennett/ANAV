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

def cost(A, B, IncPriority, BLPriority, HWPriority, bikelane=false, road_type=""):
    """
    Calculate a 'cost' for traveling from A to B, where
    cost is a dynamic function dependant on the priority
    preferences defined by the user.
    """
    cost = dist_3d(A, B) * ((IncPriority * incline_multiplier(incline(A, B)) + (BLPriority * BL_multiplier(bikelane)) + (HWPriority * HW_multiplier(road_type)))) # TODO: find a way to work in the incline multiplier
    # TODO: add in values based on whether bike lanes are present and what type of road it is.
    # if (not bikelane)
    # cost += BLPriority * Some Hard Coded Value
    # or something like that
    return cost

def incline_multiplier(incline, hard_cap=20, neg_cap=-10,
                       damp=.01, exp_damp=.05):
    """
    Calculate a cost multiplier for a given incline, representing relative effort.

    The multiplier is exponential for positive numbers, with a hard cap.
    This represents all downhills being "rests".
    The default parameters give pretty good approximations of "effort".
    """
    # TODO: Conscider other ways to calculate this such that it works efficiently alongside the priority preferences.
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

def BL_multiplier(bikelane):
    if not bikelane:
        return 93
    return 0

def HW_multiplier(road_type):
    if road_type in ["motorway", "service"]:
        return 93
    if road_type in ["primary", "secondary", "tertiary"]:
        return 62
    if road_type in ["tertiary", "other"]:
        return 31
    if road_type in ["residential", "cycleway"]:
        return 0
    return 31