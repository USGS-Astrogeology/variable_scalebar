# -*- coding: utf-8 -*-

import itertools
import math
import sys

import numpy as np
import pyproj
import svgwrite as svg
from svgwrite import cm

from scalebar.examples import get_path
from scalebar.fileio import gdalio
from scalebar.utils import util
from scalebar.metadata import extract_metadata as emd

class ScaleBar():

    """
    Parameters
    ----------
    spatialreference : object
                       A OSR spatial reference object.
    extent : iterable
             An iterable in the form xmin, ymin, xmax, ymax

    nnodes : int
             The number of nodes used to create smoother lines

    cliplat : float
              The latitude at which the scale bar reflects, e.g. the equator

    lat_tick_interval : int
                        The frequency at which latitude lines are labeled

    mapscale : float
               The map scale, e.g. 1/1000000.  Must be expressed as a fraction (ratio)

    lon_minor_ticks : list
                      Unlabeled tick lines

    lon_major_ticks : list
                      Labeled tick lines

    symmetrical : bool
                  Determines whether the scale bar is reflected over the central meridian

    height : float
             The height, in cm, of the scale bar

    fontsize : float
               The point size of the font (Default: 12)

    padding : float
              The total padding around the scale bar used for label space, etc.
              Padding is added to each edge.

    outputnamne : str
                  Name of the output file.  This can be a full path.

    Attributes
    ----------

    """
    def __init__(self, spatialreference, extent, nnodes=51, cliplat=0.0, lat_tick_interval=5, mapscale=1/1e6,
                lon_minor_ticks=[12.5], lon_major_ticks=[25, 50, 75],
                symmetrical=True, height = 4.0, fontsize=12, padding=1.0, outputname='scalebar.svg'):
        nnodes = self._checknnodes(nnodes)

        self.fontsize = fontsize
        self.height = height
        self.nnodes = nnodes
        self.outputname = outputname
        self.padding = padding
        self._dwg = None

        (xmin, ymin), (xmax, ymax) = extent
        projstr = spatialreference.ExportToProj4()
        semimajor = spatialreference.GetSemiMajor()
        semiminor = spatialreference.GetSemiMinor()

        name = emd.get_projection_name(spatialreference)
        parallels = emd.get_standard_parallels(spatialreference)

        #Create proj4 projection and geod objects
        proj = pyproj.Proj(projstr)
        geod = pyproj.Geod(a=semimajor, b=semiminor)

        #Setup start and stop nodes
        self.coords = np.empty((nnodes * 2, 2))
        self.coords[:self.nnodes,0] = xmin
        self.coords[self.nnodes:,0] = xmax
        self.coords[:,1] = np.tile(np.linspace(ymin, ymax, self.nnodes), 2)

        #Convert to pixel grid to latlon grid
        lon, lat =  proj(self.coords[:,0], self.coords[:,1], inverse=True)

        if name != 'Polar_Stereographic':

            if parallels[0] >= lat[0] and parallels[0] <= lat[1]:
                p = parallels[0]
            else:
                p = parallels[1]

            #Ensure that the standard parallel, where scale is correct, is in the linspace
            sidx = np.abs(lat[:self.nnodes] - p).argmin()
            eidx = np.abs(lat[self.nnodes:] - p).argmin()
            lat[:self.nnodes][sidx] = p
            lat[self.nnodes:][eidx] = p
            slon = lon[:self.nnodes]
            slat = lat[:self.nnodes]
            elon = lon[self.nnodes:]
            elat = lat[self.nnodes:]

            self.mask = slat >= cliplat
            #Pass the latlon grid into the geod to compute distances
            _, _, distance = geod.inv(slon[self.mask], slat[self.mask], elon[self.mask], elat[self.mask])
            distance *= 100  #m to cm
            distance *= mapscale #Apply the map scale
            distance /= distance[eidx] #Compute the scaling factor as a function of latitude using a standard parallel
        else:
            #Manually compute k
            self.coords = np.empty((nnodes * 2, 2))
            self.coords[:,1] = lat = np.tile(np.linspace(np.min(lat), 90, self.nnodes), 2)
            distance = np.empty(len(self.coords[:,1]))
            k_naught = emd.get_scale_factor(spatialreference)
            clat = emd.get_latitude_of_origin(spatialreference)
            clon = emd.get_central_meridian(spatialreference)
            for i, l in enumerate(self.coords[:,1]):
                distance[i] = (2 * k_naught) / (1.0 + math.sin(math.radians(clat)) * math.sin(math.radians(l)) +\
                            math.cos(math.radians(clat))*math.cos(math.radians(l))*math.cos(math.radians(180 - clon)))
            distance = distance[::-1]
            self.mask = self.coords[self.nnodes:,1] >= cliplat

        lon_major_ticks = map(lambda x: x * 1000, lon_major_ticks) #km to m
        lon_minor_ticks = map(lambda x: x * 1000, lon_minor_ticks)

        ticks = lon_major_ticks + lon_minor_ticks
        ticks.sort()
        ticks = ticks[::-1]

        for l in ticks:
            line_coords = ((l * 100) *  mapscale) * distance
            if self._dwg == None:
                length = np.max(line_coords)
                size = (length * 2, self.height)
                self.createdrawing(size)
                if symmetrical == True:
                    size = list(size)
                    size[0] /= 2
                    size = tuple(size)
                self.createvertical(size)

            nodes = zip(line_coords[::-1] + size[0], self.y[::-1])
            for i, start in enumerate(nodes[:-1]):
                coords = self._pad_and_convert(start, nodes[i + 1])
                self.drawline(coords, group=self.vertical)

                if i == 0 and l in lon_major_ticks:
                    dist = self._dwg.text('{}km'.format(l / 1000), (coords[0][0], (self.y[-1]  + self.padding * 1.3) * cm))
                    self._dwg.add(dist)
            if symmetrical:
                nline_coords = (line_coords * -1)
                nodes = zip(nline_coords[::-1] + size[0], self.y[::-1])
                for i, start in enumerate(nodes[:-1]):
                    coords = self._pad_and_convert(start, nodes[i + 1])
                    self.drawline(coords, group=self.vertical)
                    if i == 0 and l in lon_major_ticks:
                        dist = self._dwg.text('{}km'.format(l / 1000), (coords[0][0], (self.y[-1] + padding * 1.3) * cm ))
                        self._dwg.add(dist)


        #Compute the latrange and labels
        latrange = lat[:self.nnodes][self.mask]
        ticks = np.arange(util.integerround(latrange[0] + lat_tick_interval) ,latrange[-2], lat_tick_interval)
        ticks = labels = np.hstack((round(latrange[0], 1), ticks, round(latrange[-1], 1)))
        horizontal_ticks = self._dwg.add(self._dwg.g(id='horizontal_tick', stroke='black'))
        #Compute the y coordinate values in scalebar space

        horizontals = self.height / (np.max(ticks) - np.min(ticks)) *(ticks - np.min(ticks))
        horizontals = np.abs(horizontals - self.height)
        for i, h in enumerate(horizontals):
            x = [(size[0] + self.padding) * cm, (size[0] * 2 + self.padding) * cm]
            y = [(h + self.padding)  * cm] * 2
            xy = zip(x, y)
            line = self._dwg.line(start=xy[0], end=xy[1])
            horizontal_ticks.add(line)
            if i % 2 == 0:
                lat = self._dwg.text(u'{}\u00b0'.format(labels[i]), ((size[0] * 2 + 1.0) * cm, y[1]))
                self.text.add(lat)

            if symmetrical:
                x = [self.padding * cm, (size[0] + self.padding) * cm]
                xy = zip(x, y)
                line = self._dwg.line(start=xy[0], end=xy[1])
                horizontal_ticks.add(line)
                if i % 2 == 0:
                    lat = self._dwg.text(u'{}\u00b0'.format(labels[i]), (0.0 * cm, y[1]))
                    self.text.add(lat)

        self._dwg.save()

    @classmethod
    def from_image(cls, datasource, **kwargs):
        """
        Constructor that generates a scalebar from a map projected image.

        Parameters
        -----------
        datasource : str
                     Path to the datasource

        """
        ds = gdalio.GeoDataSet(datasource)
        srs = ds.spatialreference
        extent = ds.extent
        return cls(srs, extent, **kwargs)

    @classmethod
    def from_projstring(cls, projstring, extent, **kwargs):
        """
        Constructor that generates a scalebar from an OSR supported
        projection string and a user defined lat/lon extent

        Parameters
        ----------
        projstring : str
                     OSR supported projection string, i.e. WKT, ESRI WKT, proj4

        extent : tuple
                 in the form (minlat, minlon, maxlat, maxlon)
        """
        srs = emd.extract_projstring(projstring)
        return cls(srs, extent, **kwargs)

    def createdrawing(self, size):
        xsize = (size[0] + self.padding * 2) * cm
        ysize = (size[1] + self.padding * 2) * cm
        self._dwg = svg.Drawing(self.outputname, size=(xsize, ysize), debug=True)
        self.text = self._dwg.add(self._dwg.g(font_size=self.fontsize))
        self.vertical = self._dwg.add(self._dwg.g(id='vertical', stroke='black'))

    def createvertical(self, size):
        y = self.coords[:self.nnodes, 1][self.mask]
        #Rescale coordinates to scalebar space
        y = self.height / (np.max(y) - np.min(y)) *(y - np.min(y))
        ny = len(y)

        self.y = y
        #Draw the line(s)
        center = size[0]
        nodes = list(itertools.izip_longest([center], y, fillvalue=center))
        for i, start in enumerate(nodes[:-1]):
            coords = self._pad_and_convert(start, nodes[i + 1])
            self.drawline(coords, group=self.vertical)

    def drawline(self, coords, group=None):
        line = self._dwg.line(start=coords[0], end=coords[1])
        group.add(line)

    def _pad_and_convert(self, *args):
        formatted = []
        for i, a in enumerate(args):
            coords = list(a)
            formatted.append(tuple(map(lambda x: (x + self.padding) * cm, coords)))
        return formatted

    def _checknnodes(self, nnodes):
        if nnodes % 2 == 0:
            nnodes += 1
        return nnodes
