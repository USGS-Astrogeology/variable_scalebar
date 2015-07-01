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

def cm_to_inches(cm):
    return cm / 2.54

def main(nnodes=51, cliplat=0.0, lat_tick_interval=5, mapscale=1/1e6, lon_minor_ticks=[25], lon_major_ticks=[50, 100], symmetrical=True, size=(30,4), dpi=300, fontsize=10, linewidth=0.5):
    #Read file and get projection information
    ds = gdalio.GeoDataSet(get_path('Mars_MGS_MOLA_ClrShade_MAP2_0.0N0.0_MERC.tif'))
    #ds = gdalio.GeoDataSet(get_path('Mars_MGS_MOLA_ClrShade_MAP2_90.0N0.0_POLA.tif'))
    (xmin, ymin), (xmax, ymax) = ds.extent
    semimajor, semiminor, invflat = ds.spheroid
    projstr = ds.spatialreference.ExportToProj4()

    figsize = size
    if symmetrical == True:
        size = list(size)
        size[0] /= 2
        size = tuple(size)

    #Write a log

    #Create proj4 projection and geod objects
    proj = pyproj.Proj(projstr)
    geod = pyproj.Geod(a=semimajor, b=semiminor)

    #Setup start and stop nodes
    coords = np.empty((nnodes * 2, 2))
    coords[:nnodes,0] = xmin
    coords[nnodes:,0] = xmax
    coords[:,1] = np.tile(np.linspace(ymin, ymax, nnodes), 2)

    #Convert to pixel grid to latlon grid
    lon, lat =  proj(coords[:,0], coords[:,1], inverse=True)

    slon = lon[:nnodes]
    slat = lat[:nnodes]
    elon = lon[nnodes:]
    elat = lat[nnodes:]

    mask = slat >= cliplat

    #Pass the latlon grid into the geod to compute distances
    _, _, distance = geod.inv(slon[mask], slat[mask], elon[mask], elat[mask])

    #Get pixel count and cm per pixel
    npixels = xmax - xmin
    distance /= ds.rastersize[0]  #meters per pixel

    #Apply the map scale
    #figsize = (cm_to_inches(size[0]), cm_to_inches(size[1]))
    fig = plt.figure(dpi=dpi, figsize=figsize)

    #Create the vertical
    y = coords[:nnodes, 1][mask] / (ds.rastersize[0])
    y = (y * size[1]) / y[-1]
    x = np.zeros(len(y))
    l1 = plt.plot(x,y , 'k-', linewidth=linewidth)
    print size[0]
    num = (size[0] / mapscale) / 100 #cm to m
    print num
    lon_major_ticks = map(lambda x: x * 1000, lon_major_ticks) #km to m
    lon_minor_ticks = map(lambda x: x * 1000, lon_minor_ticks)

    #Compute and plot the outer extents
    pixels_per_scale_distance = num / distance
    x = (pixels_per_scale_distance * size[0]) / pixels_per_scale_distance[-1]
    plt.plot(x, y, 'k-', linewidth=linewidth)
    #plt.text(x[0], y[0] - y[1], '{}km'.format('150'), fontsize=fontsize)
    if symmetrical:
        nx = x * -1
        plt.plot(nx, y, 'k-', linewidth=linewidth)
        #plt.text(nx[0], y[0] - y[1], '{}km'.format('150'), fontsize=fontsize)

    ticks = lon_major_ticks + lon_minor_ticks

    for l in ticks:
        line = (x * l) / num
        plt.plot(line, y, 'k-', linewidth=linewidth)
        #if l in lon_major_ticks:
            #plt.text(line[0], y[0] - y[1], '{}km'.format(l / 1000), fontsize=fontsize)
        if symmetrical:
            nline = line * -1
            plt.plot(nline, y, 'k-', linewidth=linewidth)
            #if l in lon_major_ticks:
                #plt.text(nline[0], y[0] - y[1], '{}km'.format(l / 1000), fontsize=fontsize)

    #Compute the latrange and labels
    latrange = lat[:nnodes][mask]
    ticks = np.arange(integerround(latrange[0] + lat_tick_interval) ,latrange[-2], lat_tick_interval)
    ticks = labels = np.hstack((round(latrange[0], 1), ticks, round(latrange[-1], 1)))

    #Compute the y coordinate values in scalebar space
    horizontals =  (size[1] * ticks) / ticks[-1]
    for i, h in enumerate(horizontals):
        x = [0, size[0]]
        y = [h, h]
        plt.plot(x, y, 'k-', linewidth=linewidth)
        #plt.text(size[0] * 1.01, h, u'{}\u00b0'.format(labels[i]), fontsize=fontsize)
        if symmetrical:
            x[1] *= -1
            plt.plot(x, y, 'k-', linewidth=linewidth)
            #plt.text(size[0] * - 1 - .7, h, u'{}\u00b0'.format(labels[i]), fontsize=fontsize)

    #Hide the tick labels
    #plt.gca().axes.get_xaxis().set_visible(False)
    #plt.gca().axes.get_yaxis().set_visible(False)
    plt.gca().axis('off')
    plt.tight_layout(pad=0.0, w_pad=0.0, h_pad=0.0)
    plt.savefig('test.svg', pad_inches=0)
    #plt.show()

