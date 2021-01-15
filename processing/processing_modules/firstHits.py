from icecube import dataclasses

def firstHits(frame,inputPulses,outputPulses):
    # This function makes a mask of only the first pulses seen on every DOM.
    # see http://software.icecube.wisc.edu/offline_trunk/projects/dataclasses/masks.html
    if(frame.Has(inputPulses)):
        frame.Put(outputPulses,dataclasses.I3RecoPulseSeriesMapMask(frame,inputPulses,lambda OM,id,i3P: id==0))
    else:
        return True

