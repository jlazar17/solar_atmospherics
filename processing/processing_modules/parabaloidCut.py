from selector import selector
from icecube import dataclasses

@selector
def parabaloidCut(frame):
	if(frame["TrackFitParaboloidFitParams"].pbfStatus!=dataclasses.I3Particle.OK): return False
	return(True)

