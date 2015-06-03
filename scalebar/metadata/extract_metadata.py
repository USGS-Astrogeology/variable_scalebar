from future.utils import lrange
import gdal
import osr

import_options = ['ImportFromWkt', 'ImportFromProj4',
                  'ImportFromEPSG', 'ImportFromUSGS',
                  'ImportFromXML']

def extract_projstring(proj_string):
    """
    Import an OSR supported projection string into
    a spatial reference object

    Parameters
    ----------
    proj_string : string
                  Projection String in some OSR supported format

    Returns
    -------
    srs : object
          OSR spatial reference object

    """
    srs = osr.SpatialReference()
    for import_option in import_options:
        try:
            func = getattr(srs, import_option)
            func(proj_string)
            break
        except:
            pass
    return srs

def get_standard_parallels(srs):
    """
    Get all standard parallels for a given map projection

    Parameters
    ----------
    srs : object
          OSR spatial reference system

    Returns
    -------
        : list
          of standard parallels
    """
    
    parallels = [None, None]
    print srs.GetProjParm('Standard_Parallel_1', 24)
    for i in lrange(2):
        parallels[i] = srs.GetProjParm('Standard_Parallel_{}'.format(i), 0.0)    
    return parallels

def get_central_meridian(srs):
    """
    Get the central meridian of the projection
    
     Parameters
    ----------
    srs : object
          OSR spatial reference system

    Returns
    -------
        : float
          central meridian
    """

    return srs.GetProjParm('central_meridian', 0.0) 


def get_spheroid(srs):
    """
    Get the semi-major, semi-minor, and inverse flattening 
    of the body from the srs
     
    Parameters
    ----------
    srs : object
          OSR spatial reference system

    Returns
    -------
        : tuple
          semi-major, semi-minor, invflattening
    """
    
    semimajor = srs.GetSemiMajor()
    semiminor = srs.GetSemiMinor()
    invflattening = srs.GetInvFlattening()
    return semimajor, semiminor, invflattening
 
def get_projection_name(srs):
    """
    Eactract the projection name from a
    spatial reference system

    Parameters
    ----------
    srs : object
          OSR spatial reference system

    Returns
    -------
        : string
          The projection name
    """
    proj_name = srs.GetAttrValue("PROJECTION", 0)
    return proj_name

def get_false_easting(srs):
    """
    Extract the false easting parameter from a
    spatial reference system

    Parameters
    ----------
    srs : object
          OSR spatial reference system

    Returns
    -------
        : float
          The false easting value
    """

    return srs.GetProjParm('False_Easting', 0)

def get_false_northing(srs):
    """
    Extract the false northing parameter from a
    spatial reference system

    Parameters
    ----------
    srs : object
          OSR spatial reference system

    Returns
    -------
        : float
          The false northing value
    """

    return srs.GetProjParm('False_Northing', 0)