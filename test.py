import numpy as np
#import matplotlib.pyplot as plt
from physicsconstants import PhysicsConstants
units = PhysicsConstants()

import h5py
mcF = h5py.File('/data/ana/SterileNeutrino/IC86/HighEnergy/SPE_Templates/Nominal/Ares/IC86.AVG/Merged/Ares_IC86.AVG_0.97_cuts_platinum_5000.h5', 'r')
print(mcF['keysDict'][()].dtype.names)

PrimaryType     = mcF['keysDict'][()]['PrimaryType']
NuEnergy        = mcF['keysDict'][()]['NuEnergy']
NuZenith        = mcF['keysDict'][()]['NuZenith']
Overburden      = mcF['keysDict'][()]['Overburden']
ParaboloidSigma = mcF['keysDict'][()]['ParaboloidSigma']
RLogL           = mcF['keysDict'][()]['RLogL']
BayesLLHR       = mcF['keysDict'][()]['BayesLLHR']
DirNDoms        = mcF['keysDict'][()]['DirNDoms']

import nuSQUIDSpy as nsq

# nuSQuIDS params
from controls import theta_12, theta_23, theta_13, delta, delta_m_21, delta_m_31, r_earth
interactions     = True
tau_regeneration = True
czens            = np.linspace(min(np.cos(NuZenith)), max(np.cos(NuZenith)), 40)

nu_flux    = np.genfromtxt('data/PostPropagation/SIBYLL2.3_pp_CombinedGHAndHG_H4a_nu.txt')
nubar_flux = np.genfromtxt('data/PostPropagation/SIBYLL2.3_pp_CombinedGHAndHG_H4a_nubar.txt')
ee         = nu_flux[:,0]
flux       = np.hstack([nu_flux[:,1:], nubar_flux[:,1:]])

# Get inital flux into the form nuSQuIDS expects
initial_flux = np.zeros((len(flux[:,0]), 2, 3))
for i in range(3):
    initial_flux[:,0,i] = flux[:, i]
    initial_flux[:,1,i] = flux[:, i+3]

detector_flux = np.zeros((len(flux[:,0]), 2, 3, len(czens)))
for i, czen in enumerate(czens):
    zen = np.arccos(czen)
    print(zen)
    chord  = 2*r_earth*np.sin(zen/2)
    nuSQ = nsq.nuSQUIDS(ee*units.GeV, 3, nsq.NeutrinoType.both, interactions)
    nuSQ.Set_abs_error(1.0e-10)
    nuSQ.Set_rel_error(1.0e-10)

    nuSQ.Set_SquareMassDifference(1, delta_m_21)
    nuSQ.Set_SquareMassDifference(2, delta_m_31)
    nuSQ.Set_MixingAngle(0, 1, theta_12)
    nuSQ.Set_MixingAngle(0, 2, theta_13)
    nuSQ.Set_MixingAngle(1, 2, theta_23)
    nuSQ.Set_CPPhase(0,2,delta)

    nuSQ.Set_Body(nsq.Earth())
    nuSQ.Set_Track(nsq.Earth.Track(chord))
    nuSQ.Set_TauRegeneration(True)
    nuSQ.Set_initial_state(initial_flux, nsq.Basis.flavor)
    nuSQ.EvolveState()
    
    for j in range(3):
        detector_flux[:,0,j,i] = [nuSQ.EvalFlavor(j,e*units.GeV,0) for e in ee]
        detector_flux[:,1,j,i] = [nuSQ.EvalFlavor(j,e*units.GeV,1) for e in ee]

print(detector_flux)
