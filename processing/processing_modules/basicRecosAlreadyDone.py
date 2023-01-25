from icecube import icetray
from selector import selector
@selector
def basicRecosAlreadyDone(frame):
	if(frame.Stop!=icetray.I3Frame.Physics):
		return(True)
	return(frame.Has("MPEFit_TT"))
