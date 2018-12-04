import math
from decimal import Decimal

def cost(distance, incline, IncPriority, BLPriority, HWPriority):
    """
    Calculate a 'cost' for traveling from A to B, where
    cost is a dynamic function dependant on the priority
    preferences defined by the user.
    """

    #need modified
    cost = distance * (Decimal(1) + IncPriority * incline_multiplier(incline) + BLPriority * BL_multiplier(True) + HWPriority * HW_multiplier(0))
    # TODO: add in values based on whether bike lanes are present and what type of road it is.
    # if (not bikelane)
    # cost += BLPriority * Some Hard Coded Value
    # or something like that
    return cost

def incline_multiplier(incline, hard_cap=20, neg_cap=-10,
                       damp=Decimal(.01), exp_damp=Decimal(.05)):
    """
    Calculate a cost multiplier for a given incline, representing relative effort.

    The multiplier is exponential for positive numbers, with a hard cap.
    This represents all downhills being "rests".
    The default parameters give pretty good approximations of "effort".
    """
    # TODO: Conscider other ways to calculate this such that it works efficiently alongside the priority preferences.
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

def BL_multiplier(bikelane):
    if not bikelane:
        return 93
    return 0

def HW_multiplier(road_type):
    """
    if road_type is in #some list of bad road types:
        return 93
    """
    return 0
