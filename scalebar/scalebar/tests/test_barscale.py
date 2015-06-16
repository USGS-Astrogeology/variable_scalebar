import unittest
from .. import scalebar

from scalebar.examples import get_path
from scalebar.fileio import gdalio

class TestScaleBarMercator(unittest.TestCase):
    def setUp(self):
        self.ds = gdalio.GeoDataSet(get_path('Mars_MGS_MOLA_ClrShade_MAP2_0.0N0.0_MERC.tif'))
    def testMercator(self):
        #Jay opens an input Mercator image and gets the extent
        extent = self.ds.extent
        print extent
