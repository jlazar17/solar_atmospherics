from .selector import selector
# In case of weirdness, select only for events which have the necessary pulses
@selector
def has_twsrt_offline_pulses(frame):
    return(frame.Has('SRTInIcePulses'))
