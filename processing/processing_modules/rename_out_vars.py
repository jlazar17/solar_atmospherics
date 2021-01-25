from icecube.common_variables import hit_statistics as hs
from icecube import dataclasses
fit_params = ['LineFit_TTParams', 'SPEFitSingle_TTFitParams', 'SPEFit4_TTFitParams', 'MPEFit_TTFitParams']
fits = ['MPEFit_TT', 'SPEFit4_TT']

def RenameOutVars(frame):
    for param in fit_params[::-1]:
        if (frame.Has(param) and not frame.Has('RLogL')):
            frame.Put('RLogL', dataclasses.I3Double(frame[param].rlogl))
    if not frame.Has('RLogL'):
        return False
    track = frame.Get('TrackFit')
    reco_zenith = track.dir.zenith
    reco_azimuth = track.dir.azimuth
    
    geometry = frame['I3Geometry']
    pulses_map = dataclasses.I3RecoPulseSeriesMap.from_frame(frame, 'TTPulses')
    z_travel   = hs.calculate_z_travel(geometry, pulses_map)
    cog_vertex = hs.calculate_cog(geometry, pulses_map)
    cogz_sigma = hs.calculate_cog_z_sigma(geometry, pulses_map)
    frame.Put('RecoZenith', dataclasses.I3Double(reco_zenith))
    frame.Put('RecoAzimuth', dataclasses.I3Double(reco_azimuth))
    frame.Put('ZTravel', dataclasses.I3Double(z_travel))
    frame.Put('COGZ', dataclasses.I3Double(cog_vertex.z))
    frame.Put('COGZSigma', dataclasses.I3Double(cogz_sigma))
    frame.Put('NuEnergy', dataclasses.I3Double(frame['I3MCWeightDict']['PrimaryNeutrinoEnergy']))
    frame.Put('NuZenith', dataclasses.I3Double(frame['I3MCWeightDict']['PrimaryNeutrinoZenith']))
    frame.Put('NuAzimuth', dataclasses.I3Double(frame['I3MCWeightDict']['PrimaryNeutrinoAzimuth']))
    frame.Put('PrimaryType', dataclasses.I3Double(frame['I3MCWeightDict']['PrimaryNeutrinoType']))
    frame.Put('oneweight', dataclasses.I3Double(frame['I3MCWeightDict']['OneWeight']))
    keys_dict = {'NuEnergy'    : frame['NuEnergy'].value,
                 'NuZenith'    : frame['NuZenith'].value,
                 'NuAzimuth'   : frame['NuAzimuth'].value,
                 'RecoZenith'    : frame['RecoZenith'].value,
                 'RecoAzimuth'   : frame['RecoAzimuth'].value,
                 'PrimaryType' : frame['PrimaryType'].value,
                 'oneweight'   : frame['oneweight'].value,
                 'ZTravel'     : frame['ZTravel'].value,
                 'COGZ'        : frame['COGZ'].value,
                 'COGZSigma'   : frame['COGZSigma'].value
                }
    frame.Put('keysDict', dataclasses.I3MapStringDouble(keys_dict))
    return True
