import numpy as np
from mc_reader import MCReader

import sys
sys.path.append('/data/user/jlazar/solar_WIMP_v2/modules/')


def initialize_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--mcpath',
                        type=str,
                        help='path to mcpath to be used'
                       )
    parser.add_argument('--fluxtype',
                        type=str,
                        help='fluxtype to be used, e.g. conv-numu or ch5-m1000'
                       )
    parser.add_argument('-o', type=str)
    args = parser.parse_args()
    return args

def create_mc_fluxmaker(mcpath, fluxtype):
    if fluxtype=='conv-numu':
        from convnumu_mc_fluxmaker import ConvNumuMCFluxMaker
        fluxmaker = ConvNumuMCFluxMaker(mcpath, fluxtype)
    elif fluxtype=='solar-atm':
        from solaratm_mc_fluxmaker import SolarAtmMCFluxMaker
        fluxmaker = SolarAtmMCFluxMaker(mcpath, fluxtype)
    else:
        from signal_mc_fluxmaker import SignalMCFluxMaker
        fluxmaker = SignalMCFluxMaker(mcpath, fluxtype)
    return fluxmaker

def main(mcpath, fluxtype, outfile):
    mc = MCReader(mcpath)
    fluxmaker = create_mc_fluxmaker(mc, fluxtype)
    fluxmaker.initialize_nuSQuIDS()
    fluxmaker.interp_mc()
    
    np.save(outfile, fluxmaker.mcflux)

if __name__=='__main__':
    args      = initialize_args()
    main(args.mcpath, args.fluxtype, args.o)
