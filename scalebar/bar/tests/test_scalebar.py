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

    def test_mertcator_image(self):
        ds = get_path('Mars_MGS_MOLA_ClrShade_MAP2_0.0N0.0_MERC.tif')
        s = bar.ScaleBar.from_image(ds, outputname='merctest.svg')
        ref, test = getsvg(get_path('mars_merc.svg'), 'merctest.svg')
        os.remove('merctest.svg')
        self.assertEqual(ref, test)

    def test_polar_image(self):
        ds = get_path('Mars_MGS_MOLA_ClrShade_MAP2_90.0N0.0_POLA.tif')
        s = bar.ScaleBar.from_image(ds, outputname = 'pola_tests.svg')

    def test_lambert_image(self):
        ds = get_path('Lunar_LRO_LOLA_Shade_MAP2_90.0N20.0_LAMB.tif')
        s = bar.ScaleBar.from_image(ds, outputname='lambtest.svg')
        ref, test = getsvg(get_path('lunar_lamb.svg'), 'lambtest.svg')
        os.remove('lambtest.svg')
        self.assertEqual(ref, test)

    def test_mercator_projstring(self):
        pass

    def test_polar_projstring(self):
        pass

    def test_lambert_projstring(self):
        pass
