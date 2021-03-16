#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py2-v2/icetray-start
#METAPROJECT /data/ana/SterileNeutrino/IC86/HighEnergy/MC/Metaprojects/icerec.XLevel/build/icerec.XLevel

##METAPROJECT /data/ana/SterileNeutrino/IC86/HighEnergy/MC/Metaprojects/icerec.XLevel.Noise/build/

import sys, os.path,subprocess, os
from optparse import OptionParser
import numpy as np

from I3Tray import *
from icecube import icetray, dataio, dataclasses
from icecube.common_variables import hit_multiplicity, hit_statistics, direct_hits
from icecube.STTools.seededRT.configuration_services import I3DOMLinkSeededRTConfigurationService
#from icecube import icetray, dataio, dataclasses
from icecube import TopologicalSplitter
from icecube import CoincSuite
from icecube import phys_services, DomTools, simclasses, VHESelfVeto
from icecube import lilliput, gulliver, gulliver_modules, paraboloid
from icecube import linefit, MuonGun, WaveCalibrator,wavedeform
from icecube import photonics_service
#from icecube.VariableExtractor import BasicRecos
#from icecube import RandomStuff
from icecube import TopologicalSplitter
import icecube.lilliput.segments
from icecube import tableio, hdfwriter
from icecube.icetray import I3Units
from icecube.common_variables import direct_hits
from icecube.common_variables import hit_multiplicity
from icecube.common_variables import track_characteristics
load('libtruncated_energy')

module_dir = '/data/user/jlazar/solar/solar_atmospherics/processing/processing_modules/'
if module_dir not in sys.path:
    sys.path.append(module_dir)
from cut_high_energy import CutHighEnergy
from get_pulse_names import get_pulse_names
from initialize_args import initialize_parser
from is_lowup import IsLowUp
from renameMCTree import renameMCTree
from hasTWSRTOfflinePulses import hasTWSRTOfflinePulses
from fixWeightMap import fixWeightMap
from isMuonFilter import IsMuonFilter

options,args = initialize_parser()

infile          = options.infile
if 'corsika' in infile:
    filetype     = 'corsika'
else:
    if 'genie' in infile:
        filetype = 'genie'
    else:
        filetype     = 'nancy'
    
if filetype=='nancy':
    gcdfile = '/cvmfs/icecube.opensciencegrid.org/data/GCD/GeoCalibDetectorStatus_AVG_55697-57531_PASS2_SPE_withScaledNoise.i3.gz'
elif filetype=='genie':
    gcdfile = '/cvmfs/icecube.opensciencegrid.org/data/GCD/GeoCalibDetectorStatus_AVG_55697-57531_PASS2_SPE_withScaledNoise.i3.gz'
elif filetype=='corsika':
    gcdfile = '/cvmfs/icecube.opensciencegrid.org/data/GCD/GeoCalibDetectorStatus_AVG_55697-57531_PASS2_SPE_withStdNoise.i3.gz'

    
if not callable(options.outfile):
    outfile = options.outfile
else:
    outfile = options.outfile(infile)
outfile = outfile.replace('JLevel', 'JLevel_%s' % filetype)
# save tempfile
tmpfile = outfile.replace('.i3.zst', '.npy')
np.save(tmpfile, [])
print(tmpfile)

osg = options.osg

