import numpy as np

from DM import DMAnnihilationJungmanSD
from opening_angle import opening_angle
from base_mc_fluxmaker import BaseMCFluxmaker
from wimp_flux_calculator import WIMPFluxCalculator
from controls import fluxmaker_params
import solar_position_calc as sc
fluxmaker_params = fluxmaker_params()

class WIMPMCFluxmaker(BaseMCFluxmaker):
    
    def __init__(self, mc, fluxpath):
        BaseMCFluxmaker.__init__(self, mc, fluxpath)
        self.mass = int(self.fluxpath.split('/')[-1].split('_')[0].split('m')[-1])
        wfc = WIMPFluxCalculator(fluxpath, self.mass)
        wfc.initialize_nuSQuIDS()
        self.dndz = np.array([wfc.get_flux(cz, e, ptype) for cz, e, ptype in zip(np.array(np.cos(self.mc.nu_zen),np.float64),
                                                                                 self.mc.nu_e,
                                                                                 self.mc.ptype
                                                                                )
                             ]
                            )
        self.rate = DMAnnihilationJungmanSD(self.mass, 1.0e-39) # Annihlation rate for xs=1 femtobarn

    def calc_flux(self, rad, zen, az):
        solar_solid_angle = 2*np.pi*(1-np.cos(fluxmaker_params['r_sun']/rad))
        gamma_cut         = np.arctan(fluxmaker_params['r_sun'] / rad)
        zmax              = zen+gamma_cut
        zmin              = zen-gamma_cut
        amax              = az+gamma_cut
        amin              = az-gamma_cut
        m1                = np.logical_and(self.mc.nu_zen>zmin, self.mc.nu_zen<zmax)
        m2                = np.logical_and((self.mc.nu_az>amin%(2*np.pi)), self.mc.nu_az<amax%(2*np.pi))
        m3                = True
        #m3                = self.mc.nu_e<=float(self.mass)
        m12               = np.logical_and(m1, m2)
        m                 = np.logical_and(m12, m3)
        nu_gamma          = np.where(m, opening_angle(self.mc.nu_zen, self.mc.nu_az, zen, az), 1)
        
        n = np.where(nu_gamma <= gamma_cut,
                     self.dndz *             \
                     #self.mc.oneweight[m] *    \
                     (1. / solar_solid_angle) * \
                     (1. / (4*np.pi*np.power(rad, 2))) * \
                     (1. / self.mass) * \
                     self.rate,
                     0
                    )
        return n
    
    def do_calc(self):
        flux = np.zeros(len(self.dndz))
        for az, jd in zip(fluxmaker_params['azimuths'], fluxmaker_params['jds']):
            x    = sc.nParameter(jd)
            obl  = sc.solarObliquity(x)
            L    = sc.L(x)
            G    = sc.g(x)
            lamb = sc.solarLambda(L,G)
            rad  = sc.solarR(G)
            zen  = sc.equatorialZenith(obl, lamb)

            flux += self.calc_flux(rad, zen, az)
            
        self.mcflux = np.divide(flux, len(fluxmaker_params['jds'])) # returns a rate
