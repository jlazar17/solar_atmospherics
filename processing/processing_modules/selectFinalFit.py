from icecube import dataclasses, icetray

def selectFinalFit(frame):
    fits=["MPEFit_TT","SPEFit4_TT","SPEFitSingle_TT","LineFit_TT"]
    resultName="TrackFit"
    result=None
    params=None
    for fitName in fits:
        if(not frame.Has(fitName)):
            continue
        fit=frame.Get(fitName)
        if(fit.fit_status==dataclasses.I3Particle.OK):
            frame.Put(resultName,fit)
            frame.Put(resultName+"Fallback",icetray.I3Int(fits.index(fitName)))
            #print(fitName)
            if(frame.Has(fitName+"FitParams")):
                frame.Put(resultName+"FitParams",frame.Get(fitName+"FitParams"))
            break
    if(not frame.Has(resultName+"Fallback")):
        frame.Put(resultName+"Fallback",icetray.I3Int(len(fits)))
