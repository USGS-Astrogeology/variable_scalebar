import sys
from metadata import extract_metadata

projstring = sys.argv[1]

extract_metadata.extract_projstring(projstring)
