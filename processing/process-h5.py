import sys 
import os
from os.path import expandvars
cwd = os.getcwd()

moduledir= '/data/user/jlazar/solar/solar_atmospherics/processing/processing_modules/'
if moduledir not in sys.path:
    sys.path.append(moduledir)


from I3Tray import I3Tray
from icecube import tableio, hdfwriter, icetray, dataclasses

from initialize_args import initialize_parser
from rename_out_vars import RenameOutVars
from controls import process_params
i3streams = process_params()['i3streams']
options, args = initialize_parser()

infiles = [options.gcdfile, options.infile]
if not callable(options.h5file):
    h5file = options.h5file
else:
    h5file = options.h5file(options.infile)
print(h5file)
if 'nancy' in options.infile:
    fluxname = 'nancy'
elif 'genie' in options.infile:
    fluxname = 'genie'
elif 'corsika' in options.infile:
    fluxname = 'corsika'


if fluxname in ['genie', 'nancy']:
    corsika_set=None
else:
    corsika_set = int(options.infile.split('.')[-4])

icetray.set_log_level(icetray.I3LogLevel.LOG_ERROR)
tray = I3Tray()
tray.AddModule("I3Reader","reader")(("FilenameList",infiles))
tray.AddModule(RenameOutVars, geometry=None, fluxname=fluxname, corsika_set=corsika_set)
h5outkeys = ['ZTravel', 'oneweight','COGZ', 'COGZSigma', 'TrueEnergy', 'TrueZenith', 'TrueAzimuth', 'PrimaryType', 'RLogL', 'RecoAzimuth', 'RecoZenith', 'weights', 'MuonRate', 'QTot', 'LDir_A', 'NDirPulse_A', 'NDirDOM_A', 'NDirStr_A', 'LDir_B', 'NDirPulse_B', 'NDirDOM_B', 'NDirStr_B', 'LDir_C', 'NDirPulse_C', 'NDirDOM_C', 'NDirStr_C', 'LDir_D', 'NDirPulse_D', 'NDirDOM_D', 'NDirStr_D', 'LDir_E', 'NDirPulse_E', 'NDirDOM_E', 'NDirStr_E', 'RecoAngSep', 'BayesRatio']
tray.AddModule(tableio.I3TableWriter, "hdfwriter")(
        ("tableservice",hdfwriter.I3HDFTableService(h5file)),
        ("SubEventStreams",["TTrigger"]),
        ("keys",h5outkeys)
        )
tray.Execute()
tray.Finish()
