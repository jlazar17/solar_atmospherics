from I3Tray import *
import solar_atmospherics
from utils import (
    HitStatisticsCutter,
    FitCutter,
    get_pulse_names,
    cut_bad_fits,
    cut_high_energy,
    is_lowup_filter,
    is_muon_filter,
    rename_mc_tree,
    has_twsrt_offline_pulses,
    fix_weight_map,
    write_simname,
    write_corsika_set
)

def initialize_parser():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--infile",
        dest="infile",
        nargs="+",
        required=True
    )
    parser.add_argument(
        '-g', '--gcdfile',
        dest='gcdfile',
        nargs="+"
    )
    parser.add_argument(
        "-o", "--outfile",
        dest="outfile",
        nargs="+"
    )
    parser.add_argument(
        "--outdir",
        dest="outdir",
        default=".",
        type=str,
    )
    parser.add_argument(
        '-n', '--nframes',
        dest='n',
        default=-1,
        type=int,
        help='How many frames to do this for. Default do all frames.'
    )
    parser.add_argument(
        "--profile",
        dest="profile",
        type=bool,
        default=False
    )
    parser.add_argument(
        "--force_recalc",
        dest="force_recalc",
        type=bool,
        default=False
    )
    parser.add_argument(
        "--ice_model",
        dest="ice_model",
        default='spice_3.2',
        type=str,
        help='Ignore this'
    )
    parser.add_argument(
        "--thin",
        dest="thin",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--l3_a",
        dest="l3_a",
        action="store_true",
        default=False
    )
    parser.add_argument(
        "--l3_b",
        dest="l3_b",
        action="store_true",
        default=False
    )
    parser.add_argument(
        "--no_cut",
        dest="no_cut",
        action = "store_true",
        default=False
    )
    args = parser.parse_args()
    return args

