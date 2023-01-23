from I3Tray import *
import solar_atmospherics
from solar_atmospherics.modules import get_pulse_names, cut_bad_fits, cut_high_energy, is_lowup_filter, is_muon_filter, rename_MC_tree, has_TWSRT_offline_pulses, fix_weight_map
from modules import hit_statistics_cut, fit_cut, PacketCutter

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
        "--no_cut",
        dest="no_cut",
        action="store_true",
        #default=False
        default=True
    )
    args = parser.parse_args()
    return args

def main(
    infile,
    outfile,
    gcd,
    n=-1,
    cut=True,
    z_travel=-10,
    cog_z_vertex=110,
    cog_z_sigma=110,
    rlogl = 22,
    zenith_min = 1.4835, # 85 degrees
    zenith_max = 2.4435 # 140 degrees
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
    if filetype=='genie':
        tray.AddModule(cut_high_energy)
    tray.AddModule(
        rename_MC_tree,
        "_renameMCTree",
        Streams=[icetray.I3Frame.DAQ]
    )
    tray.AddModule(
        is_lowup_filter & ~is_muon_filter & has_TWSRT_offline_pulses,
        "selectValidData"
    )
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
        TimeWindow = 2000, #Default=4000 ns
        XYDist = 300, 
        ZDomDist = 15, 
        TimeCone = 1000, #Default=1000 ns
        SaveSplitCount = True
    )
    tray.AddSegment(
        CoincSuite.Complete, "CoincSuite Recombinations",
        SplitPulses = "TTPulses",
        SplitName = 'TTrigger',
        FitName = "LineFit"
    )
    tray.AddSegment(
        hit_statistics.I3HitStatisticsCalculatorSegment,
        'HitStatistics',
        PulseSeriesMapName = 'TTPulses',
        OutputI3HitStatisticsValuesName = 'TTPulses_HitStatistics',
        BookIt = False,
        If=lambda frame: frame['I3EventHeader'].sub_event_stream=='TTrigger',
    )
    #tray.AddModule('Delete', 'delkeys', Keys = ["I3DetectorStatus", "I3Geometry", "I3Calibration"])
    if cut:
        tray.AddModule(
            PacketCutter,
            "Stats_Cutter",
            cut = hit_statistics_cut,
            #z_travel = z_travel,
            #cog_z_vertex = cog_z_vertex,
            #cog_z_sigma = cog_z_sigma
            cutkawrgs={
                "z_travel" : z_travel,
                "cog_z_vertex" : cog_z_vertex,
                "cog_z_sigma" : cog_z_sigma
            }
        )
    #class ExampleMod(icetray.I3PacketModule):
    #    def __init__(self, context):
    #        print("Initializing ExampleMod")
    #        super(ExampleMod, self).__init__(context, icetray.I3Frame.DAQ)

    #    def FramePacket(self, frames):
    #        print("Adding NSplits")
    #        i = icetray.I3Int(len(frames) - 1)
    #        frames[0].Put('NSplits', i)
    #        for fr in frames:
    #            self.PushFrame(fr)
    #tray.AddModule(ExampleMod, 'mod')
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
    if cut:
        tray.AddModule(
            PacketCutter,
            "Fit_Cutter",
            #fit_cut,
            #rlogl = rlogl,
            #zenith_min = zenith_min,
            #zenith_max = zenith_max
        )
    tray.AddModule(
        "I3Writer","writer",
         streams = [
            icetray.I3Frame.DAQ,
            icetray.I3Frame.Physics, 
            #icetray.I3Frame.Geometry, 
            #icetray.I3Frame.Calibration, 
            #icetray.I3Frame.DetectorStatus
         ],
         filename = outfile,
    )
    tray.AddModule("TrashCan","trashcan")
    if n < 0:
      tray.Execute()
    else:
      tray.Execute(n)
    tray.Finish()

if __name__=="__main__":
    #from memory_profiler import memory_usage
    #from solar_atmospherics.event_selection.utils import make_outfile_name, figure_out_gcd

    from solar_atmospherics.modules import figure_out_gcd
    from solar_atmospherics.event_selection.l3_a.make_outfile_name import make_outfile_name    

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

    # Determine what kind of data we are processing
    if 'corsika' in infiles[0]:
        filetype = 'corsika'
    elif 'genie' in infiles[0]:
        filetype = 'genie'
    elif 'nancy' in infiles[0]:
        filetype = 'nancy'
    elif 'exp' in infiles[0]:
        filetype = 'exp_data'

    #  Determine the outfile name
    if not args.outfile:
        #outfiles = [make_outfile_name(i, outdir=args.outdir, prefix="Level3a_", strip="Level2_") for i in infiles]
        outfiles = [make_outfile_name(i, outdir=args.outdir) for i in infiles]
    else:
        outfiles = args.outfile
    outfiles = [o.replace('JLevel', 'JLevel_%s' % filetype) for o in outfiles]
    slc = slice(None, None, args.thin)
    infiles = infiles[slc]
    outfiles = outfiles[slc]
    gcds = gcds[slc]
    if not args.profile:
        from os.path import exists
        for inf, outf, gcd in zip(infiles, outfiles, gcds):
            print(inf)
            if not exists(outf):
                print("the file does NOT exist")
                main(inf,outf, gcd, cut=not args.no_cut)
            elif args.force_recalc:
                print("The file exists but we are recalculating it")
                main(inf,  outf, gcd, cut=not args.no_cut)
            else:
                print("The file exists and we are NOT recalculating it")
                pass
    else:
        def f():
            from time import time
            t0 = time()
            global infiles
            global outfiles
            global gcds
            for inf, outf, gcd in zip(infiles, outfiles, gcds):
                main(inf,  outf, gcd)
            t1 = time()
        print(t1-t0)
        #mem_usage = memory_usage(f)
        print('Maximum memory usage: %s' % max(mem_usage))

