def CutHighEnergy(frame):
    if frame['I3MCWeightDict']['PrimaryNeutrinoEnergy']>100:
        return False
    else:
        return True
