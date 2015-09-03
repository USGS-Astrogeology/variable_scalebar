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
        self.path = os.path.dirname(os.path.realpath(__file__))

    def test_mercator_image(self):
        ds = get_path('Mars_MGS_MOLA_ClrShade_MAP2_0.0N0.0_MERC.tif')
        testname = os.path.join(self.path, 'merctest.svg')
        s = bar.ScaleBar.from_image(ds, outputname=testname)
        ref, test = getsvg(get_path('mars_merc.svg'), testname)
        self.assertEqual(ref, test)
        os.remove(testname)

    def test_polar_image(self):
        ds = get_path('Mars_MGS_MOLA_ClrShade_MAP2_90.0N0.0_POLA.tif')
        testname = os.path.join(self.path, 'polartest.svg')
        s = bar.ScaleBar.from_image(ds, outputname = testname)
        ref, test = getsvg(get_path('mars_polar.svg'), testname)
        self.assertEqual(ref, test)
        os.remove(testname)

    def test_lambert_image(self):
        ds = get_path('Lunar_LRO_LOLA_Shade_MAP2_90.0N20.0_LAMB.tif')
        testname = os.path.join(self.path, 'lambtest.svg')
        s = bar.ScaleBar.from_image(ds, outputname=testname)
        ref, test = getsvg(get_path('lunar_lamb.svg'), testname)
        self.assertEqual(ref, test)
        os.remove(testname)

    def test_mercator_proj4string(self):
        pass

    def test_polar_proj4string(self):
        pass

    def test_lambert_proj4string(self):
        pass

    def test_mercator_wktstring(self):
        wkt = """PROJCS["Mercator_MARS",
                 GEOGCS["GCS_MARS",
                   DATUM["MARS",
                   SPHEROID["MARS",3396190,169.8944472236118]],
                   PRIMEM["Reference_Meridian",0],
                   UNIT["Degree",0.017453292519943295]],
                 PROJECTION["Mercator_1SP"],
                 PARAMETER["central_meridian",0],
                 PARAMETER["false_easting",0],
                 PARAMETER["false_northing",0],
                 UNIT["Meter",1],
                 PARAMETER["latitude_of_origin",0.0]]"""
        testname = os.path.join(self.path,'mars_merc_wkt.svg')
        s = bar.ScaleBar.from_projstring(wkt, (0, 0, 180,65), outputname=testname)
        ref, test = getsvg(get_path('mars_merc_wkt.svg'), testname)
        self.assertEqual(ref, test)
        os.remove(testname)

    def test_polar_wktstring(self):
        wkt = """PROJCS["Mars_South_Pole_Stereographic",
                GEOGCS["Mars 2000",
                    DATUM["D_Mars_2000",
                    SPHEROID["Mars_2000_IAU_IAG",3396190.0,169.89444722361179]],
                    PRIMEM["Greenwich",0],
                    UNIT["Decimal_Degree",0.0174532925199433]],
                    PROJECTION["Stereographic"],
                    PARAMETER["False_Easting",0],
                    PARAMETER["False_Northing",0],
                    PARAMETER["Central_Meridian",0],
                    PARAMETER["Scale_Factor",1],
                    PARAMETER["Latitude_Of_Origin",-90],
                    UNIT["Meter",1]]"""
        testname = os.path.join(self.path,'mars_polar_wkt.svg')
        s = bar.ScaleBar.from_projstring(wkt, (0, -90, 180,-40), outputname=testname, cliplat=-90)
        ref, test = getsvg(get_path('mars_polar_wkt.svg'), testname)
        self.assertEqual(ref, test)
        os.remove(testname)

    def test_lambert_wktstring(self):
        wkt = """PROJCS["Moon_Lambert_Conformal_Conic_AUTO",
                GEOGCS["Moon 2000",
                    DATUM["D_Moon_2000",
                    SPHEROID["Moon_2000_IAU_IAG",1737400.0,0.0]],
                    PRIMEM["Greenwich",0],
                    UNIT["Decimal_Degree",0.0174532925199433]],
                    PROJECTION["Lambert_Conformal_Conic"],
                    PARAMETER["False_Easting",0],
                    PARAMETER["False_Northing",0],
                    PARAMETER["Central_Meridian",0],
                    PARAMETER["Standard_Parallel_1",43],
                    PARAMETER["Standard_Parallel_2",73],
                    PARAMETER["Latitude_Of_Origin",0],
                    UNIT["Meter",1]]"""
        testname = os.path.join(self.path, 'lunar_lamb_wkt.svg')
        s = bar.ScaleBar.from_projstring(wkt, (33.25, 36, 60, 78.11), outputname=testname)
        ref, test = getsvg(get_path('lunar_lamb_wkt.svg'), testname)
        self.assertEqual(ref, test)
        os.remove(testname)

