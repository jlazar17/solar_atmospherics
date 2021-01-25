import sys 
import os
from os.path import expandvars
cwd = os.getcwd()

moduledir= '/data/user/jlazar/solar_atmospherics/processing/processing_modules/'
if moduledir not in sys.path:
    sys.path.append(moduledir)


from I3Tray import I3Tray
from icecube import tableio, hdfwriter, icetray, dataclasses

from initialize_args import initialize_parser
options, args = initialize_parser()

infiles = [options.gcdfile, options.infile]
if not callable(options.h5file):
    h5file = options.h5file
else:
    h5file = options.h5file(options.infile)
print(h5file)

tray = I3Tray()
tray.AddModule("I3Reader","reader")(("FilenameList",infiles))
h5outkeys = ['ZTravel', 'oneweight','COGZ', 'COGZSigma', 'NuEnergy', 'NuZenith', 'NuAzimuth', 'PrimaryType', 'RLogL', 'RecoAzimuth', 'RecoZenith']
tray.AddModule(tableio.I3TableWriter, "hdfwriter")(
        ("tableservice",hdfwriter.I3HDFTableService(h5file)),
        ("SubEventStreams",["TTrigger"]),
        ("keys",h5outkeys)
        )
tray.Execute()
tray.Finish()
