import unittest
from scalebar.examples import get_path
from .. import gdalio


class TestMercator(unittest.TestCase):
    def setUp(self):
        self.ds = gdalio.GeoDataSet(get_path('Mars_MGS_MOLA_ClrShade_MAP2_0.0N0.0_MERC.tif'))

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
        lat, lon = self.ds.pixel_to_latlon(0,0)
        self.assertEqual(lat, 24)
        self.assertEqual(lon, 36)


class TestLambert(unittest.TestCase):
    def setUp(self):
        self.ds = gdalio.GeoDataSet(get_path('Lunar_LRO_LOLA_Shade_MAP2_90.0N20.0_LAMB.tif'))

    def test_geotransform(self):
        self.assertEqual(self.ds.geotransform, (-464400.0, 3870.0, 0.0, -506970.0, 0.0, -3870.0))

    def test_getscale(self):
        self.assertEqual(self.ds.scale, 1.0)

    def test_getunittype(self):
        #Write a test that has a unittype or check why this is not 'm'
        self.assertEqual(self.ds.unittype, '')

    def test_getextent(self):
        self.assertEqual(self.ds.extent, [(-464400.0, -1571220.0), (460530.0, -506970.0)])

    def test_getNDV(self):
        self.assertEqual(self.ds.ndv, 0.0)

    def test_pixel_to_latlon(self):
        lat, lon = self.ds.pixel_to_latlon(0,0)
        self.assertEqual(lat, 75.59448322442925)
        self.assertEqual(lon, 89.99999998419707)


class TestPolar(unittest.TestCase):
    def setUp(self):
        self.ds = gdalio.GeoDataSet(get_path('Mars_MGS_MOLA_ClrShade_MAP2_90.0N0.0_POLA.tif'))

    def test_geotransform(self):
        self.assertEqual(self.ds.geotransform, (-2129800.0, 4630.0, 0.0, 2129800.0, 0.0, -4630.0))

    def test_getscale(self):
        self.assertEqual(self.ds.scale, 1.0)

    def test_getunittype(self):
        #Write a test that has a unittype or check why this is not 'm'
        self.assertEqual(self.ds.unittype, '')

    def test_getextent(self):
        self.assertEqual(self.ds.extent, [(-2129800.0, -2129800.0), (2129800.0, 2129800.0)])

    def test_getNDV(self):
        self.assertEqual(self.ds.ndv, 0.0)

    def test_pixel_to_latlon(self):
        lat, lon = self.ds.pixel_to_latlon(0,0)
        self.assertEqual(lat, 24)
        self.assertEqual(lon, 36)




