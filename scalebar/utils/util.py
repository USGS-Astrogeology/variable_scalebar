def cm_to_inches(measurement, inverse=False):
    """
    Simple converion from centimeters to inches

    Parameters
    -----------

    measurement : float
                  distance to be converted
    inverse : boolean
              Default False.  If true, convert measurement to inches

    Returns
    -------
        : float
          The converted measurement
    """

    if inverse == False:
        return measurement / 2.54
    else:
        return measurement * 2.54

def integerround(x, base=5):
    """
    Round an input value to a given base, e.g. 2.25 to 5.

    Parameters
    ---------
    x : float
        Input value to be rounded

    base : int
           Base to round to

    Returns
    --------
        : int
          The rounded value
    """

    return int(base * round(float(x) / base))
