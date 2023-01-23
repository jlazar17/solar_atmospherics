from I3Tray import I3Tray
from icecube import tableio, hdfwriter, icetray, dataclasses

from .rename_out_vars import rename_out_vars
from .cut_bad_fits import cut_bad_fits
from .l3b_cuts import l3b_cuts

def make_outfile_name(infile):
    outfile = infile.replace('i3.zst', 'h5').replace('i3', 'h5')
    return outfile

def initialize_parser():
    parser = OptionParser()
    parser.add_option('-n', '--nFrames', 
                      dest='nFrames',
                      default=0, 
                      type=int, 
                      help='How many frames to do this for. Default do all frames.')
    parser.add_option("-i", "--infile", 
                      dest="infile",
                      type=str,
                      default = '/data/sim/IceCube/2016/filtered/level2/neutrino-generator/nancy001/NuMu/low_energy/hole_ice/p1=0.3_p2=0.0/10/l2_00009414.i3.zst',
                     )
    parser.add_option("-o", "--outfile",
                      dest="outfile",
                      default=make_outfile_name
                     )
    parser.add_option("-l", "--level",
                      dest="level",
                      default=""
                     )
    options,args = parser.parse_args()
    return options, args



def main(infile, outfile, output_keys, fluxname, corsika_set):
    icetray.set_log_level(icetray.I3LogLevel.LOG_ERROR)
    tray = I3Tray()
    tray.AddModule("I3Reader","reader")(("FilenameList", self.infiles))
    tray.AddModule(rename_out_vars, geometry=None, fluxname=fluxname, corsika_set=corsika_set)
    tray.AddModule(tableio.I3TableWriter, "hdfwriter")(
            ("tableservice",hdfwriter.I3HDFTableService(self.outfile)),
            ("SubEventStreams",["TTrigger"]),
            ("keys", output_keys)
            )
    tray.Execute()
    tray.Finish()

if __name__=='__main__':
    options, args = initialize_parser()
    h5w = H5Writer(options.infile, options.gcdfile, options.level)
    h5w.set_outfile(options.outfile)
    h5w.dump_h5()
