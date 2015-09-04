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
             An iterable in the form (xmin, ymin, xmax, ymax) or
             (latmin, lonmin, latmax, lonmax)

    nnodes : int
             The number of nodes used to create smoother lines

    cliplat : float
              The latitude at which the scale bar reflects, e.g. the equator

    lat_tick_interval : int
                        The frequency at which latitude lines are labeled

    mapscale : float
               The denominator of the map scale, e.g. 1000000.

    lon_minor_ticks : list
                      Unlabeled tick lines, in kilometers

    lon_major_ticks : list
                      Labeled tick lines, in kilometers

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

    latlon : boolean
             
    Attributes
    ----------

    """
    def __init__(self, spatialreference, extent, nnodes=51, cliplat=0.0, lat_tick_interval=5, mapscale=1000000,
                lon_minor_ticks=[12.5], lon_major_ticks=[25, 50, 75],
                symmetrical=True, height = 4.0, fontsize=12, padding=1.0, outputname='scalebar.svg',
                latlon=False):

        nnodes = self._checknnodes(nnodes)

        self.fontsize = fontsize
        self.height = height
        self.nnodes = nnodes
        self.outputname = outputname
        self.padding = padding
        self._dwg = None
        self.spatialreference = spatialreference.__str__()
        self.mapscale = 1/float(mapscale)

        (xmin, ymin, xmax, ymax) = extent
        projstr = spatialreference.ExportToProj4()
        semimajor = spatialreference.GetSemiMajor()
        semiminor = spatialreference.GetSemiMinor()

        self.name = emd.get_projection_name(spatialreference)
        parallels = emd.get_standard_parallels(spatialreference)

        #Create proj4 projection
        proj = pyproj.Proj(projstr)
        #Setup start and stop nodes

        self.coords = np.empty((nnodes, 2))
        self.coords[:,0] = xmin
        self.coords[:,1] = np.linspace(ymin, ymax, self.nnodes)


        if latlon:
            #This is intentionally inverting lat/lon to match how GDAL returns image extents
            lat = self.coords[:,1]
            lon = np.empty(len(lat))
            lon[:] = xmin
        else:
            #Convert to pixel grid to latlon grid
            lon, lat =  proj(self.coords[:,0], self.coords[:,1], inverse=True)
        

        self.minlat = np.min(lat)
        self.minlon = np.min(lon)
        self.maxlat = np.max(lat)
        self.maxlon = np.max(lon)

        self.latlon_bounds = ((self.minlat, self.minlon),
                              (self.maxlat, self.maxlon))
        #Parallels
        if parallels[0] >= lat[0] and parallels[0] <= lat[1]:
            p = parallels[0]
        else:
            p = parallels[1]

        if 'Transverse_Mercator' in self.name:

            clat = emd.get_latitude_of_origin(spatialreference)
            clon = emd.get_central_meridian(spatialreference)

            if clat > 0:
                self.coords[:,1] = lat = np.linspace(np.min(lat), clat, self.nnodes)
            else:
                self.coords[:,1] = lat = np.linspace(np.max(lat), clat, self.nnodes)

            distance = np.empty(len(lat))
            k_naught = emd.get_scale_factor(spatialreference)
            for i, l in enumerate(lat):
                B = math.cos(math.radians(clon)) * math.sin(math.radians(clat) - math.radians(l))
                distance[i] = k_naught / math.sqrt(1.0 - B ** 2.0)
            distance = distance[::-1]
            self.mask = self.coords[:,1] >= cliplat
           
        elif 'Mercator' in self.name:
            self.mask = lat >= cliplat
            distance = 1.0 / np.cos(np.radians(lat[self.mask]))
            distance = distance[::-1]

        #elif 'Sinusoidal' in self.name:

        elif (('Equirectangular' in self.name) or ('Equidistant_Cylindrical' in self.name) \
              or ('Plate_Carree' in self.name) or ('Simple_Cylindrical' in self.name)):

            p1 = parallels[0]
            clon = emd.get_central_meridian(spatialreference)

            if p1 > 0:
                self.coords[:,1] = lat = np.linspace(np.min(lat), p1, self.nnodes)
            else:
                self.coords[:,1] = lat = np.linspace(np.max(lat), p1, self.nnodes)

            distance = np.empty(len(lat))
            for i, l in enumerate(lat):
                distance[i] = math.cos(math.radians(p1))/math.cos(math.radians(l))
            distance = distance[::-1]
            self.mask = self.coords[:,1] >= cliplat

        elif 'Lambert_Conformal' in self.name:
            self.mask = lat >= cliplat
            parallels.sort()

            p1 = math.radians(parallels[0])
            p2 = math.radians(parallels[1])

            cp1 = math.cos(p1)
            cp2 = math.cos(p2)
            n = np.log(cp1 / cp2) / np.log( math.tan((math.pi / 4) + (math.radians(parallels[1] / 2))) / math.tan((math.pi / 4) + (math.radians(parallels[0] / 2)) ))
            num = cp1 * np.tan(math.pi / 4 + math.radians(parallels[0] / 2)) ** n
            den = np.cos(np.radians(lat)) * np.tan(math.pi / 4 + np.radians(lat / 2.0)) ** n
            distance = num / den
            distance = distance[::-1]

        elif 'Stereographic' in self.name:
            clat = emd.get_latitude_of_origin(spatialreference)
            clon = emd.get_central_meridian(spatialreference)

            if clat > 0:
                self.coords[:,1] = lat = np.linspace(np.min(lat), clat, self.nnodes)
            else:
                self.coords[:,1] = lat = np.linspace(np.max(lat), clat, self.nnodes)
            distance = np.empty(len(lat))
            k_naught = emd.get_scale_factor(spatialreference)
            for i, l in enumerate(lat):
                distance[i] = (2 * k_naught) / (1.0 + math.sin(math.radians(clat)) * math.sin(math.radians(l)) +\
                            math.cos(math.radians(clat))*math.cos(math.radians(l))*math.cos(math.radians(180 - clon)))
            distance = distance[::-1]
            self.mask = self.coords[:,1] >= cliplat

            
        lon_major_ticks = map(lambda x: x * 1000, lon_major_ticks) #km to m
        lon_minor_ticks = map(lambda x: x * 1000, lon_minor_ticks)

        ticks = lon_major_ticks + lon_minor_ticks
        ticks.sort()
        ticks = ticks[::-1]

        south = False
        if lat[0] > lat[-1]:
            south = True
    
        #Vertical distance line logic
        for l in ticks:
            line_coords = ((l * 100) *  self.mapscale) * distance
            if self._dwg == None:
                length = np.max(line_coords)
                size = (length * 2, self.height)
                self.createdrawing(size)
                if symmetrical == True:
                    size = list(size)
                    size[0] /= 2
                    size = tuple(size)
                self.createvertical(size)
               
                #Check hemisphere
                if south == True:
                    ytext = self.y[0]
                else:
                    ytext = self.y[-1]
                #Label the vertical 
                center = (size[0]  + self.padding)* 0.995 # Offset left for font size
                dist = self._dwg.text('0', (center * cm, (ytext + self.padding * 1.3) * cm)) 
                self._dwg.add(dist)
               
            nodes = zip(line_coords[::-1] + size[0], self.y[::-1])
            for i, start in enumerate(nodes[:-1]):
                coords = self._pad_and_convert(start, nodes[i + 1])
                self.drawline(coords, group=self.vertical)
                if i == 0 and l in lon_major_ticks:
                    dist = self._dwg.text('{}km'.format(l / 1000), (coords[0][0], (ytext  + self.padding * 1.3) * cm))
                    self._dwg.add(dist)
            if symmetrical:
                nline_coords = (line_coords * -1)
                nodes = zip(nline_coords[::-1] + size[0], self.y[::-1])
                for i, start in enumerate(nodes[:-1]):
                    coords = self._pad_and_convert(start, nodes[i + 1])
                    self.drawline(coords, group=self.vertical)
                    if i == 0 and l in lon_major_ticks:
                        dist = self._dwg.text('{}km'.format(l / 1000), (coords[0][0], (ytext +self.padding * 1.3) * cm ))
                        self._dwg.add(dist)

        
        #Compute the latrange and labels
        latrange = lat[self.mask]
        if latrange[0] > latrange[-1]: #Ghetto monotonic check for southern hemisphere...
            ticks = np.arange(util.integerround(latrange[-2]), latrange[0] + lat_tick_interval, lat_tick_interval)
        else:
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
                ytext = y[1]
                lat = self._dwg.text(u'{}\u00b0'.format(labels[i]), ((size[0] * 2 + 1.0) * cm, ytext))
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
        packed_extent = ds.extent
        if 'extent' in kwargs.keys():
            extent = kwargs['extent']
            kwargs.pop('extent')
            latlon = True
        else:
            extent = (packed_extent[0][0], packed_extent[0][1],
                      packed_extent[1][0], packed_extent[1][1])
            latlon = False
        return cls(srs, extent, latlon=latlon, **kwargs)

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
        return cls(srs, extent, latlon=True, **kwargs)

    def createdrawing(self, size):
        xsize = (size[0] + self.padding * 2) * cm
        ysize = (size[1] + self.padding * 2) * cm
        self._dwg = svg.Drawing(self.outputname, size=(xsize, ysize), debug=True)
        self.text = self._dwg.add(self._dwg.g(font_size=self.fontsize))
        self.vertical = self._dwg.add(self._dwg.g(id='vertical', stroke='black'))

    def createvertical(self, size):
        y = self.coords[:, 1][self.mask]
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
