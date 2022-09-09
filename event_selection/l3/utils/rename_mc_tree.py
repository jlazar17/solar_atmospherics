def rename_mc_tree(frame):
    if frame.Has("I3MCTree_preMuonProp") and not frame.Has("I3MCTree"):
        frame["I3MCTree"] = frame["I3MCTree_preMuonProp"]
        del frame["I3MCTree_preMuonProp"]
#def renameMCTree(frame):
#    if frame.Has("I3MCTree_preMuonProp") and not frame.Has("I3MCTree"):
#        frame["I3MCTree"] = frame["I3MCTree_preMuonProp"]
#        del frame["I3MCTree_preMuonProp"]
#
