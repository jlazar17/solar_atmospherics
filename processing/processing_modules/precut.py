from selector import selector
from icecube import dataclasses, icetray
# Perform a set of very simple quality cuts to reduce data rate:
# For events whose cos(reconstructed zenith)>.2, make a qtot cut similar to the on used in the filter
# For all up-going events, make a cut demanding that the charge-weighted distance be smaller than
# 200 meters or the total charge be greater than 100 p.e.

@selector
def precut(frame):
    PoleMPEFitName=frame['PoleMPEFitName'].value
    if(not frame.Has(PoleMPEFitName) or not frame.Has(PoleMPEFitName+"_AvgDistQ") or not frame.Has(SRTInIcePulses_NoDC_Qtot)):
        return(False)

    track = frame.Get(PoleMPEFitName)
    qtot = frame.Get(SRTInIcePulses_NoDC_Qtot).value
    qwDist = frame.Get(PoleMPEFitName+"_AvgDistQ").value

    if(track.dir.zenith > (math.pi / 2.)):
        if(qtot < 100. and qwDist > 200.):
            return(False)
        return(True)
    else:
        c = math.cos(track.dir.zenith)
        lq = 0
        if(qtot > 0.0):
            lq = math.log10(qtot)
        if(c > .2):
            return(lq >= (0.6*(c-0.5) + 2.5))
        return(True)

