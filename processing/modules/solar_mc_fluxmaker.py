import numpy as np

from opening_angle import opening_angle
from base_mc_fluxmaker import BaseMCFluxmaker
from atmo_flux_calculator import SolarAtmoFluxCalculator
import solar_position_calc as sc
from controls import fluxmaker_params
params = fluxmaker_params()

class SolarMCFluxmaker(BaseMCFluxmaker):
    
    def __init__(self, mc, fluxpath):
        BaseMCFluxmaker.__init__(self, mc, fluxpath)
        wfc = SolarAtmoFluxCalculator(fluxpath)
        wfc.initialize_nuSQuIDS()
        self.dndz = np.array([wfc.get_flux(cz, e, ptype) for cz, e, ptype in zip(np.cos(self.mc.nu_zen),
                                                                                 self.mc.nu_e,
                                                                                 self.mc.ptype
                                                                                )
                             ]
                            )

    def calc_flux(self, rad, zen, az):
        solar_solid_angle = 2*np.pi*(1-np.cos(params['r_sun']/rad))
        gamma_cut         = np.arctan(params['r_sun'] / rad)
        zmax              = zen+gamma_cut
        zmin              = zen-gamma_cut
        amax              = az+gamma_cut
        amin              = az-gamma_cut
        m1                = np.logical_and(self.mc.nu_zen>zmin, self.mc.nu_zen<zmax)
        m2                = np.logical_and((self.mc.nu_az>amin%(2*np.pi)), self.mc.nu_az<amax%(2*np.pi))
        m3                = True
        m12               = np.logical_and(m1, m2)
        m                 = np.logical_and(m12, m3)
        nu_gamma          = np.where(m, opening_angle(self.mc.nu_zen, self.mc.nu_az, zen, az), 1)
        reco_gamma        = np.where(m, opening_angle(self.mc.reco_zen, self.mc.reco_az, zen, az), 0)
        
        n = np.where(nu_gamma <= gamma_cut,
                     self.dndz,
                     0
                    )
        return n
    def do_calc(self):
        flux = np.zeros(len(self.dndz))
        for az, jd in zip(params['azimuths'], params['jds']):
            x    = sc.nParameter(jd)
            obl  = sc.solarObliquity(x)
            L    = sc.L(x)
            G    = sc.g(x)
            lamb = sc.solarLambda(L,G)
            rad  = sc.solarR(G)
            zen  = sc.equatorialZenith(obl, lamb)

            flux += self.calc_flux(rad, zen, az)
            
        self.mcflux = np.divide(flux, len(params['jds'])) # returns a rate
