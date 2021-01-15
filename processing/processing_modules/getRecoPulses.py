from icecube import dataclasses

def getRecoPulses(frame,name):
    pulses = frame[name]
    if pulses.__class__ == dataclasses.I3RecoPulseSeriesMapMask:
	cal = frame['I3Calibration']
	pulses = pulses.apply(frame)
    return pulses

