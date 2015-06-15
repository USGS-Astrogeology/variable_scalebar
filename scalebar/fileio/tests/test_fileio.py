import unittest
from scalebar.examples import get_path
from .. import gdalio


class TestMercator(unittest.TestCase):
    def setUp(self):
        self.ds = gdalio.GeoDataSet(get_path('Mars_MGS_MOLA_ClrShade_MAP2_0.0N0.0_MERC.tif'))

    def test_geotransform(self):
        self.assertEqual(self.ds.geotransform, (0.0, 4630.0, 0.0, 3921610.0, 0.0, -4630.0))

    def test_getunittype(self):
        #Write a test that has a unittype or check why this is not 'm'
        self.assertEqual(self.ds.unittype, '')

    def test_getextent(self):
        self.assertEqual(self.ds.extent, [(0.0, -3921610.0), (10667520.0, 3921610.0)])

    def test_getNDV(self):
        self.assertEqual(self.ds.ndv, 0.0)

    def test_pixel_to_latlon(self):
        lat, lon = self.ds.pixel_to_latlon(0,0)
        self.assertAlmostEqual(lat, 55.33228905180849, 6)
        self.assertEqual(lon, 0.0)

    def test_extent(self):
        extent = self.ds.extent
        self.assertEqual(extent, [(0.0, -3921610.0), (10667520.0, 3921610.0)])

class TestLambert(unittest.TestCase):
    def setUp(self):
        self.ds = gdalio.GeoDataSet(get_path('Lunar_LRO_LOLA_Shade_MAP2_90.0N20.0_LAMB.tif'))

    def test_geotransform(self):
        self.assertEqual(self.ds.geotransform, (-464400.0, 3870.0, 0.0, -506970.0, 0.0, -3870.0))

    def test_getunittype(self):
        #Write a test that has a unittype or check why this is not 'm'
        self.assertEqual(self.ds.unittype, '')

    def test_getextent(self):
        self.assertEqual(self.ds.extent, [(-464400.0, -1571220.0), (460530.0, -506970.0)])

    def test_getNDV(self):
        self.assertEqual(self.ds.ndv, 0.0)

    def test_pixel_to_latlon(self):
        lat, lon = self.ds.pixel_to_latlon(0,0)
        self.assertAlmostEqual(lat, 69.90349154912009, 6)
        self.assertAlmostEqual(lon, -29.72166902463681, 6)

    def test_standard_parallels(self):
        sp = self.ds.standardparallels
        self.assertEqual(sp, [73.0, 42.0])

    def test_extent(self):
        extent = self.ds.extent
        self.assertEqual(extent, [(-464400.0, -1571220.0), (460530.0, -506970.0)])


class TestPolar(unittest.TestCase):
    def setUp(self):
        self.ds = gdalio.GeoDataSet(get_path('Mars_MGS_MOLA_ClrShade_MAP2_90.0N0.0_POLA.tif'))

    def test_geotransform(self):
        self.assertEqual(self.ds.geotransform, (-2129800.0, 4630.0, 0.0, 2129800.0, 0.0, -4630.0))

    def test_getunittype(self):
        #Write a test that has a unittype or check why this is not 'm'
        self.assertEqual(self.ds.unittype, '')

    def test_getextent(self):
        self.assertEqual(self.ds.extent, [(-2129800.0, -2129800.0), (2129800.0, 2129800.0)])

    def test_getNDV(self):
        self.assertEqual(self.ds.ndv, 0.0)

    def test_pixel_to_latlon(self):
        lat, lon = self.ds.pixel_to_latlon(0,0)
        self.assertAlmostEqual(lat, 42.25747350133827, 6)
        self.assertAlmostEqual(lon, -135.0, 6)

        #Check the pole
        mid = 1064900
        lat, lon = self.ds.pixel_to_latlon(mid, mid)
        self.assertAlmostEqual(lat, -89.78046521460993, 6)
        self.assertAlmostEqual(lon, 45.0, 6)

    def test_extent(self):
        extent = self.ds.extent
        self.assertEqual(extent, [(-2129800.0, -2129800.0), (2129800.0, 2129800.0)])
