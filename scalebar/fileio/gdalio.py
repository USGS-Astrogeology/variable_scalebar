from osgeo import gdal
import osr

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
    def scale(self):
        if not getattr(self, '_scale', None):
            self._scale = self.ds.GetRasterBand(1).GetScale()
        return self._scale

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
                self._srs.MorphFromESRI()
            except: pass

            #Setup the GCS
            self._gcs = self._srs.CloneGeogCS()
        return self._srs

    @property
    def latlonextent(self):
        if not getattr(self, '_geotransform', None):
                   self.geotransform

        if not getattr(self, '_latlonextent', None):


            self._latlonextent = [(),()]

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

    def pixel_to_latlon(self, lat, lon):

        if not getattr(self, 'geotransform', None):
            self.geotransform

        if not getattr(self, 'srs', None):
            self.spatialreference
        

        print self._srs.ExportToProj4()
        print self._gcs.ExportToProj4()
        if not getattr(self, 'ct', None):
            self.ct = osr.CoordinateTransformation(self.spatialreference,
                                                   self._gcs)
            print self.ct
        #(x, y, z) = self.ct.TransformPoint(18, 24, 0)

        #gt = self.geotransform
        #x = (x - gt[0]) /gt[1]
        #y = (y - gt[3]) / gt[5]

        return 0, 0

    def latlon_to_pixel(self):
        pass

    @property
    def ndv(self, band=1):
        if not getattr(self, '_ndv', None):
            self._ndv = self.ds.GetRasterBand(band).GetNoDataValue()
        return self._ndv


