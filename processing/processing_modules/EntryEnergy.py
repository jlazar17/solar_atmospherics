from final_selection import finalSample
from I3Tray import NaN
from icecube import dataclasses
from is_simulation import is_simulation
def EntryEnergy(frame):
    if not (finalSample & is_simulation)(frame):
        return
    mcTree = frame["I3MCTree"]
    #locate the highest energy muon
    muon = None
    for p in mcTree:
        if p.type in [dataclasses.I3Particle.ParticleType.MuPlus,
                      dataclasses.I3Particle.ParticleType.MuMinus]:
            if(muon==None):
                muon = p
            elif(p.energy>muon.energy):
                muon = p
            #break

    #print "Muon energy is",muon.energy
    #sum all losses before the muon enters the detector
    timeWindow = frame["ContainedTimeRange"]
    #print "Contained time window is [",timeWindow.start,',',timeWindow.stop,']'
    containedEnergyMC = 0.
    earlyLosses = 0.
    for p in frame["I3MCTree"]:
        if p.shape == dataclasses.I3Particle.ParticleShape.Dark:
            continue
        if p.type in [dataclasses.I3Particle.ParticleType.MuPlus,
                      dataclasses.I3Particle.ParticleType.MuMinus,
                      dataclasses.I3Particle.ParticleType.TauPlus,
                      dataclasses.I3Particle.ParticleType.TauMinus,
                      dataclasses.I3Particle.ParticleType.NuE,
                      dataclasses.I3Particle.ParticleType.NuEBar,
                      dataclasses.I3Particle.ParticleType.NuMu,
                      dataclasses.I3Particle.ParticleType.NuMuBar,
                      dataclasses.I3Particle.ParticleType.NuTau,
                      dataclasses.I3Particle.ParticleType.NuTauBar,
                     ]:
            continue # skip tracks for now
        if p.location_type != dataclasses.I3Particle.LocationType.InIce:
            continue
        if p.time > timeWindow.stop:
            continue
        if p.time < timeWindow.start:
            earlyLosses += p.energy
            continue
        containedEnergyMC += p.energy
        if muon is None:
            print('No muon, could be NC?')
            if not frame.Has("MuonEntryEnergy"):
                frame["MuonEntryEnergy"]=dataclasses.I3Double(NaN)
    '''
    else:
            frame["MuonEntryEnergy"]=dataclasses.I3Double(muon.energy-earlyLosses)
    frame["MuonEnergyLoss"]=dataclasses.I3Double(containedEnergyMC)
    lengthInDetector=dataclasses.I3Constants.c*(timeWindow.stop-timeWindow.start)/icetray.I3Units.m
    frame["MuonLengthInDetector"]=dataclasses.I3Double(lengthInDetector)
    frame["MuonAverage_dEdX"]=dataclasses.I3Double(containedEnergyMC/lengthInDetector)
    '''

