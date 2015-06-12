import unittest

from .. import proj4_transformer as pt
from scalebar.metadata import extract_metadata as em

class TestLatLon_To_LineSample(unittest.TestCase):

    def setUp(self):
        import osr
        from pyproj import Proj
        self.wktsrs = 'PROJCS["Moon2000_Mercator180",GEOGCS["GCS_Moon_2000",DATUM["D_Moon_2000",SPHEROID["Moon_2000_IAU_IAG",1737400.0,0.0]],PRIMEM["Reference_Meridian",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Mercator"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",180.0],PARAMETER["Standard_Parallel_1",0.0],UNIT["Meter",1.0]]'
        self.srs = em.extract_projstring(self.wktsrs)

        print self.srs.ExportToProj4()
        self.transformer = pt.create_projection_transformer(proj4_projection)

    def test_latlon_to_linesample(self):
        lat = 0
        lon = 0
        y, x = self.transformer(lon, lat)
        assertEqual(y, 24)



