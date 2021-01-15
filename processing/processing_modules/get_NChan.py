from icecube import icetray
# This is needed for Paraboloid sigma corrector.
def get_NChan(frame):
    if frame.Has('TTPulses_hm'):
        pulse_hm = frame.Get('TTPulses_hm')
        frame.Put("NChanSource",icetray.I3Int(pulse_hm.n_hit_doms))
    else:
        return
