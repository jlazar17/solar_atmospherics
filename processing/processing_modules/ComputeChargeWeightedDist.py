from icecube import icetray, dataclasses,phys_services
from getRecoPulses import getRecoPulses

def ComputeChargeWeightedDist(frame, Pulses, Track):
    if(not frame.Stop==icetray.I3Frame.Physics):
        return
    if(not frame.Has(Pulses)):
        return
    if(not frame.Has(Track)):
        return
    pulses=getRecoPulses(frame,Pulses)
    track=frame[Track]
    if(track.__class__==dataclasses.I3String):
        Track=track.value
        if(not frame.Has(Track)):
            return
        track=frame[Track]
    geo=frame.Get('I3Geometry')
    omgeo=geo.omgeo
    Qtot=0
    AvgDistQ=0
    for dom in pulses:
        DomPosition=omgeo[dom[0]].position
        Dist=phys_services.I3Calculator.closest_approach_distance(track,DomPosition)
        Qdom=0
        for pulse in dom[1]:
            Qdom+=pulse.charge
        Qtot+=Qdom
        AvgDistQ+=Dist*Qdom
    if(Qtot==0):
        AvgDistQ=NaN
    else:
        AvgDistQ/=Qtot
    if not frame.Has(Track+'_AvgDistQ'):
        frame.Put(Track+"_AvgDistQ",dataclasses.I3Double(AvgDistQ))
    if not frame.Has(Pulses+"_Qtot"):
        frame.Put(Pulses+"_Qtot",dataclasses.I3Double(Qtot))

