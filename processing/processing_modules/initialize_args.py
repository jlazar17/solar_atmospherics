from optparse import OptionParser
import os
def make_outfile_name(infile):
    infile  = infile.replace('=', '').replace('\\', '')
    if 'nancy001' in infile:
        outdir    = '/data/user/jlazar/solar_atmospherics/processing/data/nancy'
        nutype    = infile.split('/')[9]
        eregime   = infile.split('/')[10].replace('_', '')
        syst_desc = '-'.join(infile.split('/')[11:13]).replace('_', '').replace('p1','').replace('p2','').replace('.', '')
        fnum      = infile.split('/')[-1].strip('l2_')
        outfile   ='%s/JLevel_%s_%s_%s_%s' % (outdir, nutype,eregime, syst_desc, fnum)
    elif 'data/nancy/i3/' in infile:
        outdir  = '/data/user/jlazar/solar_atmospherics/processing/data/nancy/h5/'
        fname   = infile.split('/')[-1].replace('i3.zst', 'h5')
        outfile = '%s/%s' % (outdir, fname)

    else:
        quit()
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
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
    parser.add_option("--h5file",
                      dest="h5file",
                      default=make_outfile_name
                     )
    parser.add_option("-t", '--test',
                      dest='test',
                      type=str,
                      default='True'
                     )
    parser.add_option("-m", "--move",
                      dest="move",
                      default='False',
                      type=str, 
                      help = 'Generate in tmp dir, then move to correct location?'
                     )
    parser.add_option("-s", "--osg",
                      dest="osg",
                      default='False',
                      type=str, 
                      help = 'Is this running on the OSG?'
                     )
    parser.add_option("-c", "--cut",
                      dest="cut",
                      default='False',
                      type=str, 
                      help = 'Do not touch this. Should be False.'
                     )

    options,args = parser.parse_args()
    return options, args

