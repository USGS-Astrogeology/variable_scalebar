import argparse
import os

from scalebar.bar import bar

def parseargs():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='Latitude dependent scalebar generation')
    parser.add_argument('-e', '--extent', action='append', dest='extent', default=[],help='If providing a projection string, an extent in the form (minlat, minlon, maxlat, maxlon) is also required.')
    parser.add_argument('-L', action='append', dest='lon_major_ticks', default=[25, 50, 75], help='Distance(s) at which major ticks are to be drawn and labeled.')
    parser.add_argument('-l', action='append', dest='lon_minor_ticks', default=[12.5], help='Distance(s) at which minor ticks are to be drawn, but not labeled.')
    parser.add_argument('-n', action='store', type=int, dest='nnodes', default=51, help='Number of nodes at which to draw verticals.  More nodes results in smoother plots.')
    parser.add_argument('-c', action='store', type=float, dest='cliplat', default=0.0, help='Latitude at which to clip the plot, e.g. 0.0 to generate a scale bar for the northern hemisphere.  Set to -90.0 for south polar stereographic.')
    parser.add_argument('-i', action='store', type=int, dest='lat_tick_interval', default=5, help='Interval at which latitudinal lines are drawn, e.g. every 5 degrees.')
    parser.add_argument('-m', action='store', type=float, dest='mapscale', default=1/1e6, help='Map scale in fractional form, e.g. 1/1000000')
    parser.add_argument('-t', action='store', type=float, dest='height', default=4.0, help='Scalebar height in cm.')
    parser.add_argument('-f', action='store', type=float, dest='fontsize', default=12.0, help='Font size.')
    parser.add_argument('inputds', action='store', help='Either a projected image, or a projection string')
    parser.add_argument('outputname', action='store', help='The output file name')    
    
    return parser.parse_args()

def main():
    """
    Program Main
    """
    kwargs = vars(parseargs())
    ds = kwargs.pop('inputds')
    extent = kwargs.pop('extent')
    
    if os.path.exists(ds):
        bar.ScaleBar.from_image(ds, **kwargs)
    else:
        bar.ScaleBar.from_projstring(ds, extent, **kwargs)  

if __name__ == '__main__':
    main()
