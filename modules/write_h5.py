from I3Tray import I3Tray
from icecube import tableio, hdfwriter, icetray, dataclasses

from .rename_out_vars import rename_out_vars
from .cut_bad_fits import cut_bad_fits

def make_outfile_name(infile):
    outfile = infile.replace('i3.zst', 'h5').replace('i3', 'h5')
    print(outfile)
    return outfile

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
                      default ='/data/ana/SterileNeutrino/IC86/HighEnergy/MC/Systematics/Noise/GeoCalibDetectorStatus_AVG_Fit_55697-57531_SPE_PASS2_Raw.i3.gz'
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
    parser.add_option("-l", "--level",
                      dest="level",
                      default=""
                     )
    options,args = parser.parse_args()
    return options, args

class H5Writer(object):

    def __init__(self, i3file, gcdfile, level):
        r'''
        i3file  : IceCube file whose contents you want to dump to an h5 file
        gcdfile : Not sure this is the right thing to do ????????
        level   : Level within the processing chain the i3file has been processed to
        '''
        self.i3file   = i3file
        self.gcdfile  = gcdfile
        self.level    = level
        self.infiles  = [gcdfile, i3file]
        self.outfile  = None
        self._set_simnname()
        self._set_outkeys()

    def set_outfile(self, outfile):
        if not callable(outfile):
            self.outfile = outfile
        else:
            self.outfile = outfile(self.infile)

    def _set_simnname(self):
        if 'nancy' in self.i3file:
            self.fluxname    = 'nancy'
            self.corsika_set = None
        elif 'genie' in self.i3file:
            self.fluxname    = 'genie'
            self.corsika_set = None
        elif 'corsika' in self.i3file:
            self.fluxname    = 'corsika'
            self.corsika_set = int(self.i3file.split('.')[-4])
        elif 'exp' in self.i3file:
            self.fluxname    = 'exp_data'
            self.corsika_set = None
        else:
            raise ValueError(f'unable to determine simname from infile {self.i3file}')

    def _set_outkeys(self):
        from .outkeys import outkeys_dict
        self.outkeys =  outkeys_dict[self.level]
    
    def dump_h5(self):
        icetray.set_log_level(icetray.I3LogLevel.LOG_ERROR)
        tray = I3Tray()
        tray.AddModule("I3Reader","reader")(("FilenameList", self.infiles))
        tray.AddModule(cut_bad_fits, 'bad_fit_cutter') # This should not be in here long term
        tray.AddModule(rename_out_vars, geometry=None, fluxname=self.fluxname, corsika_set=self.corsika_set)
        tray.AddModule(tableio.I3TableWriter, "hdfwriter")(
                ("tableservice",hdfwriter.I3HDFTableService(self.outfile)),
                ("SubEventStreams",["TTrigger"]),
                ("keys",self.outkeys)
                )
        tray.Execute()
        tray.Finish()

if __name__=='__main__':
    options, args = initialize_parser()
    h5w = H5Writer(options.infile, options.gcdfile, options.level)
    h5w.set_outfile(options.outfile)
    h5w.dump_h5()
