from icecube import dataclasses
def true_trackfit(frame):
    if frame.Has('I3MCTree'):
        # We want the true trajectory of the muon for this. But if there is no muon (ie NuGen Nue simulation), then take the cascade
        try:
                track = dataclasses.I3Particle(dataclasses.get_most_energetic_muon(frame['I3MCTree']))
        except:
                track = dataclasses.I3Particle(dataclasses.get_most_energetic_cascade(frame['I3MCTree']))
        frame.Put('true_trackfit',track)
    else:
        return

