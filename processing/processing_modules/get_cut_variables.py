from icecube.icetray import I3Units
from icecube import dataclasses
from icecube.common_variables import direct_hits
from icecube.common_variables import hit_multiplicity
from icecube.common_variables import track_characteristics

def get_cut_variables(frame):
    if frame.Has('TTPulses') and frame.Has('TrackFit'):
        geometry                     = frame["I3Geometry"]
        particle                     = frame["TrackFit"]
        pulses_map                   = dataclasses.I3RecoPulseSeriesMap.from_frame(frame, 'TTPulses')
        hit_multiplicity_values      = hit_multiplicity.calculate_hit_multiplicity(geometry, pulses_map)
        direct_hits_map              = direct_hits.calculate_direct_hits(geometry, pulses_map, particle)
        cylinder_radius              = 150*I3Units.m
        track_characteristics_values = track_characteristics.calculate_track_characteristics(geometry,pulses_map,particle,cylinder_radius)

        frame.Put("dir_N_D_strings",     dataclasses.I3Double(direct_hits_map['D'].n_dir_strings))
        frame.Put("dir_N_D_doms",        dataclasses.I3Double(direct_hits_map['D'].n_dir_doms))
        frame.Put("dir_N_D_pulses",      dataclasses.I3Double(direct_hits_map['D'].n_dir_pulses))
        frame.Put("dir_L_D",             dataclasses.I3Double(direct_hits_map['D'].dir_track_length))
        frame.Put("dir_S_D",             dataclasses.I3Double(direct_hits_map['D'].dir_track_hit_distribution_smoothness))
        frame.Put("dir_N_B_strings",     dataclasses.I3Double(direct_hits_map['B'].n_dir_strings))
        frame.Put("dir_N_B_doms",        dataclasses.I3Double(direct_hits_map['B'].n_dir_doms))
        frame.Put("dir_N_B_pulses",      dataclasses.I3Double(direct_hits_map['B'].n_dir_pulses))
        frame.Put("dir_L_B",             dataclasses.I3Double(direct_hits_map['B'].dir_track_length))
        frame.Put("dir_S_B",             dataclasses.I3Double(direct_hits_map['B'].dir_track_hit_distribution_smoothness))
        frame.Put("trackfit_separation", dataclasses.I3Double(track_characteristics_values.track_hits_separation_length))
        return(True)

