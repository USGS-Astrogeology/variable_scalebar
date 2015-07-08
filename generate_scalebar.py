# -*- coding: utf-8 -*-

import sys

import numpy as np
import matplotlib.pylab as plt
from scipy.interpolate import interp1d

from scalebar.examples import get_path
from scalebar.fileio import gdalio
from scalebar.utils import util
from scalebar.bar import bar

if __name__ == '__main__':
    #Read file and get projection information
    #ds = get_path('Mars_MGS_MOLA_ClrShade_MAP2_0.0N0.0_MERC.tif')
    #ds = get_path('Mars_MGS_MOLA_ClrShade_MAP2_90.0N0.0_POLA.tif')
    ds = get_path('Lunar_LRO_LOLA_Shade_MAP2_90.0N20.0_LAMB.tif')
    S = bar.ScaleBar.from_image(ds, outputname='lamb.svg', lon_major_ticks=[25,50,75])

