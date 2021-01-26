#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py2-v2/icetray-start
#METAPROJECT /data/ana/SterileNeutrino/IC86/HighEnergy/MC/Metaprojects/icerec.XLevel/build/icerec.XLevel

##METAPROJECT /data/ana/SterileNeutrino/IC86/HighEnergy/MC/Metaprojects/icerec.XLevel.Noise/build/

import time, sys, math, os.path,subprocess, os
from optparse import OptionParser
from shutil import copyfile
from os.path import expandvars
import numpy as np

from I3Tray import *
from icecube import icetray, dataio, dataclasses, STTools, MuonInjector
from icecube import phys_services, DomTools, simclasses, VHESelfVeto
from icecube import lilliput, gulliver, gulliver_modules, paraboloid
from icecube import linefit, MuonGun, WaveCalibrator,wavedeform
from icecube import photonics_service
from icecube import RandomStuff
from icecube.STTools.seededRT.configuration_services import I3DOMLinkSeededRTConfigurationService
from icecube import TopologicalSplitter
import icecube.lilliput.segments
from icecube import tableio, hdfwriter
from icecube import MuonGun
from icecube.icetray import I3Units
from icecube.common_variables import direct_hits
from icecube.common_variables import hit_multiplicity
from icecube.common_variables import track_characteristics

from rename_out_vars import RenameOutVars
from get_pulse_names import get_pulse_names
from initialize_args import initialize_parser
from is_lowup import IsLowUp
from renameMCTree import renameMCTree
from hasTWSRTOfflinePulses import hasTWSRTOfflinePulses
from fixWeightMap import fixWeightMap
from dumbOMSelection import dumbOMSelection
from ComputeChargeWeightedDist import ComputeChargeWeightedDist
from isMuonFilter import IsMuonFilter
from splitFrames import splitFrames
from afterpulses import afterpulses
from precut import precut
from basicRecosAlreadyDone import basicRecosAlreadyDone
from doExpensiveRecos import doExpensiveRecos
from add_basic_reconstructions import add_basic_reconstructions
from add_bayesian_reconstruction import add_bayesian_reconstruction
from add_paraboloid import add_paraboloid
from add_split_reconstructions import add_split_reconstructions
from SamePulseChecker import SamePulseChecker
from computeSimpleCutVars import computeSimpleCutVars
from controls import process_params

deepCoreStrings = process_params()['deepCoreStrings']
stConfigService = process_params()['stConfigService']
i3streams       = process_params()['i3streams']

load("bayesian-priors")
load("double-muon")
load("libmue")
load('MCParticleExtractor')

start_time = time.time()
print("Starting ...")
options,args = initialize_parser()
gcdfile = '/data/ana/SterileNeutrino/IC86/HighEnergy/MC/Systematics/Noise/GeoCalibDetectorStatus_AVG_Fit_55697-57531_SPE_PASS2_Raw.i3.gz'

infile          = options.infile
outfile         = options.outfile
osg             = options.osg

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
        outfile = options.outfile
        spline_path = "/data/ana/SterileNeutrino/IC86/HighEnergy/scripts/jobs/paraboloidCorrectionSpline.dat"

#====================================
InIcePulses, SRTInIcePulses, SRTInIcePulses_NoDC_Qtot, SRTInIcePulses_NoDC = get_pulse_names(infile)
#====================================
tray = I3Tray()
tray.AddService("I3GSLRandomServiceFactory","Random") # needed for bootstrapping
tray.AddModule("I3Reader","reader")(
                ("FilenameList",infiles)
                )

exitStatus=RandomStuff.ExitStatus()

tray.AddModule(renameMCTree, "_renameMCTree", Streams=[icetray.I3Frame.DAQ])

tray.AddModule(IsLowUp & ~IsMuonFilter & hasTWSRTOfflinePulses,"selectValidData")
tray.AddModule(fixWeightMap,"patchCorsikaWeights")

truecondition=lambda frame: True

#======================================
# Compute precut variables and do precut
tray.AddModule(dumbOMSelection,"NoDeepCore",
        pulses                  = SRTInIcePulses,
        output                  = SRTInIcePulses_NoDC,
        omittedStrings  = deepCoreStrings,
        IfCond                  = truecondition
        )

tray.AddModule(ComputeChargeWeightedDist,"CCWD",Pulses=SRTInIcePulses_NoDC,Track="PoleMPEFitName")

tray.AddModule(precut,"precut")
tray.AddModule("I3OrphanQDropper","OrphanQDropper")
#======================================
# Run TTrigger and do reconstructions

