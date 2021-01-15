from icecube import dataclasses
def get_pulses(frame):
    if frame.Has('TTPulses') and frame.Has('TTPulses_NoDC'):
        TTpulses            = dataclasses.I3RecoPulseSeriesMap.from_frame(frame, 'TTPulses')
        TTpulses_NoDC       = dataclasses.I3RecoPulseSeriesMap.from_frame(frame, 'TTPulses_NoDC')
        TTnchan             = len(TTpulses)
        TTall_pulses        = [p for i,j in TTpulses for p in j]
        TTtotal_charge      = sum([p.charge for p in TTall_pulses])
        TTnchan_NoDC        = len(TTpulses_NoDC)
        TTall_pulses_NoDC   = [p for i,j in TTpulses_NoDC for p in j]
        TTtotal_charge_NoDC = sum([p.charge for p in TTall_pulses_NoDC])
        frame.Put("TTPulses_nchan"      ,dataclasses.I3Double(TTnchan))
        frame.Put("TTPulses_qtot"       ,dataclasses.I3Double(TTtotal_charge))
        frame.Put("TTPulses_NoDC_nchan" ,dataclasses.I3Double(TTnchan_NoDC))
        frame.Put("TTPulses_NoDC_qtot"  ,dataclasses.I3Double(TTtotal_charge_NoDC))

