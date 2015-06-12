from pyproj import Proj

def create_projection_transformer(proj4_string):
    """
    Create a proj4 projection instance.
    """
    return Proj(proj4_string)
