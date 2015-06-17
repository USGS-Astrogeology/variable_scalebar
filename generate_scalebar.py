# -*- coding: utf-8 -*-

import sys

import numpy as np
import pyproj
import matplotlib.pylab as plt
from scipy.interpolate import interp1d

from scalebar.examples import get_path
from scalebar.fileio import gdalio


def integerround(x, base=5):
    return int(base * round(float(x) / base))

def main(nnodes=51, cliplat=0.0, lat_tick_interval=5):
    #Read file and get projection information
    ds = gdalio.GeoDataSet(get_path('Mars_MGS_MOLA_ClrShade_MAP2_0.0N0.0_MERC.tif'))
    #ds = gdalio.GeoDataSet(get_path('Mars_MGS_MOLA_ClrShade_MAP2_90.0N0.0_POLA.tif'))
    (xmin, ymin), (xmax, ymax) = ds.extent
    semimajor, semiminor, invflat = ds.spheroid
    projstr = ds.spatialreference.ExportToProj4()

    #Write a log

    #Create proj4 projection and geod objects
    proj = pyproj.Proj(projstr)
    geod = pyproj.Geod(a=semimajor, b=semiminor)

    #Setup start and stop nodes
    coords = np.empty((nnodes * 2, 2))
    coords[:nnodes,0] = xmin
    coords[nnodes:,0] = xmax
    coords[:,1] = np.tile(np.linspace(ymin, ymax, nnodes), 2)
    print coords
    #Convert to pixel grid to latlon grid
    lon, lat =  proj(coords[:,0], coords[:,1], inverse=True)

    slon = lon[:nnodes]
    slat = lat[:nnodes]
    elon = lon[nnodes:]
    elat = lat[nnodes:]

    mask = slat >= cliplat

    #Pass the latlon grid into the geod to compute distances
    _, _, distance = geod.inv(slon[mask], slat[mask], elon[mask], elat[mask])

    #Get pixel count and meters per pixel
    npixels = xmax - xmin
    distance /= ds.rastersize[0]

    fig = plt.figure(figsize=(12, 4), dpi=100)
    y = coords[:nnodes, 1][mask] / (ds.rastersize[0])
    l1 = plt.plot(np.zeros(len(y)),y , 'k-')
    x2 = (1e6 / distance)
    x2a = x2 * -1
    l2 = plt.plot(x2, y, 'k-')
    l2a = plt.plot(x2a, y, 'k-')
    x1 = (5e5 / distance)
    x1a = x1 * -1
    l2 = plt.plot(x1, y, 'k-')
    l2a = plt.plot(x1a, y, 'k-')

    #Labels
    labels = np.arange(0, 2.5e5 * 5, 2.5e5)
    labels /= 1000 #m to km
    ys = np.empty(5)
    ys[:] = y[0] - 100
    c = 5
    xs = [x2a[0], x1a[0], 0, x1[1], x2[0]]
    for i, l in enumerate(labels):
        plt.text(xs[i] - c, ys[i], '{}km'.format(l), fontsize=8)


    func = interp1d(y, x2, bounds_error=False)

    #major horizontal ticks
    latrange = lat[:nnodes]
    ticks = np.arange(integerround(lat[0] + lat_tick_interval) ,lat[-2], lat_tick_interval)
    ticks = np.hstack((latrange[0], ticks, latrange[-1]))
    labels = ticks
    _, majorhorizontal =  proj(np.zeros(len(ticks)), ticks)
    majorhorizontal /= ds.rastersize[0]

    label_coordinates = []

    for i, m in enumerate(majorhorizontal):
        x = func(m)
        plt.plot([ds.central_meridian,x], [m,m], 'k-')
        plt.plot([ds.central_meridian, x * -1], [m, m], 'k-')

        plt.text(x + 8.5, m, u'{}º'.format(round(labels[i],1)), fontsize=8)
        plt.text(-x - 50, m, u'{}º'.format(round(labels[i],1)), fontsize=8)

    buffer = 100
    plt.xlim(x2a[-1] - buffer, x2[-1] + buffer)
    if cliplat != None:
        print "Setting cliplat"
        plt.ylim(cliplat - (2 * buffer), m + buffer)
    plt.show()


if __name__ == '__main__':
    main()

