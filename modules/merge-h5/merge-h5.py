import h5py as h5
from glob import glob
import numpy as np
from solar_atmospherics import outdescs_dict
import solar_atmospherics
params = {}
nevents = {
          ('nancy', 'low') : 50000.0,
          ('nancy', 'medium') : 10000.0,
          'genie' : 50000.0
         }
params['nevents'] = nevents
def initialize_parser():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('--simname', 
                      dest='simname',
                      default='nancy', 
                      type=str,
                      help='Which simulation to use. Must be "nancy", "genie" or "corsika". "Nancy" by default'
                     )
    parser.add_option('--jump', 
                      dest='jump',
                      type=int,
                     )
    parser.add_option('--level', 
                      dest='level',
                      type=str,
                     )
    options,args = parser.parse_args()
    return options, args
def get_info(simname, level, jump=None):
    params['descs'] = outdescs_dict[level]
    print(params['descs'])
    base_dir = '/data/user/jvillarreal/solar_atmospherics/event_selection/%s/data/%s/h5/' % (level, simname)
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
        skip = 50
        base_dir = '/data/user/jvillarreal/solar_atmospherics/event_selection/l3_b/data/corsika/h5/'
        h5_infiles = [
                      sorted(glob('%s/*.h5' % base_dir)[jump::skip])
                     ]
        all_files = open(solar_atmospherics.__path__[0]+'/event_selection/l3_a/input/i3/corsika/input_corsika_l3_a_i3.txt')
        fudge     = skip*len(h5_infiles[0])/float(len(all_files.readlines()))
        info      = [(fs, fudge) for fs in h5_infiles]
    elif simname=='exp_data':
        raise ValueError('Merging for experimental data not supported yet.')
    else:
        raise ValueError('Simname %s not recognize' % simname)
    return info

def merge_h5(simname, level, jump):
    info = get_info(simname, level)
    if simname=='corsika':
        outfile = '/data/user/jlazar/big_files/solar_atmospherics/merging/%s_%s_merged_holeice-0300_%d.h5'  % (level,simname, jump)
    else:
        outfile = '/data/user/jlazar/big_files/solar_atmospherics/%s_%s_merged_holeice-0300_1.h5' % (level,simname)
    with h5.File(outfile, 'w') as h5_outfile:
        dsets = {}
        for key, dtype in params['descs']:
            dsets[key] = h5_outfile.create_dataset(key, (0,), dtype=dtype, maxshape=(None,), chunks=None)
        for infiles, divisor in info:
            for k, infile in enumerate(infiles):
                if k%1000==0:
                    print(k)
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
if __name__=='__main__':
    options, args = initialize_parser()
    merge_h5(options.simname, options.level, options.jump)
