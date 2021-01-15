from selector import selector

@selector
def parabaloidCut(frame):
	if(frame["TrackFitParaboloidFitParams"].pbfStatus!=dataclasses.I3Particle.OK): return False
	return(True)

