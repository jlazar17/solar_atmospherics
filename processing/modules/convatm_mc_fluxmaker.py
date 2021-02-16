import numpy as np

from base_mc_fluxmaker import BaseMCFluxmaker
from atmo_flux_calculator import ConvAtmoFluxCalculator
import solar_position_calc as sc

class ConvAtmMCFluxMaker(BaseMCFluxmaker):
    
    def __init__(self, mc, fluxpath):
        BaseMCFluxmaker.__init__(self, mc, fluxpath)
        wfc         = ConvAtmoFluxCalculator(fluxpath)
        wfc.initialize_nuSQuIDS()
        self.mcflux = np.array([wfc.get_flux(cz, e, ptype) for cz, e, ptype in zip(np.array(np.cos(self.mc.mc_data.nu_zen),np.float64),
                                                                                 self.mc.mc_data.nu_e,
                                                                                 self.mc.mc_data.ptype
                                                                                )
                               ]
                              )

    def do_calc(self):
        pass
