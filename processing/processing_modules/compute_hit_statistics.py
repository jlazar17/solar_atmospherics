from icecube.common_variables import hit_statistics as hs
from icecube import dataclasses

def ComputeHitStatistics(frame):
    if frame.Has('TTPulses'):
        geometry = frame['I3Geometry']
        pulses_map = dataclasses.I3RecoPulseSeriesMap.from_frame(frame, 'TTPulses')
        z_travel   = hs.calculate_z_travel(geometry, pulses_map)
        cog_vertex = hs.calculate_cog(geometry, pulses_map)
        cogz_sigma = hs.calculate_cog_z_sigma(geometry, pulses_map)
        frame.Put('ZTravel', dataclasses.I3Double(z_travel))
        frame.Put('COGZ', dataclasses.I3Double(cog_vertex.z))
        frame.Put('COGZSigma', dataclasses.I3Double(cogz_sigma))
    return True
