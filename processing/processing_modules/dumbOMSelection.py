from icecube import dataclasses
from getRecoPulses import getRecoPulses

def dumbOMSelection(frame, pulses, output, omittedStrings, IfCond):
	if not IfCond:
		return
	if not frame.Has(pulses):
		return
	ps = getRecoPulses(frame,pulses)
	nps = dataclasses.I3RecoPulseSeriesMap()
	for om in ps.keys():
		if not om.string in omittedStrings:
			nps[om] = ps[om]
	frame.Put(output,nps)

