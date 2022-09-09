#from icecube.icetray import I3Frame
#from I3Tray import *
from icecube import icetray, dataio, dataclasses
#from icecube.common_variables import direct_hits
#from icecube.common_variables import hit_multiplicity
from icecube.icetray import I3Units
from icecube.common_variables import track_characteristics
from icecube import phys_services
from icecube import VHESelfVeto, DomTools
from icecube import weighting
from icecube.weighting.weighting import from_simprod
from icecube.weighting.fluxes import GaisserH3a
from icecube import truncated_energy
from icecube.common_variables import hit_statistics as hs
from icecube import lilliput, gulliver, gulliver_modules, paraboloid
from icecube import dataclasses, icetray
from icecube.icetray import I3PacketModule
#from .packet_cutter import PacketCutter

def hit_statistics_cut(
    frame,
    z_travel=-10,
    cog_z_vertex=110,
    cog_z_sigma=110,
):
    if frame["I3EventHeader"].sub_event_stream != "TTrigger":
        return True
    key = "TTPulses_HitStatistics"
    if key not in frame.keys():
        raise RuntimeError("No 'TTPulses_HitStatistics' found. What is going on here")
    stats = frame[key]
    if stats.cog.z >= cog_z_vertex:
        return False
    if stats.cog_z_sigma >= cog_z_sigma:
        return False
    if stats.z_travel <= z_travel:
        return False
    return True

def fit_cut(
    frame,
    rlogl = 22,
    zenith_min = 1.4835, # 85 degrees
    zenith_max = 2.4435 # 140 degrees
):
    if frame["I3EventHeader"].sub_event_stream != "TTrigger":
        return True
    fit = None
    for fit_name in ["SPEFit4_TT", "MPEFit_TT"]:
        proposed_fit = frame[fit_name]
        if proposed_fit.fit_status_string=="OK":
            fit = proposed_fit
            params = frame[fit_name + "FitParams"]
    if fit is None:
        return False
    else:
        if params.rlogl > rlogl:
            return False
        if fit.dir.zenith < zenith_min or fit.dir.zenith > zenith_max:
            return False
        return True

class FitCutter(I3PacketModule):

    def __init__(
        self,
        context,
        rlogl = 22,
        zenith_min = 1.4835, # 85 degrees
        zenith_max = 2.4435, # 140 degrees
        sub_event_stream = "TTrigger"
    ):
        super(FitCutter, self).__init__(context, icetray.I3Frame.DAQ)
        self.AddParameter(
            "zenith_max",
            "Maximum zenith we consider",
            zenith_max
        )
        self.AddParameter(
            "zenith_min",
            "Minimum zenith we consider",
            zenith_min
        )
        self.AddParameter(
            "rlogl",
            "RLogL to cut on bitch",
            rlogl
        )
        self.AddParameter(
            "sub_event_stream",
            "kill me",
            sub_event_stream
        )

    def Configure(self):
        super(FitCutter, self).Configure()
        self._cut = lambda frame: fit_cut(
            frame,
            rlogl = self.GetParameter("rlogl"),
            zenith_min = self.GetParameter("zenith_min"),
            zenith_max = self.GetParameter("zenith_max")
        )
        self._sub_event_stream = self.GetParameter("sub_event_stream")

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
                elif self._cut(fr):
                    frames_to_push.append(fr)
        for fr in frames_to_push:
            self.PushFrame(fr)
        return

class HitStatisticsCutter(I3PacketModule):

    def __init__(
        self,
        context,
        z_travel = -10,
        cog_z_vertex = 110,
        cog_z_sigma = 110,
        sub_event_stream = "TTrigger"
    ):
        super(HitStatisticsCutter, self).__init__(context, icetray.I3Frame.DAQ)
        self.AddParameter(
            "z_travel",
            "Z travel",
            z_travel
        )
        self.AddParameter(
            "cog_z_vertex",
            "COG z vertex",
            cog_z_vertex
        )
        self.AddParameter(
            "cog_z_sigma",
            "COG z sigma",
            cog_z_sigma
        )
        self.AddParameter(
            "sub_event_stream",
            "kill me",
            sub_event_stream
        )

    def Configure(self):
        super(HitStatisticsCutter, self).Configure()
        self._cut = lambda frame: hit_statistics_cut(
            frame,
            z_travel = self.GetParameter("z_travel"),
            cog_z_vertex = self.GetParameter("cog_z_vertex"),
            cog_z_sigma = self.GetParameter("cog_z_sigma")
        )
        self._sub_event_stream = self.GetParameter("sub_event_stream")

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
                elif self._cut(fr):
                    frames_to_push.append(fr)
        for fr in frames_to_push:
            self.PushFrame(fr)
        return
