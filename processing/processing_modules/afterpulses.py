from selector import selector
@selector
def afterpulses(frame):
    return(frame.Has("IsAfterPulses"))