if osg == 'True':
    def copy_to_OSG(NPX_file):
        subprocess.check_call(['globus-url-copy','-nodcau','-rst', NPX_file,"file:"+os.getcwd()+'/'+str(NPX_file.split('/')[-1])])

    def copy_to_NPX(NPX_file):
        subprocess.check_call(['globus-url-copy','-nodcau','-rst',"file:"+os.getcwd()+'/'+str(NPX_file.split('/')[-1]), NPX_file])

    gcdfile_NPX = str('gsiftp://gridftp.icecube.wisc.edu' + gcdfile)
    gcdfile = str(os.getcwd()+'/'+gcdfile.split('/')[-1])

    infile_NPX = str('gsiftp://gridftp.icecube.wisc.edu' + infile)
    infile = str(os.getcwd()+'/'+infile.split('/')[-1])

    spline_NPX = "gsiftp://gridftp.icecube.wisc.edu/data/ana/SterileNeutrino/IC86/HighEnergy/scripts/jobs/paraboloidCorrectionSpline.dat"

    copy_to_OSG(gcdfile_NPX)
    copy_to_OSG(infile_NPX)
    copy_to_OSG(spline_NPX)

    infiles = [gcdfile,infile]
    outfile  = str('gsiftp://gridftp.icecube.wisc.edu' + outfile)
    outfile_temp = str(os.getcwd()+'/'+outfile.split('/')[-1])
    '''
    try:
        copy_to_OSG(outfile)
    except:
        print('Outfile does not exsist. Continuing...')
    if os.path.isfile(outfile_temp):
        print('Outfile already processed. Exiting.')
        sys.exit()
    '''

    #outfile_temp = str(os.getcwd()+'/'+outfile.split('/')[-1])

    spline_path =  str(os.getcwd()+'/'+str(spline_NPX).split('/')[-1])
else:

        infiles = [gcdfile, infile]
        outfile_temp = '/data/ana/SterileNeutrino/IC86/HighEnergy/MC/scripts/temp/'+outfile.split('/')[-1]
        spline_path = "/data/ana/SterileNeutrino/IC86/HighEnergy/scripts/jobs/paraboloidCorrectionSpline.dat"

truef=lambda frame: True
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
    tray.AddModule(CutHighEnergy)
tray.AddModule(renameMCTree, "_renameMCTree", Streams=[icetray.I3Frame.DAQ])
tray.AddModule(IsLowUp & ~IsMuonFilter & hasTWSRTOfflinePulses,"selectValidData")
tray.AddModule(fixWeightMap,"patchCorsikaWeights")
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
                SplitName='TTrigger',
                FitName = "LineFit"
               )
tray.AddSegment(linefit.simple,
                fitname="LineFit_masked",
                If=lambda frame: frame['I3EventHeader'].sub_event_stream=='TTrigger',
                inputResponse='TTPulses',
               )
tray.AddSegment(lilliput.segments.I3SinglePandelFitter,
                fitname="SPEFitSingle_masked",
                If=lambda frame: frame['I3EventHeader'].sub_event_stream=='TTrigger',
                domllh="SPE1st",
                pulses='TTPulses',
                seeds=["LineFit_masked"],
              )
tray.AddSegment(lilliput.segments.I3IterativePandelFitter,
                fitname="SPEFit4_masked",
                If=lambda frame: frame['I3EventHeader'].sub_event_stream=='TTrigger',
                domllh="SPE1st",
                n_iterations=4,
                pulses='TTPulses',
                seeds=["SPEFitSingle_masked"],
               )
tray.AddSegment(lilliput.segments.I3SinglePandelFitter,
                fitname="MPEFit_masked",
                If=lambda frame: frame['I3EventHeader'].sub_event_stream=='TTrigger',
                domllh="MPE",
                pulses='TTPulses',
                seeds=["SPEFit4_masked"],
               )
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
                  direct_hits.I3DirectHitsDefinition("ClassD", -float("inf"), -15*I3Units.ns),
                  direct_hits.I3DirectHitsDefinition("ClassE", -15*I3Units.ns, +float("inf")),
                 ]
tray.AddSegment(direct_hits.I3DirectHitsCalculatorSegment, 'DirectHits',
                DirectHitsDefinitionSeries = dh_definitions,
                PulseSeriesMapName = 'TTPulses',
                ParticleName = 'MPEFit_masked',
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
               RecoParticleName       = 'MPEFit_masked',
               ResultParticleName     = 'MPEFit_masked'+'_TruncatedEnergy',
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
