from icecube import dataclasses
from I3Tray import NaN
# Find the muon we will use for weighting
def getWeightingCandidate(frame):
    WeightingCandidatesThisRound=0
    if frame.Has('I3MCTree'):
        for i in frame['I3MCTree']:
            if((i.type==i.ParticleType.MuMinus) or (i.type==i.ParticleType.MuPlus)):
                WeightingCandidatesThisRound+=1
                Candidate=i
        if(WeightingCandidatesThisRound==1):
            frame.Put("WeightingMuon",dataclasses.I3Particle(Candidate))
        else:
            print("Warning! Multiple weighting candidates found! Storing none of them")
            print("This is fine for NuGen, NuFSGen shouldn't see this message Since there is always only one muon.")

