from optparse import OptionParser
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
                      default ='/data/ana/SterileNeutrino/IC86/HighEnergy/MC/Systematics/Noise/Ares/GeoCalibDetectorStatus_AVG_55697-57531_PASS2_SPE_withScaledNoise.i3.gz'
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
                      default = '/data/ana/SterileNeutrino/IC86/HighEnergy/SPE_Templates/Nominal/Ares/IC86.AVG/L2/domeff_0.97/00001-01000/L2_00_11_00991.i3.zst'
                     )
    parser.add_option("-o", "--outfile",
                      dest="outfile",
                      type=str,
                      default='/data/user/jlazar/share/jvillarreal/test_JLevel.i3.zst'
                     )
    parser.add_option("--h5file",
                      dest="h5file",
                      type=str,
                      default=''
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

