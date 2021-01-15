from icecube import dataclasses
from controls import outer_string_list, top_bottom_om_list
def outer_charge(frame):
    if frame.Has('TTPulses'):
        TTpulses = dataclasses.I3RecoPulseSeriesMap.from_frame(frame, 'TTPulses')
        Radial_charges = 0
        TB_charges = 0
        for omkey, pulse, in TTpulses:
            if omkey[0] in outer_string_list:
                for p in pulse:
                    Radial_charges += p.charge
            if omkey[1] in top_bottom_om_list and not omkey[0] in outer_string_list:
                for p in pulse:
                    TB_charges += p.charge
        TTPulses_total_outer_charge = Radial_charges+TB_charges
        all_TTpulses = [p for i,j in TTpulses for p in j]
        total_TTcharge = sum([p.charge for p in all_TTpulses])
        frame.Put("TTPulses_total_outer_charge",dataclasses.I3Double(TTPulses_total_outer_charge))
        frame.Put("TTPulses_outer_charge_ratio",dataclasses.I3Double(TTPulses_total_outer_charge/total_TTcharge))

