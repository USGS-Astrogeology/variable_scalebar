import unittest
import os
from .. import bar
from scalebar.examples import get_path

def getsvg(im1, im2):
    reference_merc = get_path(im1)
    with open(reference_merc, 'r') as f:
        ref = f.readlines()

    with open(im2, 'r') as f:
        test = f.readlines()

    return ref, test

class TestScaleBar(unittest.TestCase):
    def setUp(self):
        pass

    def test_mercator_image(self):
        ds = get_path('Mars_MGS_MOLA_ClrShade_MAP2_0.0N0.0_MERC.tif')
        s = bar.ScaleBar.from_image(ds, outputname='merctest.svg')
        ref, test = getsvg(get_path('mars_merc.svg'), 'merctest.svg')
        self.assertEqual(ref, test)

    def test_polar_image(self):
        ds = get_path('Mars_MGS_MOLA_ClrShade_MAP2_90.0N0.0_POLA.tif')
        s = bar.ScaleBar.from_image(ds, outputname = 'pola_test.svg')
        ref, test = getsvg(get_path('mars_polar.svg'), 'pola_test.svg')
        self.assertEqual(ref, test)

    def test_lambert_image(self):
        ds = get_path('Lunar_LRO_LOLA_Shade_MAP2_90.0N20.0_LAMB.tif')
        s = bar.ScaleBar.from_image(ds, outputname='lambtest.svg')
        ref, test = getsvg(get_path('lunar_lamb.svg'), 'lambtest.svg')
        self.assertEqual(ref, test)

    def test_mercator_proj4string(self):
        pass

    def test_polar_proj4string(self):
        pass

    def test_lambert_proj4string(self):
        pass

    def test_mercator_wktstring(self):
        wkt = 'PROJCS["Moon2000_Mercator180",GEOGCS["GCS_Moon_2000",DATUM["D_Moon_2000",SPHEROID["Moon_2000_IAU_IAG",1737400.0,0.0]],PRIMEM["Reference_Meridian",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Mercator"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",180.0],PARAMETER["Standard_Parallel_1",0.0],UNIT["Meter",1.0]]'
        s = bar.ScaleBar.from_projstring(wkt, ((0, 0), (90, 180)), outputname='merctest.svg')
        ref, test = getsvg(get_path('mars_merc.svg'), 'merctest.svg')
        self.assertEqual(ref, test)

    def test_polar_wktstring(self):
        pass

    def test_lambert_wktstring(self):
        pass