def mainsvg(nnodes=51, cliplat=0.0, lat_tick_interval=5, mapscale=1/1e6, lon_minor_ticks=[25], lon_major_ticks=[50, 100], symmetrical=True, size=(30,4), dpi=300, fontsize=10, linewidth=0.5):
    import svgwrite as svg
    from svgwrite import cm

    #Read file and get projection information
    ds = gdalio.GeoDataSet(get_path('Mars_MGS_MOLA_ClrShade_MAP2_0.0N0.0_MERC.tif'))
    #ds = gdalio.GeoDataSet(get_path('Mars_MGS_MOLA_ClrShade_MAP2_90.0N0.0_POLA.tif'))
    (xmin, ymin), (xmax, ymax) = ds.extent
    semimajor, semiminor, invflat = ds.spheroid
    projstr = ds.spatialreference.ExportToProj4()

    dwg = svg.Drawing('svgtest.svg', size=(size[0] * cm, size[1] * cm), debug=True)

    if symmetrical == True:
        size = list(size)
        size[0] /= 2
        size = tuple(size)

    #Create proj4 projection and geod objects
    proj = pyproj.Proj(projstr)
    geod = pyproj.Geod(a=semimajor, b=semiminor)

    #Setup start and stop nodes
    coords = np.empty((nnodes * 2, 2))
    coords[:nnodes,0] = xmin
    coords[nnodes:,0] = xmax
    coords[:,1] = np.tile(np.linspace(ymin, ymax, nnodes), 2)

    #Convert to pixel grid to latlon grid
    lon, lat =  proj(coords[:,0], coords[:,1], inverse=True)

    slon = lon[:nnodes]
    slat = lat[:nnodes]
    elon = lon[nnodes:]
    elat = lat[nnodes:]

    mask = slat >= cliplat

    #Pass the latlon grid into the geod to compute distances
    _, _, distance = geod.inv(slon[mask], slat[mask], elon[mask], elat[mask])

    #Get pixel count and cm per pixel
    npixels = xmax - xmin
    distance /= ds.rastersize[0]  #meters per pixel

    #Create the vertical
    y = coords[:nnodes, 1][mask] / (ds.rastersize[0])
    y = (y * size[1]) / y[-1]
    ny = len(y)
    x = np.zeros(len(y))

    #Draw the line(s)
    vertical = dwg.add(dwg.g(id='vertical', stroke='black'))
    center = size[0] * cm
    for i in range(ny - 1):
        line = dwg.line(start=(center, y[i] * cm), end=(center, y[i+1] * cm))
        vertical.add(line)



    num = (size[0] / mapscale) / 100 #cm to m
    lon_major_ticks = map(lambda x: x * 1000, lon_major_ticks) #km to m
    lon_minor_ticks = map(lambda x: x * 1000, lon_minor_ticks)

    #Compute and plot the outer extents
    pixels_per_scale_distance = num / distance
    x = (pixels_per_scale_distance * size[0]) / pixels_per_scale_distance[-1]
    max_extents = dwg.add(dwg.g(id='maxextents', stroke='black'))
    nodes = zip((x + size[0]) * cm, y[::-1] * cm)
    for i, start in enumerate(nodes[:-1]):
        line = dwg.line(start=(start), end=(nodes[i + 1]))
        max_extents.add(line)
    if symmetrical:
        nx = (x * -1) + size[0]
        nodes = zip(nx * cm, y[::-1] * cm)
        for i, start in enumerate(nodes[:-1]):
            line = dwg.line(start=start, end=nodes[i+1])
            max_extents.add(line)

    ticks = lon_major_ticks + lon_minor_ticks
    vertical_ticks = dwg.add(dwg.g(id='vertical_ticks', stroke='black'))

    for l in ticks:
        line_coords = (x * l) / num
        nodes = zip((line_coords + size[0]) * cm, y[::-1] * cm)
        for i, start in enumerate(nodes[:-1]):
            line = dwg.line(start=start, end=nodes[i+1])
            vertical_ticks.add(line)

        if symmetrical:
            nline_coords = (line_coords * -1) + size[0]
            nodes = zip(nline_coords * cm, y[::-1] * cm)
            for i, start in enumerate(nodes[:-1]):
                line = dwg.line(start=start, end=nodes[i+1])
                vertical_ticks.add(line)


    #Compute the latrange and labels
    latrange = lat[:nnodes][mask]
    ticks = np.arange(integerround(latrange[0] + lat_tick_interval) ,latrange[-2], lat_tick_interval)
    ticks = labels = np.hstack((round(latrange[0], 1), ticks, round(latrange[-1], 1)))

    horizontal_ticks = dwg.add(dwg.g(id='horizontal_tick', stroke='black'))

    #Compute the y coordinate values in scalebar space
    horizontals =  (size[1] * ticks) / ticks[-1]
    for i, h in enumerate(horizontals):
        x = [size[0] * cm, size[0] * 2 * cm]
        y = [h * cm, h * cm]
        xy = zip(x, y)
        line = dwg.line(start=xy[0], end=xy[1])
        horizontal_ticks.add(line)

        if symmetrical:
            x = [0 * cm, size[0] * cm]
            y = [h * cm, h * cm]
            xy = zip(x, y)
            line = dwg.line(start=xy[0], end=xy[1])
            horizontal_ticks.add(line)


    dwg.save()
if __name__ == '__main__':
    mainsvg()

