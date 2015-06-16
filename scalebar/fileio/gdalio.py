from osgeo import gdal
import osr

from scalebar.metadata import extract_metadata as em

class GeoDataSet(object):
    def __init__(self, filename):
        self.filename = filename
        self.ds = gdal.Open(filename)

    @property
    def geotransform(self):
        if not getattr(self, '_geotransform', None):
            self._geotransform = self.ds.GetGeoTransform()
        return self._geotransform

    @property
    def standardparallels(self):
        if not getattr(self, '_standardparallels', None):
            self._standardparallels = em.get_standard_parallels(self.spatialreference)
        return self._standardparallels

    @property
    def unittype(self):
        if not getattr(self, '_unittype', None):
            self._unittype = self.ds.GetRasterBand(1).GetUnitType()
        return self._unittype

    @property
    def spatialreference(self):
        if not getattr(self, '_srs', None):
            self._srs = osr.SpatialReference()
            self._srs.ImportFromWkt(self.ds.GetProjection())
            try:
                self._srs.MorphToESRI()
                self._srs.MorphFromESRI()
            except: pass

            #Setup the GCS
            self._gcs = self._srs.CloneGeogCS()
        return self._srs

    @property
    def geospatial_coordinate_system(self):
        if not getattr(self, '_gcs', None):
            self._gcs = self.spatialreference.CloneGeogCS()
        return self._gcs

    @property
    def latlon_extent(self):
        if not getattr(self, '_latlonextent', None):
            ext = self.extent

            llat, llon = self.pixel_to_latlon(ext[0][0], ext[0][1])
            ulat, ulon = self.pixel_to_latlon(ext[1][0], ext[1][1])

            self._latlonextent = [(llat, llon), (ulat, ulon)]
        return self._latlonextent

    @property
    def extent(self):
        if not getattr(self, '_geotransform', None):
            self.geotransform

        if not getattr(self, '_extent', None):
            gt = self.geotransform
            minx = gt[0]
            maxy = gt[3]

            maxx = minx + gt[1] * self.ds.RasterXSize
            miny = maxy + gt[5] * self.ds.RasterYSize

            self._extent = [(minx, miny), (maxx, maxy)]

        return self._extent

    @property
    def coordinate_transformation(self):
        if not getattr(self, '_ct', None):
            self._ct = osr.CoordinateTransformation(self.spatialreference,
                                                  self.geospatial_coordinate_system)
        return self._ct

    @property
    def inverse_coordinate_transformation(self):
        if not getattr(self, '_ict', None):
                       self._ict = osr.CoordinateTransformation(self.geospatial_coordinate_system,
                                                                self.spatialreference)
        return self._ict

    def pixel_to_latlon(self, x, y):

        if not getattr(self, 'geotransform', None):
            self.geotransform

        if not getattr(self, 'srs', None):
            self.spatialreference

        gt = self.geotransform
        x = gt[0] + (x * gt[1]) + (y * gt[2])
        y = gt[3] + (x * gt[4]) + (y * gt[5])
        lon, lat, _ = self.coordinate_transformation.TransformPoint(x, y)

        return lat, lon

    def latlon_to_pixel(self, lat, lon):
        gt = self.geotransform
        ulat, ulon, _ = self.inverse_coordinate_transformation.TransformPoint(lon, lat)
        x = (ulat - gt[0]) / gt[1]
        y = (ulon - gt[3]) / gt[5]
        return x, y

    @property
    def ndv(self, band=1):
        if not getattr(self, '_ndv', None):
            self._ndv = self.ds.GetRasterBand(band).GetNoDataValue()
        return self._ndv


