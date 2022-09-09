from icecube.icetray import I3PacketModule
from icecube import icetray

class PacketCutter(I3PacketModule):
    def __init__(
        self,
        context,
        cut = lambda frame: True,
        sub_event_stream = "TTrigger",
    ):
        super(PacketCutter, self).__init__(context, icetray.I3Frame.DAQ)
        self._cut = cut
        self._sub_event_stream = sub_event_stream
 
    def FramePacket(
        self,
        frames,
    ):
        frames_to_push = []
        tt_passed = [
            self._cut(fr) for fr in frames 
            if fr["I3EventHeader"].sub_event_stream==self._sub_event_stream
        ]
        # We only add to the pushable frames if one of the split pulses
        # passes our criteria
        if any(tt_passed):
            i = 0
            for fr in frames:
                # We've already checked if the cut was passed
                # We don't need to look again
                if fr["I3EventHeader"].sub_event_stream==self._sub_event_stream:
                    if tt_passed[i]:
                        frames_to_push.append(fr)
                    i += 1
                # We haven't checked the cut for non
                elif self._cut(frame, **self._cutkwargs):
                    frames_to_push.append(fr)
        for fr in frames_to_push:
            self.PushFrame(fr)
