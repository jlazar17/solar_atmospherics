import numpy as np
from icecube import dataclasses
def overburden(frame):
    if frame.Has('MuEx'):
        muex = frame['MuEx']
        z = muex.pos.z
        zen = muex.dir.zenith
        a = 0.259
        b = 0.000363
        R = 12714000.0/2
        h = 1950.0
        d = np.sqrt(muex.pos.x**2+muex.pos.y**2)
        L = d/np.tan(zen)
        J = R - h + L + z
        p = np.sqrt(d**2 + (J-L)**2)
        beta = 3*np.pi/2 - zen - np.arctan(J/d)
        alpha = np.arcsin(p * np.sin(beta)/R)
        theta = np.pi - (beta + alpha)
        OB = R*np.sin(theta)/np.sin(beta)
        frame.Put("Overburden",dataclasses.I3Double(OB))

