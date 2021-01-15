from selector import selector
from icecube import icetray
@selector
def splitFrames(frame):
    if(frame.Stop!=icetray.I3Frame.Physics):
        return(True)
    return (frame["I3EventHeader"].sub_event_stream=="TTrigger")
