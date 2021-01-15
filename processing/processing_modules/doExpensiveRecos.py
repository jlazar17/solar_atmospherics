import numpy as np
from selector import selector
from icecube import icetray

#Only select events to calculate more complicated cut variables if they pass some very basic cuts
@selector
def doExpensiveRecos(frame):
    if(frame.Stop!=icetray.I3Frame.Physics):
        return(True)
    
    fallback=frame.Get("TrackFitFallback")
    if(fallback.value > 2):
        return(False)

    track = frame.Get("TrackFit")
    if(np.cos(track.dir.zenith) > 0.2):
        return(False)

    track_dh = frame.Get("TrackFit_dh")
    pulse_hm = frame.Get("TTPulses_hm")

    if(float(pulse_hm.n_hit_doms) < 15.0):
        return(False)
    if(float(track_dh.n_dir_doms) <= 6.0):
        return(False)
    if(float(track_dh.dir_track_length) < 200.0):
        return(False)
    if(abs(float(track_dh.dir_track_hit_distribution_smoothness)) > 0.6):
        return(False)

    return(True)

