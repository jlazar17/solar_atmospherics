import numpy as np

import sys
sys.path.append('./modules/')
sys.path.append('/data/user/jlazar/charon/charon/')

from mc_reader import MCReader

def initialize_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--mcpath',
                        type=str,
                        help='path to mcpath to be used'
                       )
    parser.add_argument('--flux',
                        type=str,
                        help='flux to be used, e.g. conv-atm or ch5-m1000'
                       )
    parser.add_argument('-o', type=str, default='')
    args = parser.parse_args()
    return args

def create_mc_fluxmaker(mcpath, flux):
    if flux=='conv-atm':
        from convnumu_mc_fluxmaker import ConvNumuMCFluxMaker
        fluxmaker = ConvNumuMCFluxMaker(mcpath, flux)
    elif flux=='solar-atm':
        from solar_mc_fluxmaker import SolarMCFluxmaker
        fluxmaker = SolarMCFluxmaker(mcpath, flux)
    else:
        fluxpath = '/data/user/jlazar/solar_WIMP_v2/data/charon_fluxes/%s_1AU_BRW.npy' % flux
        from wimp_mc_fluxmaker import WIMPMCFluxmaker
        fluxmaker = WIMPMCFluxmaker(mcpath, fluxpath)
    return fluxmaker

def main(mcpath, flux, outfile):
    mc = MCReader(mcpath)
    fluxmaker = create_mc_fluxmaker(mc, flux)
    #fluxmaker.initialize_nuSQuIDS()
    fluxmaker.do_calc()
    
    np.save(outfile, fluxmaker.mcflux)

if __name__=='__main__':
    args      = initialize_args()
    if args.o=='':
        default_outdir  = '/data/user/jlazar/solar_atmospherics/data/mc_fluxes/'
        import os
        if not os.path.isdir(default_outdir):
            os.makedirs(default_outdir)
        mcname  = args.mcpath.split('/')[-1].split('.')[0]
        outfile = '%s/%s_%s.npy' % (default_outdir, args.flux, mcname)
    else:
        outfile = args.o
    print(args.o)
    main(args.mcpath, args.flux, outfile)
