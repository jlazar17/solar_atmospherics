import numpy as np

from controls import fluxmaker_params
import solar_position_calc as sc

class BaseMCFluxmaker():
    
    def __init__(self, mc, fluxpath):
        self.mc       = mc
        self.fluxpath = fluxpath

    def calc_flux(self, rad, zen, az):
        pass

    
    def do_calc(self):
        avg_flux = np.zeros(len(self.mc.oneweight))
        for az, jd in zip(fluxmaker_params['azimuths'], fluxmaker_params['jds']):
            x      = sc.nParameter(jd)
            obl    = sc.solarObliquity(x)
            L      = sc.L(x)
            G      = sc.g(x)
            lamb   = sc.solarLambda(L,G)
            rad    = sc.solarR(G)
            zenith = sc.equatorialZenith(obl, lamb)

            avg_flux += self.calc_flux(rad, zenith, az)
            
        self.avg_flux = np.divide(avg_flux, len(fluxmaker_params['jds'])) # returns a rate
