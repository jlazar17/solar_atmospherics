#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py2-v2/icetray-start
#METAPROJECT /data/ana/SterileNeutrino/IC86/HighEnergy/MC/Metaprojects/icerec.XLevel/build/icerec.XLevel

##METAPROJECT /data/ana/SterileNeutrino/IC86/HighEnergy/MC/Metaprojects/icerec.XLevel.Noise/build/

import sys 
import os
from os.path import expandvars
cwd = os.getcwd()

moduledir= '/data/user/jlazar/solar_atmospherics/processing/processing_modules/'
if moduledir not in sys.path:
    sys.path.append(moduledir)

from I3Tray import I3Tray, load
from icecube import RandomStuff, tableio, hdfwriter, icetray, dataclasses
from icecube import wavedeform, TopologicalSplitter,WaveCalibrator, VHESelfVeto
from icecube.icetray import I3Units

from get_pulse_names import get_pulse_names
from is_lowup import IsLowUp
from isMuonFilter import IsMuonFilter
from overburden import overburden
from outer_charge import outer_charge
from rename_out_vars import RenameOutVars
#from is_simulation import is_simulation
from compute_hit_statistics import ComputeHitStatistics
from interaction_type import interaction_type
from hasTWSRTOfflinePulses import hasTWSRTOfflinePulses
from getWeightingCandidate import getWeightingCandidate
from finalNeutrino import finalNeutrino
from doExpensiveRecos import doExpensiveRecos
from precut import precut
from fixWeightMap import fixWeightMap
from get_cut_variables import get_cut_variables
from get_pulses import get_pulses
from add_split_reconstructions import add_split_reconstructions
from add_bayesian_reconstruction import add_bayesian_reconstruction
from add_basic_reconstructions import add_basic_reconstructions
from SamePulseChecker import SamePulseChecker
from EntryEnergy import EntryEnergy
from splitFrames import splitFrames
from basicRecosAlreadyDone import basicRecosAlreadyDone
from computeSimpleCutVars import computeSimpleCutVars
from cutL3 import cutL3
from FindDetectorVolumeIntersections import FindDetectorVolumeIntersections
from parabaloidCut import parabaloidCut
from afterpulses import afterpulses
from add_paraboloid import add_paraboloid
from planL3Cut import planL3Cut
from is_cut_time import is_cut_time
from true_trackfit import true_trackfit
from goodFit import goodFit
from findHighChargeDOMs import findHighChargeDOMs
from renameMCTree import renameMCTree
from dumbOMSelection import dumbOMSelection
from ComputeChargeWeightedDist import ComputeChargeWeightedDist
from final_selection import finalSample
from controls import process_params
i3streams = process_params()['i3streams']
dh_definitions = process_params()['dh_definitions']
stConfigService = process_params()['stConfigService']
deepCoreStrings = process_params()['deepCoreStrings']

load("bayesian-priors")
load("double-muon")
load("libmue")
load('MCParticleExtractor')

from helper_functions import check_write_permissions, parse_boolean, truecondition

from initialize_args import initialize_parser
options, args = initialize_parser()

###### Get the right ice model ######
ice_model = options.ice_model
if ice_model == 'spice_3.2':
    ice_model_location = expandvars("$I3_BUILD/mue/resources/ice/spice_3.2")
else:
    print('Invalid Ice model')
    sys.exit()

###### Set up all the files ######

if not callable(options.outfile): # this means an explicit path is made
    outfile      = options.outfile
else:
    outfile = options.outfile(options.infile)
###### Make sure we can actually write before doing things ######
if not check_write_permissions(outfile):
    print('You do not have write permission for outdir')
    sys.exit()