def main(
    infile,
    outfile,
    gcd,
    **kwargs
):
    from icecube import icetray, dataio, dataclasses
    from icecube.common_variables import hit_multiplicity, hit_statistics, direct_hits
    from icecube.STTools.seededRT.configuration_services import I3DOMLinkSeededRTConfigurationService
    from icecube import TopologicalSplitter
    from icecube import CoincSuite
    from icecube import phys_services, DomTools, simclasses, VHESelfVeto
    from icecube import lilliput, gulliver, gulliver_modules, paraboloid
    from icecube import linefit, MuonGun, WaveCalibrator, wavedeform
    from icecube import photonics_service
    import icecube.lilliput.segments
    from icecube import tableio, hdfwriter
    from icecube.icetray import I3Units
    load('libtruncated_energy')
    load("bayesian-priors")
    infile_gcd = [gcd, infile]
    # save tempfile
    icetray.set_log_level(icetray.I3LogLevel.LOG_ERROR)
    #====================================
    InIcePulses, SRTInIcePulses, SRTInIcePulses_NoDC_Qtot, SRTInIcePulses_NoDC = get_pulse_names(infile)
    #====================================
    tray = I3Tray()
    tray.AddService("I3GSLRandomServiceFactory","Random") # needed for bootstrapping
    tray.AddModule("I3Reader","reader")(("FilenameList", infile_gcd))
    # Remove high energy portion from GENIE simulation to make sure simulation is non-overlapping
    if kwargs["simname"]=='genie':
        tray.AddModule(cut_high_energy)
    tray.AddModule(
        rename_mc_tree,
        "_renameMCTree",
        Streams=[icetray.I3Frame.DAQ]
    )
    tray.AddModule(
        is_lowup_filter & ~is_muon_filter & has_twsrt_offline_pulses,
        "selectValidData"
    )
    if kwargs["l3_a"]:
        tray.AddModule(fix_weight_map,"patchCorsikaWeights")
        tray.AddModule("I3OrphanQDropper","OrphanQDropper")
        #======================================
        stConfigService = I3DOMLinkSeededRTConfigurationService(
            allowSelfCoincidence = False, # Default: False.
            useDustlayerCorrection  = True, # Default: True.
            dustlayerUpperZBoundary =  0 * I3Units.m, # Default: 0m.
            dustlayerLowerZBoundary = -150 * I3Units.m, # Default: -150m.
            ic_ic_RTTime = 1000 * I3Units.ns, # Default: 1000m.
            ic_ic_RTRadius = 150 * I3Units.m, # Default: 150m.
        )
        tray.AddModule(
            "I3SeededRTCleaning_RecoPulse_Module", "SRTClean",
            InputHitSeriesMapName = InIcePulses,
            OutputHitSeriesMapName = SRTInIcePulses,
            STConfigService = stConfigService,
            #SeedProcedure = "HLCCoreHits",
            NHitsThreshold = 2,
            Streams = [icetray.I3Frame.DAQ]
        )
        tray.AddModule(
            "I3TopologicalSplitter", "TTrigger",
            SubEventStreamName = 'TTrigger',
            InputName = "SRTInIcePulses",
            OutputName = "TTPulses",
            Multiplicity = 4,
            TimeWindow = 2000,
            XYDist = 300,
            ZDomDist = 15,
            TimeCone = 1000,
            SaveSplitCount = True
        )
        tray.AddSegment(
            CoincSuite.Complete, "CoincSuite Recombinations",
            SplitPulses = "TTPulses",
            SplitName = 'TTrigger',
            FitName = "LineFit"
        )
        tray.AddModule(
            write_simname,
            simname = kwargs["simname"]
        )
        if kwargs["corsika_set"] > 0:
            tray.AddModule(
                write_corsika_set,
                corsika_set = kwargs["corsika_set"]
            )
        tray.AddSegment(
            hit_statistics.I3HitStatisticsCalculatorSegment,
            'HitStatistics',
            PulseSeriesMapName = 'TTPulses',
            OutputI3HitStatisticsValuesName = 'TTPulses_HitStatistics',
            BookIt = False,
            If=lambda frame: frame['I3EventHeader'].sub_event_stream=='TTrigger',
        )
        if kwargs["cut"]:
            tray.AddModule(
                HitStatisticsCutter,
                "Stats_Cutter",
                z_travel = kwargs["z_travel"],
                cog_z_vertex = kwargs["cog_z_vertex"],
                cog_z_sigma = kwargs["cog_z_sigma"]
            )
        tray.AddSegment(
            hit_multiplicity.I3HitMultiplicityCalculatorSegment,
            'TTPulses_HitMultiplicity',
            PulseSeriesMapName = 'TTPulses',
            OutputI3HitMultiplicityValuesName = 'TTPulses'+'_HitMultiplicity',
            BookIt = False,
            If=lambda frame: frame['I3EventHeader'].sub_event_stream=='TTrigger',
        )
        tray.AddSegment(
            linefit.simple,
            fitname = "LineFit_TT",
            If = lambda frame: frame['I3EventHeader'].sub_event_stream=='TTrigger',
            inputResponse = 'TTPulses',
        )
        tray.AddSegment(
            lilliput.segments.I3SinglePandelFitter,
            fitname = "SPEFitSingle_TT",
            If = lambda frame: frame['I3EventHeader'].sub_event_stream=='TTrigger',
            domllh = "SPE1st",
            pulses = 'TTPulses',
            seeds = ["LineFit_TT"],
        )
        tray.AddSegment(
            lilliput.segments.I3IterativePandelFitter,
            fitname = "SPEFit4_TT",
            If = lambda frame: frame['I3EventHeader'].sub_event_stream=='TTrigger',
            domllh = "SPE1st",
            n_iterations = 4,
            pulses = 'TTPulses',
            seeds = ["SPEFitSingle_TT"],
        )
        tray.AddSegment(
            lilliput.segments.I3SinglePandelFitter,
            fitname = "MPEFit_TT",
            If = lambda frame: frame['I3EventHeader'].sub_event_stream=='TTrigger',
            domllh = "MPE",
            pulses = 'TTPulses',
            seeds = ["SPEFit4_TT"],
        )
        if kwargs["cut"]:
            tray.AddModule(
                FitCutter,
                "Fit_Cutter",
                rlogl = kwargs["rlogl"],
                zenith_min = kwargs["zenith_min"],
                zenith_max = kwargs["zenith_max"]
            )
    if kwargs["l3_b"]:

        seed_likelihood='MPEFit_TT'+"_BayesianLikelihoodSeed"
        tray.AddService(
            'I3GulliverIPDFPandelFactory',
            seed_likelihood,
            InputReadout='TTPulses',
            EventType="InfiniteMuon",
            Likelihood="SPE1st",
            PEProb="GaussConvolutedFastApproximation",
            JitterTime=15.*I3Units.ns,
            NoiseProbability=10.*I3Units.hertz
        )
        tray.AddService(
            "I3PowExpZenithWeightServiceFactory",
            "ZenithPrior",
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
        tray.AddModule(
            "I3IterativeFitter",
            'MPEFit_TT'+"_Bayesian",
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
        #tray.AddSegment(
        #    hit_multiplicity.I3HitMultiplicityCalculatorSegment,
        #    'TTPulses_HitMultiplicity',
        #    PulseSeriesMapName = 'TTPulses',
        #    OutputI3HitMultiplicityValuesName = 'TTPulses'+'_HitMultiplicity',
        #    BookIt = False,
        #    If=lambda frame: frame['I3EventHeader'].sub_event_stream=='TTrigger',
        #)
        #tray.AddSegment(
        #    hit_statistics.I3HitStatisticsCalculatorSegment,
        #    'HitStatistics',
        #    PulseSeriesMapName = 'TTPulses',
        #    OutputI3HitStatisticsValuesName = 'TTPulses_HitStatistics',
        #    BookIt = False,
        #    If=lambda frame: frame['I3EventHeader'].sub_event_stream=='TTrigger',
        #)
        ### I3DirectHitsDefinitions ### this should move out to wimp globals
        dh_definitions = [ 
            direct_hits.I3DirectHitsDefinition("ClassA", -15*I3Units.ns, +25*I3Units.ns),
            direct_hits.I3DirectHitsDefinition("ClassB", -15*I3Units.ns, +75*I3Units.ns),
            direct_hits.I3DirectHitsDefinition("ClassC", -15*I3Units.ns, +150*I3Units.ns),
            #direct_hits.I3DirectHitsDefinition("ClassD", -float("inf"), -15*I3Units.ns),
            direct_hits.I3DirectHitsDefinition("ClassE", -15*I3Units.ns, +float("inf")),
                         ]
        tray.AddSegment(
            direct_hits.I3DirectHitsCalculatorSegment,
            'DirectHits',
            DirectHitsDefinitionSeries = dh_definitions,
            PulseSeriesMapName = 'TTPulses',
            ParticleName = 'MPEFit_TT',
            OutputI3DirectHitsValuesBaseName = 'MPEFit'+'_DirectHits',
            BookIt = False,
            If=lambda frame: frame['I3EventHeader'].sub_event_stream=='TTrigger',
        )
    tray.AddModule(
        "I3Writer","writer",
         streams = [
            icetray.I3Frame.DAQ,
            icetray.I3Frame.Physics, 
         ],
         filename = outfile,
    )
    tray.AddModule("TrashCan","trashcan")
    if kwargs["n"] < 0:
      tray.Execute()
    else:
      tray.Execute(n)
    tray.Finish()

if __name__=="__main__":
    from solar_atmospherics.event_selection.utils import make_outfile_name, figure_out_gcd
    args = initialize_parser()

    # Get a list of infiles
    infiles = args.infile


    # Construct a list of all GCD fils
    if not args.gcdfile:
        gcds = [figure_out_gcd(i) for i in infiles]
    elif len(args.gcdfile)==len(infiles):
        gcds = args.gcdfile
    else:
        raise ValueError("Number of provided GCDs does not match number of infiles")

    #  Determine the outfile name
    if not args.outfile:
        outfiles = [make_outfile_name(i, outdir=args.outdir, prefix="Level3_a_", strip="Level2_") for i in infiles]
    else:
        outfiles = args.outfile

    #outfiles = [o.replace('JLevel', 'JLevel_%s' % simname) for o in outfiles]
    slc = slice(None, None, args.thin)
    infiles = infiles[slc]
    outfiles = outfiles[slc]
    gcds = gcds[slc]

    # Determine what kind of data we are processing
    if 'corsika' in infiles[0]:
        simname = 'corsika'
    elif 'genie' in infiles[0]:
        simname = 'genie'
    elif 'nancy' in infiles[0]:
        simname = 'nancy'
    elif 'exp' in infiles[0]:
        simname = 'exp_data'

    if simname=="corsika":
        from utils import determine_corsika
        corsika_sets = [determine_corsika(f) for f in infiles]
    else:
        import numpy as np
        corsika_sets = np.full(len(infiles), -1)

    # TODO get rid of this kwargs bullshit
    kwargs = {
        "l3_a" : args.l3_a,
        "l3_b" : args.l3_b,
        "cut" : not args.no_cut,
        "n" : args.n,
        "z_travel" : -10,
        "cog_z_sigma" : 110,
        "cog_z_vertex" : 110,
        "rlogl" : 22,
        "zenith_min" : 1.4835,
        "zenith_max" : 2.4435,
        "simname" : simname
    }

    if not args.profile:
        from os.path import exists
        for inf, outf, gcd, corsika_set in zip(
            infiles,
            outfiles,
            gcds,
            corsika_sets
        ):
            print(inf, outf)
            kwargs["corsika_set"] = corsika_set
            if not exists(outf):
                main(inf, outf, gcd, **kwargs)
            elif args.force_recalc:
                main(inf, outf, gcd, **kwargs)
            else:
                pass
    else:
        from memory_profiler import memory_usage
        def f():
            from time import time
            t0 = time()
            global infiles
            global outfiles
            global gcds
            for inf, outf, gcd in zip(infiles, outfiles, gcds):
                main(inf,  outf, gcd, **kwargs)
            t1 = time()
            print(t1-t0)
        mem_usage = memory_usage(f)
        print('Maximum memory usage: %s' % max(mem_usage))
