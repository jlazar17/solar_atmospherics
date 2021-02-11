import numpy as np
from controls import fluxmaker_params
import nuSQUIDSpy as nsq
from physicsconstants import PhysicsConstants
units = PhysicsConstants()

class BaseFluxCalculator():

    def __init__(self, init_flux_path):
        self.init_flux_path = init_flux_path

    def _make_initial_data(self):
        pass

    def initialize_nuSQuIDS(self):
        czens, energies, initial_flux = self._make_initial_data()
        interactions = True
        self.nsq_atm = nsq.nuSQUIDSAtm(czens, energies*units.GeV, 3, nsq.NeutrinoType.both, interactions)
        self.nsq_atm.Set_initial_state(initial_flux, nsq.Basis.flavor)
        
        self.nsq_atm.Set_rel_error(1.0e-15)
        self.nsq_atm.Set_abs_error(1.0e-15)
