import sys, os, time
from optparse import OptionParser
import numpy as np
sys.path.append('/data/user/jvillarreal/sa_git/')
sys.path.append('/data/user/jlazar/solar/')

from glob import glob
from I3Tray import *
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

from solar_atmospherics.modules import figure_out_gcd, l3b_cuts
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

options, args = initialize_parser()
infile        = options.infile

if 'corsika' in infile:
    filetype = 'corsika'
elif 'genie' in infile:
    filetype = 'genie'
elif 'nancy' in infile:
    filetype = 'nancy'
elif 'exp' in infile:
    filetype = 'exp_data'
    
if options.gcdfile=='':
    gcdfile = figure_out_gcd(infile)
else:
    gcdfile = options.gcdfile
    
if not callable(options.outfile):
    outfile = options.outfile
else:
    outfile = options.outfile(infile)
outfile = outfile.replace('JLevel', 'JLevel_%s' % filetype)
# save tempfile
tmpfile = outfile.replace('.i3.zst', '.npy')
np.save(tmpfile, [])

infiles = [gcdfile, infile]
outfile_temp = '/data/ana/SterileNeutrino/IC86/HighEnergy/MC/scripts/temp/'+outfile.split('/')[-1]
spline_path = "/data/ana/SterileNeutrino/IC86/HighEnergy/scripts/jobs/paraboloidCorrectionSpline.dat"
icetray.set_log_level(icetray.I3LogLevel.LOG_ERROR)
truef=lambda frame: True
#====================================
tray = I3Tray()
tray.AddService("I3GSLRandomServiceFactory","Random") # needed for bootstrapping
tray.AddModule("I3Reader","reader")(
                ("FilenameList",infiles)
                )
tray.AddModule(l3b_cuts)
########### WHAT does this shit do ? #########
seedLikelihood='MPEFit_TT'+"_BayesianLikelihoodSeed"
tray.AddService('I3GulliverIPDFPandelFactory', 'MPEFit_TT'+"_BayesianLikelihoodSeed",
                InputReadout='TTPulses',
                EventType="InfiniteMuon",
                Likelihood="SPE1st",
                PEProb="GaussConvolutedFastApproximation",
                JitterTime=15.*I3Units.ns,
                NoiseProbability=10.*I3Units.hertz
               )
tray.AddService("I3PowExpZenithWeightServiceFactory","ZenithPrior",
                Amplitude=2.49655e-07,
                CosZenithRange=[-1,1],
                DefaultWeight=1.383896526736738e-87,
                ExponentFactor=0.778393,
                FlipTrack=False,
                PenaltySlope=-1000,
                PenaltyValue=-200,
                Power=1.67721
               )
tray.AddService("I3BasicSeedServiceFactory", 'MPEFit_TT'+"_BayesianSeed",
                InputReadout='TTPulses',
                FirstGuesses=['MPEFit_TT'],
                TimeShiftType="TFirst"
               )
tray.AddService("I3EventLogLikelihoodCombinerFactory", 'MPEFit_TT'+"_BayesianLikelihood",
                InputLogLikelihoods=[seedLikelihood,'ZenithPrior']
               )
tray.AddService('I3GulliverMinuitFactory', 'Minuit',
                MinuitPrintLevel = -2,
                FlatnessCheck    = True,
                Algorithm        = 'SIMPLEX',
                MaxIterations    = 2500,
                MinuitStrategy   = 2,
                Tolerance        = 0.001
               )
tray.Add("I3SimpleParametrizationFactory", 'MinuitSimplex',
         StepX=20.*icetray.I3Units.m,
         StepY=20.*icetray.I3Units.m,
         StepZ=20.*icetray.I3Units.m,
         StepZenith=0.1*I3Units.radian,
         StepAzimuth=0.2*I3Units.radian,
         BoundsX=[-2000.*I3Units.m, 2000.*I3Units.m],
         BoundsY=[-2000.*I3Units.m, 2000.*I3Units.m],
         BoundsZ=[-2000.*I3Units.m, 2000.*I3Units.m]
        )
