from icecube import dataclasses
def add_energy(frame):
    if frame.Has('I3MCTree'):
        frame.Put("",dataclasses.get_most_energetic_muon(frame['I3MCTree']).energy)