spline_path  = "/data/ana/SterileNeutrino/IC86/HighEnergy/scripts/jobs/paraboloidCorrectionSpline.dat"
infile       = options.infile
gcdfile      = '/data/ana/SterileNeutrino/IC86/HighEnergy/MC/Systematics/Noise/GeoCalibDetectorStatus_AVG_Fit_55697-57531_SPE_PASS2_Raw.i3.gz' # I do not understand why exactly this is happenin. TODO ask Spencer
infiles      = [gcdfile, infile]

InIcePulses, SRTInIcePulses, SRTInIcePulses_NoDC_Qtot, SRTInIcePulses_NoDC = get_pulse_names(infile)

###### Buid the tray ######

tray = I3Tray()
tray.AddService("I3GSLRandomServiceFactory","Random") # needed for bootstrapping
tray.AddModule("I3Reader","reader")(("FilenameList",infiles))

exitStatus=RandomStuff.ExitStatus()

tray.AddModule(renameMCTree, "_renameMCTree", Streams=[icetray.I3Frame.DAQ])
tray.AddModule(IsLowUp & ~IsMuonFilter & hasTWSRTOfflinePulses, "selectValidData") # Mine
tray.AddModule(fixWeightMap,"patchCorsikaWeights")
tray.AddModule(dumbOMSelection,"NoDeepCore",
               pulses         = SRTInIcePulses,
               output         = SRTInIcePulses_NoDC,
               omittedStrings = deepCoreStrings,
               IfCond         = truecondition
              )
tray.AddModule(ComputeChargeWeightedDist,"CCWD",Pulses=SRTInIcePulses_NoDC,Track="PoleMPEFitName")
tray.AddModule(precut,"precut")
tray.AddModule("I3OrphanQDropper","OrphanQDropper")
tray.AddModule("I3SeededRTCleaning_RecoPulse_Module", "SRTClean",
               InputHitSeriesMapName  = InIcePulses,
               OutputHitSeriesMapName = SRTInIcePulses,
               STConfigService        = stConfigService,
               #SeedProcedure         = "HLCCoreHits",
               NHitsThreshold         = 2,
               Streams                = [icetray.I3Frame.DAQ]
              )
tray.AddModule("I3TopologicalSplitter","TTrigger",
        SubEventStreamName = "TTrigger", #Spencer -- Is this ok?? I was getting warnigngs... Jeff: Is it ?
        InputName          = SRTInIcePulses,
        OutputName         = "TTPulses",
        Multiplicity       = 4,
        TimeWindow         = 4000*I3Units.ns,
        TimeCone           = 800*I3Units.ns,
        SaveSplitCount     = True
        )
tray.AddModule("AfterPulseSpotter","Afterpulses")(
                      ("StreamName","TTrigger"),
                      ("Pulses","TTPulses")
                     )
tray.AddModule(SamePulseChecker,"SPC")
add_basic_reconstructions(tray,"_TT","TTPulses",splitFrames & ~afterpulses & ~basicRecosAlreadyDone)
computeSimpleCutVars(tray,splitFrames & ~afterpulses)
add_bayesian_reconstruction(tray,"TTPulses",splitFrames & ~afterpulses & doExpensiveRecos,"TrackFit")
add_paraboloid(tray,"TTPulses",splitFrames & ~afterpulses & doExpensiveRecos,"TrackFit")
add_split_reconstructions(tray,"TTPulses",splitFrames & ~afterpulses & doExpensiveRecos,"TrackFit")
tray.AddModule("ParaboloidSigmaCorrector","extractSigma")(
                     ("CorrectionSplinePath",spline_path),
                     ("ParaboloidParameters","TrackFitParaboloidFitParams"),
                     ("NChanSource",'NChanSource'), # with DeepCore!
                     ("Output","CorrectedParaboloidSigma")
                    )
tray.Add(RenameOutVars)
tray.AddModule("I3Writer","i3writer")(
                    ("Filename",outfile),
                    ("Streams",i3streams)
                   )


if(options.nFrames==0):
        tray.Execute()
else:
        tray.Execute(options.nFrames)
tray.Finish()