tray.AddModule("I3SeededRTCleaning_RecoPulse_Module", "SRTClean",
        InputHitSeriesMapName  = InIcePulses,
        OutputHitSeriesMapName = SRTInIcePulses,
        STConfigService        = stConfigService,
        #SeedProcedure         = "HLCCoreHits",
        NHitsThreshold         = 2,
        Streams                = [icetray.I3Frame.DAQ]
        )

tray.AddModule("I3TopologicalSplitter","TTrigger",
        SubEventStreamName              = "TTrigger", #Spencer -- Is this ok?? I was getting warnigngs...
        InputName                               = SRTInIcePulses,
        OutputName                              = "TTPulses",
        Multiplicity                    = 4,
        TimeWindow                              = 4000*I3Units.ns,
        TimeCone                                = 800*I3Units.ns,
        SaveSplitCount                  = True
        )

tray.AddModule("AfterPulseSpotter","Afterpulses")(
        ("StreamName","TTrigger"),
        ("Pulses","TTPulses")
        )

tray.AddModule(SamePulseChecker,"SPC")

add_basic_reconstructions(tray,"_TT","TTPulses",splitFrames & ~afterpulses & ~basicRecosAlreadyDone)

#======================================
# Compute some simple cut variables
computeSimpleCutVars(tray,splitFrames & ~afterpulses)

#======================================
# Compute some expensive cut variables
add_bayesian_reconstruction(tray,"TTPulses",splitFrames & ~afterpulses & doExpensiveRecos,"TrackFit")
add_paraboloid(tray,"TTPulses",splitFrames & ~afterpulses & doExpensiveRecos,"TrackFit")
add_split_reconstructions(tray,"TTPulses",splitFrames & ~afterpulses & doExpensiveRecos,"TrackFit")

#======================================
# Write output

tray.AddModule("ParaboloidSigmaCorrector","extractSigma")(
                ("CorrectionSplinePath",spline_path),
                ("ParaboloidParameters","TrackFitParaboloidFitParams"),
                ("NChanSource",'NChanSource'), # with DeepCore!
                ("Output","CorrectedParaboloidSigma"),)

tray.Add(RenameOutVars)

#i3streams = [icetray.I3Frame.DAQ,icetray.I3Frame.Physics,icetray.I3Frame.TrayInfo, icetray.I3Frame.Simulation]

outfile = options.outfile
outputKeys = ["GenerationSpec",'MuEx']

if options.move == 'True':
        tray.AddModule("I3Writer","i3writer")(
                ("Filename",outfile_temp),
                ("Streams",i3streams)
                )
        if options.cut == 'True':
                tray.AddModule(tableio.I3TableWriter, "hdfwriter")(
                        ("tableservice",hdfwriter.I3HDFTableService(outfile_temp.replace('.i3.bz2','_golden.h5'))),
                        ("SubEventStreams",["TTrigger"]),
                        ("keys",outputKeys)
                        )
        else:
                pass
else:
        if osg =='True':
                print('You need options.move to be True if using the OSG')
        else:
                tray.AddModule("I3Writer","i3writer")(
                        ("Filename",outfile),
                        ("Streams",i3streams)
                        )
                if options.cut == 'True':
                        tray.AddModule(tableio.I3TableWriter, "hdfwriter")(
                                ("tableservice",hdfwriter.I3HDFTableService(outfile_temp.replace('.i3.bz2','_golden.h5'))),
                                ("SubEventStreams",["TTrigger"]),
                                ("keys",outputKeys)
                                )
                else:
                        pass

if(options.nFrames==0):
        tray.Execute()
else:
        tray.Execute(options.nFrames)
tray.Finish()

# If the file finished processing, move it to the storage location.

if options.move == 'True':
        if osg == "True":
                copy_to_NPX('gsiftp://gridftp.icecube.wisc.edu' + outfile)
                if options.cut == 'True':
                        copy_to_NPX('gsiftp://gridftp.icecube.wisc.edu' + outfile.replace('.i3.bz2','_golden.h5'))
        else:
                os.system(str("mv "+str(outfile_temp) + " " +str(outfile)))
                if options.cut == 'True':
                        os.system(str("mv "+str(outfile_temp.replace('.i3.bz2','_golden.h5')) + " " +str(outfile.replace('.i3.bz2','_golden.h5'))))
else:
        if osg =="True":
                print('You need options.move to be True if using the OSG')
        pass

end_time = time.time()
print("Processing time: "+str(end_time-start_time))

exit(exitStatus.status)


