from I3Tray import NaN
from icecube import dataclasses
def cut_bad_fits(frame):
    if frame['I3EventHeader'].sub_event_stream!='TTrigger':
        return True

    
    fitname      = 'MPEFit_TT'
    track        = frame[fitname]
    llhparam     = frame[fitname+'FitParams']
    rlogl        = llhparam.rlogl
    if track.fit_status_string!='OK':
        return False
    else:
        return True