tray.AddModule("I3IterativeFitter",'MPEFit_TT'+"_Bayesian",
               OutputName='MPEFit_TT'+"_Bayesian",
               RandomService="SOBOL",
               NIterations=8,
               SeedService='MPEFit_TT'+"_BayesianSeed",
               Parametrization="MinuitSimplex",
               LogLikelihood='MPEFit_TT'+"_BayesianLikelihood",
               CosZenithRange=[0, 1],
               Minimizer="Minuit",
               If=lambda frame: frame['I3EventHeader'].sub_event_stream=='TTrigger',
              )
##################################################
tray.AddSegment(hit_multiplicity.I3HitMultiplicityCalculatorSegment, 'TTPulses_HitMultiplicity',
                PulseSeriesMapName = 'TTPulses',
                OutputI3HitMultiplicityValuesName = 'TTPulses'+'_HitMultiplicity',
                BookIt = False,
                If=lambda frame: frame['I3EventHeader'].sub_event_stream=='TTrigger',
               )
tray.AddSegment(hit_statistics.I3HitStatisticsCalculatorSegment, 'HitStatistics',
                PulseSeriesMapName = 'TTPulses',
                OutputI3HitStatisticsValuesName = 'TTPulses_HitStatistics',
                BookIt = False,
                If=lambda frame: frame['I3EventHeader'].sub_event_stream=='TTrigger',
               )
### I3DirectHitsDefinitions ### this should move out to wimp globals
dh_definitions = [ 
                  direct_hits.I3DirectHitsDefinition("ClassA", -15*I3Units.ns, +25*I3Units.ns),
                  direct_hits.I3DirectHitsDefinition("ClassB", -15*I3Units.ns, +75*I3Units.ns),
                  direct_hits.I3DirectHitsDefinition("ClassC", -15*I3Units.ns, +150*I3Units.ns),
                  #direct_hits.I3DirectHitsDefinition("ClassD", -float("inf"), -15*I3Units.ns),
                  direct_hits.I3DirectHitsDefinition("ClassE", -15*I3Units.ns, +float("inf")),
                 ]
tray.AddSegment(direct_hits.I3DirectHitsCalculatorSegment, 'DirectHits',
                DirectHitsDefinitionSeries = dh_definitions,
                PulseSeriesMapName = 'TTPulses',
                ParticleName = 'MPEFit_TT',
                OutputI3DirectHitsValuesBaseName = 'MPEFit'+'_DirectHits',
                BookIt = False,
                If=lambda frame: frame['I3EventHeader'].sub_event_stream=='TTrigger',
               )
# Service that I3TruncatedEnergy needs to talk to for energy estimation.
# This service creates a link for tables.
tray.AddService("I3PhotonicsServiceFactory", "PhotonicsServiceMu",
                PhotonicsTopLevelDirectory  = "/cvmfs/icecube.opensciencegrid.org/data/photon-tables/SPICEMie/",
                DriverFileDirectory         = "/cvmfs/icecube.opensciencegrid.org/data/photon-tables/SPICEMie/driverfiles",
                PhotonicsLevel2DriverFile   = "mu_photorec.list",
                PhotonicsTableSelection     = 2,
                ServiceName                 = "PhotonicsServiceMu"
               )
tray.AddModule('I3TruncatedEnergy',
               RecoPulsesName         = 'TTPulses',
               RecoParticleName       = 'MPEFit_TT',
               ResultParticleName     = 'MPEFit_TT'+'_TruncatedEnergy',
               I3PhotonicsServiceName = 'PhotonicsServiceMu',
               UseRDE                 = True,
               If                     = lambda frame: frame['I3EventHeader'].sub_event_stream=='TTrigger',
              )
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
os.remove(tmpfile)
print(time.time()-t0)
