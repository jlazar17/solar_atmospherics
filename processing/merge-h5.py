import h5py as h5
from glob import glob
from controls import weighting_params
import numpy as np
params = weighting_params()

def initialize_parser():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('--simname', 
                      dest='simname',
                      default='nancy', 
                      type=str,
                      help='Which simulation to use. Must be "nancy", "genie" or "corsika". "Nancy" by default'
                     )

    options,args = parser.parse_args()
    return options, args


options, args = initialize_parser()
base_dir = '/data/user/jvillarreal/solar_atmospherics/processing/data/%s_prime/h5/' % options.simname      
if options.simname=='nancy':
    info = []
    for nutype in ['NuE', 'NuMu', 'NuTau']:
        for etype in ['low']:
        #for etype in ['low', 'medium']:
            fs = sorted(glob('%s/*%s_%senergy*.h5' % (base_dir, nutype, etype)))
            info.append((fs, len(fs)*params['nevents'][('nancy', etype)]))
elif options.simname=='genie':
    info = []
    for did in [21405, 21388, 21379]:
        fs = sorted(glob('%s/*%d*.h5' % (base_dir, did)))
        info.append((fs, len(fs)*params['nevents']['genie']))
elif options.simname=='corsika':
    h5_infiles = [
                  sorted(glob('%s/*.h5' % base_dir))
                 ]
    f = open('./data/corsika/i3/input/input.txt', 'r')
    fudge  = len(h5_infiles[0])/float(len(f.readlines()))
    print(fudge)
    info         = [(fs, fudge) for fs in h5_infiles]

with h5.File('/data/user/jlazar/solar_atmospherics/processing/data/merged/JLevel_%s_merged_holeice-0300_1.h5' % options.simname, 'w') as h5_outfile:
    dsets = {}
    for key, dtype in params['descs']:
        dsets[key] = h5_outfile.create_dataset(key, (0,), dtype=dtype, maxshape=(None,), chunks=None)
    for infiles, divisor in info:
        for infile in infiles:
            with h5.File(infile, 'r') as h5_infile:
                if len(h5_infile.keys())>1:
                    for key, _ in params['descs']:
                        dset = dsets[key]
                        if key=='eff_oneweight':
                            n = len(h5_infile['oneweight'][()]['value'])
                            if n > 0:
                                dset.resize((dset.shape[0]+n,))
                                if options.simname=='nancy':
                                    dset[-n:] = h5_infile['oneweight'][()]['value']/divisor
                                elif options.simname=='genie':
                                    genie_genprob = np.where(h5_infile['PrimaryType'][()]['value']>0, 0.7, 0.3)
                                    dset[-n:] = h5_infile['oneweight'][()]['value']/divisor/genie_genprob
                                elif options.simname=='corsika':
                                    dset[-n:] = h5_infile['oneweight'][()]['value']/divisor
                            else:
                                print('len==0: ' + infile)
                        else:
                            n = len(h5_infile[key][()]['value'])
                            if n > 0:
                                dset.resize((dset.shape[0]+n,))
                                dset[-n:] = h5_infile[key][()]['value']
