import os,sys
from I3Tray import I3Tray
from icecube import icetray, hdfwriter, tableio, dataclasses
from solar_atmospherics import l3_b_descs
from solar_atmospherics.modules import cut_bad_fits, rename_out_vars, l3b_cuts

DEFAULT_OUTKEYS = [key for key, dtype in l3_b_descs]

def initialize_parser():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    # I/O
    parser.add_argument("-i", "--infiles", 
                      dest="infiles",
                      type=str,
                      required=True,
                     )
    parser.add_argument("-o", "--outfile",
                      dest="outfile",
                      default='l3_b.h5',
                      type=str
                     )
    parser.add_argument("--outkeys", 
                        dest="outkeys", default="")
    # Simulation / data information
    parser.add_argument("--fluxname",
                      dest="fluxname",
                      type=str,
                      required=True,
                     )
    parser.add_argument("--corsika_set",
                      dest="corsika_set",
                      type=int,
                      default=0
                     )
    # Option to process only a feewe frames. Good for debugging
    parser.add_argument('-n', '--nframe', 
                      dest='nframe',
                      default=-1, 
                      type=int, 
                      help='How many frames to do this for. Default do all frames.')
    arguments = parser.parse_args()
    return arguments

def main(infiles, outfile, outkeys, fluxname, corsika_set, nframe=-1):
    r"""
    infiles (list)    : list of i3 files to process
    outfile (str)     : name of h5 to write the output to
    outkeys (list)    : names of keys to write to the outfile
    fluxname (str)    : name of simualtion/data set to use.
                        must be in ["corsika", "nancy", "genie", "exp_data"]
    corsika_set (int) : number of CORSIKA. Should be None if fluxname!="corsika"
    [nframe] (int)    : number of frame to process. 
                        A value of -1 will process all of them
    """
    icetray.set_log_level(icetray.I3LogLevel.LOG_ERROR)
    tray = I3Tray()
    tray.AddModule("I3Reader","reader")(("FilenameList", infiles))
    tray.AddModule(cut_bad_fits, 'bad_fit_cutter') # This should not be in here long term
    tray.AddModule(l3b_cuts, 'l3_b_cutter') # This should not be in here long term
    tray.AddModule(rename_out_vars, geometry=None, fluxname=fluxname, corsika_set=corsika_set)
    tray.AddModule(tableio.I3TableWriter, "hdfwriter")(
            ("tableservice",hdfwriter.I3HDFTableService(outfile)),
            ("SubEventStreams",["TTrigger"]),
            ("keys", outkeys)
    )
    if nframe==-1:
        tray.Execute()
    else:
        tray.Execute(nframe)
    tray.Finish()

if __name__=='__main__':

    from glob import glob
    from time import time
    arguments = initialize_parser()
    infiles = glob(arguments.infiles)
    outfile = arguments.outfile
    outkeys = arguments.outkeys
    fluxname = arguments.fluxname
    corsika_set = arguments.corsika_set
    nframe = arguments.nframe

    # If outkeys has beeen passed a null argument use the default set
    if not outkeys:
        outkeys = DEFAULT_OUTKEYS
    # Else split what has been passed to make a list
    else:
        outkeys = outkeys.split()

    # Require a CORSIKA set when processing CORSIKA simulation
    if fluxname=="corsika" and not corsika_set:
        raise ValueError("You must provide a CORSIKA set to process this simulation")
    # Remove MC truth outkeys if processing data
    # This may not be necessary if the writer just ignores a key if it does not exist in the file
    # TODO test if we need this check
    if fluxname=="data":
        mc_outkeys = "oneweight eff_oneweight TrueEnergy TrueZenith TrueAzimuth PrimaryType".split()
        for key in mc_outkeys:
            try:
                outkeys.remove(key)
            # Happens if user passed non-default stuff
            except ValueError:
                pass
    t0 = time()
    main(infiles, outfile, outkeys, fluxname, corsika_set, nframe=nframe)
    t1 = time()
    print(t1-t0)
