from icecube import dataclasses
import numpy as np
def findHighChargeDOMs(frame, pulses, outputList):
    pulsemap = dataclasses.I3RecoPulseSeriesMap.from_frame(frame, pulses)
    charges = np.array([sum([p.charge for p in pulses]) for pulses in pulsemap.itervalues()])
    qmean = charges.mean()
    baddies = [om for om, q in zip(pulsemap.keys(), charges) if q/qmean > 10.]
    frame[outputList] = dataclasses.I3VectorOMKey(baddies)
