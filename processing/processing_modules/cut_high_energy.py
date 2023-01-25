def CutHighEnergy(frame):
    primary_nuetrino = frame['I3MCTree'][0]
    if primary_nuetrino.energy>100:
        return False
    else:
        return True
