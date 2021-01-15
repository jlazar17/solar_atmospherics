from selector import selector
from icecube import dataclasses

@selector
def goodFit(frame):
    if(not frame.Has("TrackFit")):
        return(False)
    if(frame["TrackFit"].fit_status!=dataclasses.I3Particle.OK):
        return(False)
    if(frame.Has("TrackFitFallback") and frame["TrackFitFallback"].value > 2):
        return(False)
    return(True)

