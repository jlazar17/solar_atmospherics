from selector import selector

#the existance of an I3MCTree is usually sufficient to distinguish simulated data
@selector
def is_simulation(frame):
    if frame.Has("I3MCTree") or frame.Has("I3MCTree_preMuonProp"):
        return True

