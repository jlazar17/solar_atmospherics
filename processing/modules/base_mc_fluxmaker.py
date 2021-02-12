import numpy as np

import solar_position_calc as sc
from controls import fluxmaker_params
params = fluxmaker_params()

class BaseMCFluxmaker():
    
    def __init__(self, mc, fluxpath):
        self.mc       = mc
        self.fluxpath = fluxpath

    def calc_flux(self, rad, zen, az):
        pass

    
    def do_calc(self):
        avg_flux = np.zeros(len(self.mc.oneweight))
        for az, jd in zip(params['azimuths'], params['jds']):
            x      = sc.nParameter(jd)
            obl    = sc.solarObliquity(x)
            L      = sc.L(x)
            G      = sc.g(x)
            lamb   = sc.solarLambda(L,G)
            rad    = sc.solarR(G)
            zenith = sc.equatorialZenith(obl, lamb)

            avg_flux += self.calc_flux(rad, zenith, az)
            
        self.avg_flux = np.divide(avg_flux, len(params['jds'])) # returns a rate
