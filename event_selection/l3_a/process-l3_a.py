import time
from optparse import OptionParser
import numpy as np
from glob import glob

print('loading I3tray...')
from I3Tray import *
print('loading icecube...')
from icecube import icetray, dataio, dataclasses
from icecube.common_variables import hit_multiplicity, hit_statistics, direct_hits
from icecube.STTools.seededRT.configuration_services import I3DOMLinkSeededRTConfigurationService
from icecube import TopologicalSplitter
from icecube import CoincSuite
from icecube import phys_services, DomTools, simclasses, VHESelfVeto
from icecube import lilliput, gulliver, gulliver_modules, paraboloid
from icecube import linefit, MuonGun, WaveCalibrator,wavedeform
from icecube import photonics_service
from icecube import TopologicalSplitter
import icecube.lilliput.segments
from icecube import tableio, hdfwriter
from icecube.icetray import I3Units
from icecube.common_variables import direct_hits
from icecube.common_variables import hit_multiplicity
from icecube.common_variables import track_characteristics
load('libtruncated_energy')
load("bayesian-priors")

from solar_atmospherics.modules import get_pulse_names, cut_bad_fits, cut_high_energy, is_lowup_filter, is_muon_filter, rename_MC_tree, has_TWSRT_offline_pulses, fix_weight_map, figure_out_gcd
from make_outfile_name import make_outfile_name

def initialize_parser():
    parser = OptionParser()
    parser.add_option('-n', '--nFrames', 
                      dest='nFrames',
                      default=0, 
                      type=int, 
                      help='How many frames to do this for. Default do all frames.')
    parser.add_option('-g', '--gcdfile',
                      dest='gcdfile',
                      type=str,
                      default =''
                     )
    parser.add_option("--ice_model", 
                      dest="ice_model", 
                      default='spice_3.2',
                      type=str, 
                      help='Ignore this'
                     )
    parser.add_option("-i", "--infile", 
                      dest="infile",
                      type=str,
                      default = '/data/sim/IceCube/2016/filtered/level2/neutrino-generator/nancy001/NuMu/low_energy/hole_ice/p1=0.3_p2=0.0/10/l2_00009414.i3.zst',
                     )
    parser.add_option("-o", "--outfile",
                      dest="outfile",
                      default=make_outfile_name
                     )
    options,args = parser.parse_args()
    return options, args

t0 = time.time()
print('parsing...')
options, args = initialize_parser()
infile        = options.infile
if options.gcdfile=='':
    gcdfile = figure_out_gcd(infile)
else:
    gcdfile = options.gcdfile

if 'corsika' in infile:
    filetype = 'corsika'
elif 'genie' in infile:
    filetype = 'genie'
elif 'nancy' in infile:
    filetype = 'nancy'
elif 'exp' in infile:
    filetype = 'exp_data'
if not callable(options.outfile):
    outfile = options.outfile
else:
    outfile = options.outfile(infile)
outfile = outfile.replace('JLevel', 'JLevel_%s' % filetype)
# save tempfile
tmpfile = outfile.replace('.i3.zst', '.npy')
np.save(tmpfile, [])
infiles = [gcdfile, infile]
icetray.set_log_level(icetray.I3LogLevel.LOG_ERROR)
#====================================
InIcePulses, SRTInIcePulses, SRTInIcePulses_NoDC_Qtot, SRTInIcePulses_NoDC = get_pulse_names(infile)
#====================================
tray = I3Tray()
tray.AddService("I3GSLRandomServiceFactory","Random") # needed for bootstrapping
tray.AddModule("I3Reader","reader")(
                ("FilenameList",infiles)
                )
# Remove high energy portion from GENIE simulation to make sure simulation is non-overlapping
if filetype=='genie':
    tray.AddModule(cut_high_energy)
tray.AddModule(rename_MC_tree, "_renameMCTree", Streams=[icetray.I3Frame.DAQ])
tray.AddModule(is_lowup_filter & ~is_muon_filter & has_TWSRT_offline_pulses,"selectValidData")
tray.AddModule(fix_weight_map,"patchCorsikaWeights")
tray.AddModule("I3OrphanQDropper","OrphanQDropper")
#======================================
stConfigService = I3DOMLinkSeededRTConfigurationService(
                     allowSelfCoincidence    = False,            # Default: False.
                     useDustlayerCorrection  = True,             # Default: True.
                     dustlayerUpperZBoundary =  0*I3Units.m,     # Default: 0m.
                     dustlayerLowerZBoundary = -150*I3Units.m,   # Default: -150m.
                     ic_ic_RTTime            =  1000*I3Units.ns, # Default: 1000m.
                     ic_ic_RTRadius          =  150*I3Units.m    # Default: 150m.
                    )
tray.AddModule("I3SeededRTCleaning_RecoPulse_Module", "SRTClean",
               InputHitSeriesMapName  = InIcePulses,
               OutputHitSeriesMapName = SRTInIcePulses,
               STConfigService        = stConfigService,
               #SeedProcedure         = "HLCCoreHits",
               NHitsThreshold         = 2,
               Streams                = [icetray.I3Frame.DAQ]
              )
tray.AddModule("I3TopologicalSplitter", "TTrigger",
               SubEventStreamName = 'TTrigger',
               InputName          = "SRTInIcePulses",
               OutputName         = "TTPulses",
               Multiplicity       = 4, 
               TimeWindow         = 2000, #Default=4000 ns
               XYDist             = 300, 
               ZDomDist           = 15, 
               TimeCone           = 1000, #Default=1000 ns
               SaveSplitCount     = True
              )
tray.AddSegment(CoincSuite.Complete, "CoincSuite Recombinations",
                SplitPulses = "TTPulses",
                SplitName   = 'TTrigger',
                FitName     = "LineFit"
               )
tray.AddSegment(linefit.simple,
                fitname       = "LineFit_TT",
                If            =lambda frame: frame['I3EventHeader'].sub_event_stream=='TTrigger',
                inputResponse = 'TTPulses',
               )
tray.AddSegment(lilliput.segments.I3SinglePandelFitter,
                fitname = "SPEFitSingle_TT",
                If      = lambda frame: frame['I3EventHeader'].sub_event_stream=='TTrigger',
                domllh  = "SPE1st",
                pulses  = 'TTPulses',
                seeds   = ["LineFit_TT"],
              )
tray.AddSegment(lilliput.segments.I3IterativePandelFitter,
                fitname      = "SPEFit4_TT",
                If           = lambda frame: frame['I3EventHeader'].sub_event_stream=='TTrigger',
                domllh       = "SPE1st",
                n_iterations = 4,
                pulses       = 'TTPulses',
                seeds        = ["SPEFitSingle_TT"],
               )
tray.AddSegment(lilliput.segments.I3SinglePandelFitter,
                fitname = "MPEFit_TT",
                If      = lambda frame: frame['I3EventHeader'].sub_event_stream=='TTrigger',
                domllh  = "MPE",
                pulses  = 'TTPulses',
                seeds   = ["SPEFit4_TT"],
               )
tray.AddModule(cut_bad_fits)
tray.AddModule("I3Writer","writer",
               streams = [icetray.I3Frame.DAQ,
                          icetray.I3Frame.Physics, 
                          icetray.I3Frame.Geometry, 
                          icetray.I3Frame.Calibration, 
                          icetray.I3Frame.DetectorStatus
                         ],
               filename = outfile,
              )
tray.AddModule("TrashCan","trashcan")
if (options.nFrames==0):
  tray.Execute()
else:
  tray.Execute(options.nFrames)
tray.Finish()
print(time.time()-t0)
os.remove(tmpfile)
