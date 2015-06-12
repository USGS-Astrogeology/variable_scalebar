import unittest

from .. import gdalio

class TestPixelToLatLon(unittest.TestCase):

    def setUp(self):
        self.ds = gdalio.GeoDataSet('../../../examples/mercator/Mars_MGS_MOLA_ClrShade_MAP2_0.0N0.0_MERC.tif')

    def test_geotransform(self):
        self.assertEqual(self.ds.geotransform, (0.0, 4630.0, 0.0, 3921610.0, 0.0, -4630.0))


    def test_getscale(self):
        self.assertEqual(self.ds.scale, 1.0)

    def test_getunittype(self):
        #Write a test that has a unittype or check why this is not 'm'
        self.assertEqual(self.ds.unittype, '')

    def test_getextent(self):
        self.assertEqual(self.ds.extent, [(0.0, -3921610.0), (10667520.0, 3921610.0)])

    def test_getNDV(self):
        self.assertEqual(self.ds.ndv, 0.0)

    def test_pixel_to_latlon(self):
        self.ds.pixel_to_latlon(0,0)
