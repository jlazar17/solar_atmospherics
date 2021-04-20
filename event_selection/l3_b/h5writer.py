import os,sys
from solar_atmospherics.modules import H5Writer, figure_out_gcd

def initialize_parser():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-n', '--nFrames', 
                      dest='nFrames',
                      default=0, 
                      type=int, 
                      help='How many frames to do this for. Default do all frames.')
    parser.add_option('-g', '--gcdfile',
                      dest='gcdfile',
                      type=str,
                      default =''
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
                      default='/data/sim/IceCube/2016/filtered/level2/neutrino-generator/nancy001/NuMu/low_energy/hole_ice/p1=0.3_p2=0.0/10/l2_00009414.i3.zst',
                     )
    parser.add_option("-o", "--outfile",
                      dest="outfile",
                      default=''
                     )
    options,args = parser.parse_args()
    return options, args

if __name__=='__main__':
    options, args = initialize_parser()
    level = 'l3_b'
    if 'i3.zst' in options.infile:
        import time
        t0 = time.time()
        infile = options.infile
        if options.outfile=='':
            fname   = infile.split('/')[-1].replace('i3.zst', 'h5')
            outdir  = '%s/%s/h5/' % (os.environ.get('L3_B_SAVEDIR'), infile.split('/')[-3])
            outfile = fname+outdir
        else:
            outfile = options.outfile
        print(outfile)
        if options.gcdfile=='':
            gcdfile = figure_out_gcd(infile)
        else:
            gcdfile = options.gcdfile
        h = H5Writer(infile, gcdfile, level)
        h.set_outfile(outfile)
        h.dump_h5()
        print(time.time()-t0)
    else:
        with open(options.infile) as f:
            fs = f.read().split('\n')[:-1]
        for infile in fs:
            fname   = infile.split('/')[-1].replace('i3.zst', 'h5')
            outdir  = '%s/%s/h5/' % (os.environ.get('L3_B_SAVEDIR'), infile.split('/')[-3])
            if not os.path.isdir(outdir):
                os.makedirs(outdir)
            outfile = outdir+fname
            gcdfile = figure_out_gcd(infile)
            h = H5Writer(infile, gcdfile, level)
            h.set_outfile(outfile)
            print(h.outfile)
            h.dump_h5()
