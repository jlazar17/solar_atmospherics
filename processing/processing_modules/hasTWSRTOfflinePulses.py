from selector import selector
# In case of weirdness, select only for events which have the necessary pulses
@ selector
def hasTWSRTOfflinePulses(frame):
    return(frame.Has("SRTInIcePulses"))
