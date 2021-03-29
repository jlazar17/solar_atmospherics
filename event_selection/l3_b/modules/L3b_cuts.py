from I3Tray import NaN
from icecube import dataclasses
def L3b_cuts(frame):
    if frame['I3EventHeader'].sub_event_stream!='TTrigger':
        return True

    
    fitname      = 'MPEFit_TT'
    track        = frame[fitname]
    llhparam     = frame[fitname+'FitParams']
    rlogl        = llhparam.rlogl
    
    if track.dir.zenith < 1.3:
        return False
    elif rlogl>34:
        return False
    else:
        return True
