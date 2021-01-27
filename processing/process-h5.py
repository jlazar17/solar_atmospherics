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
from rename_nu_out_vars import RenameNuOutVars
from controls import process_params
i3streams = process_params()['i3streams']
options, args = initialize_parser()

infiles = [options.gcdfile, options.infile]
if not callable(options.h5file):
    h5file = options.h5file
else:
    h5file = options.h5file(options.infile)
print(h5file)

tray = I3Tray()
tray.AddModule("I3Reader","reader")(("FilenameList",infiles))
tray.AddModule(RenameNuOutVars)
h5outkeys = ['ZTravel', 'oneweight','COGZ', 'COGZSigma', 'NuEnergy', 'NuZenith', 'NuAzimuth', 'PrimaryType', 'RLogL', 'RecoAzimuth', 'RecoZenith']
tray.AddModule(tableio.I3TableWriter, "hdfwriter")(
        ("tableservice",hdfwriter.I3HDFTableService(h5file)),
        ("SubEventStreams",["TTrigger", 'InIceSplit']),
        ("keys",h5outkeys)
        )
tray.AddModule("I3Writer","i3writer")(
        ("Filename",'ahhhhhhhh.i3.zst'),
        ("Streams",i3streams)
        )
tray.Execute()
tray.Finish()
