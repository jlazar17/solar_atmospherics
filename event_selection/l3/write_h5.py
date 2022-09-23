def make_outfile_name(infile):
    outfile = infile.replace('i3.zst', 'h5').replace('i3', 'h5')
    return outfile

def initialize_parser():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-n',
        '--n_frames', 
        dest='n_frames',
        default=0, 
        type=int, 
        help='How many frames to do this for. Default do all frames.'
    )
    parser.add_argument(
        "-i",
        dest = "infiles",
        nargs = "+",
    )
    parser.add_argument(
        "-o",
        dest = "outfiles",
        nargs = "+"
    )
    parser.add_argument(
        "--outdir",
        dest = "outdir",
        type = str,
        default = "./"
    )
    parser.add_argument(
        "--outkeys",
        dest = "outkeys",
        nargs = "+"
    )
    parser.add_argument(
        "-l",
        "--level",
        dest = "level",
        required = True
    )
    args = parser.parse_args()
    return args



def main(infile, outfile, level, bonus_outkeys=[]):
    from I3Tray import I3Tray
    from icecube import tableio, hdfwriter, icetray, dataclasses

    icetray.set_log_level(icetray.I3LogLevel.LOG_ERROR)
    tray = I3Tray()
    tray.AddModule("I3Reader","reader")(("FilenameList", [infile]))
    if level=="l3_a":
        from utils import prepare_l3_a_vars
        tray.AddModule(prepare_l3_a_vars)
        outkeys = [
            # HitStatistics quantities
            "ZTravel",
            "COGZVertex",
            "COGZSigma",
            # Reconstruction quantities
            "BestFitIdx",
            "RLogL",
            "ZenithReco",
            "AzimuthReco",
            # True quantities
            "ETrue",
            "ZenithTrue",
            "AzimuthTrue",
            "PrimaryType",
            "OneWeight"
        ]
    else:
        raise RuntimeError(f"level {level} not implemented yet.")
    for k in bonus_outkeys:
        outkeys.append(k)
    tray.AddModule(tableio.I3TableWriter, "hdfwriter")(
        ("tableservice",hdfwriter.I3HDFTableService(outfile)),
        ("SubEventStreams",["TTrigger"]),
        ("keys", outkeys)
    )
    tray.Execute()
    tray.Finish()

if __name__=='__main__':

    args = initialize_parser()

    infiles = args.infiles
    if  infiles is None:
        infiles = ['/data/sim/IceCube/2016/filtered/level2/neutrino-generator/nancy001/NuMu/low_energy/hole_ice/p1=0.3_p2=0.0/10/l2_00009414.i3.zst']
    outfiles = args.outfiles
    if outfiles is None:
        outfiles = [infile.split("/")[-1].replace("i3.zst", "h5") for infile in infiles]
        outfiles = [f"{args.outdir}/{f}" for f in outfiles]
    if len(infiles) != len(outfiles):
        raise ValueError("Infile and outfile lists have two different lengths.")
    for infile, outfile in zip(infiles, outfiles):
        print(infile)
        main(infile, outfile, args.level)

