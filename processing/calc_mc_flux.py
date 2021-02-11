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
    parser.add_argument('-o', type=str)
    args = parser.parse_args()
    return args

def create_mc_fluxmaker(mcpath, flux):
    if flux=='conv-atm':
        from convnumu_mc_fluxmaker import ConvNumuMCFluxMaker
        fluxmaker = ConvNumuMCFluxMaker(mcpath, flux)
    elif flux=='solar-atm':
        from solaratm_mc_fluxmaker import SolarAtmMCFluxMaker
        fluxmaker = SolarAtmMCFluxMaker(mcpath, flux)
    else:
        from wimp_mc_fluxmaker import WIMPMCFluxmaker
        fluxmaker = WIMPMCFluxmaker(mcpath, flux)
    return fluxmaker

def main(mcpath, flux, outfile):
    mc = MCReader(mcpath)
    fluxmaker = create_mc_fluxmaker(mc, flux)
    #fluxmaker.initialize_nuSQuIDS()
    fluxmaker.do_calc()
    
    np.save(outfile, fluxmaker.mcflux)

if __name__=='__main__':
    args      = initialize_args()
    main(args.mcpath, args.flux, args.o)
