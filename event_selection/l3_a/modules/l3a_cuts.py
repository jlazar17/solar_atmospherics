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
        print(f"Failed cuz cog_z_vertex")
        return False
    if stats.cog_z_sigma >= cog_z_sigma:
        print(f"Failed cuz cog_z_sigma")
        return False
    if stats.z_travel <= z_travel:
        print("Failed due to z_travel")
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
            print(f"We passed {fit_name}")
            fit = proposed_fit
            params = frame[fit_name + "FitParams"]
        else:
            print(f"We did NOT pass {fit_name}")
    if fit is None:
        print("Frown")
        return False
    else:
        if params.rlogl > rlogl:
            return False
        if fit.dir.zenith < zenith_min or fit.dir.zenith > zenith_max:
            return False
        return True
