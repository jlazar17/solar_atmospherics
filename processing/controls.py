import numpy as np
from physicsconstants import PhysicsConstants
units = PhysicsConstants()

datadir = '/data/user/jlazar/solar_WIMP_v2/data/'

start = 2455349.5
stop  = 2456810.5 # 4 years
#n     = 35000
n     = 350
fluxmaker_params = dict(
                        jds      = np.linspace(start, stop, n), # roughly every hour
                        azimuths = np.random.rand(n)*np.pi*2,
                        r_sun    = 6.9e10, # cm
                       )
czens    = np.linspace(-1, 1, 150)
