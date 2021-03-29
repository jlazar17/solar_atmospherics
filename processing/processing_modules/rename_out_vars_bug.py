from icecube.common_variables import hit_statistics as hs
from icecube import lilliput, gulliver, gulliver_modules, paraboloid
from icecube import dataclasses, icetray

def RenameOutVars(frame, geometry, fluxname):

    if frame['I3EventHeader'].sub_event_stream!='TTrigger':
        return True

    # Get geometry from frame if none is specified
    if geometry is None:
        geometry = frame['I3Geometry']
    pulses_map = dataclasses.I3RecoPulseSeriesMap.from_frame(frame, 'TTPulses')
    z_travel   = hs.calculate_z_travel(geometry, pulses_map)
    cog_vertex = hs.calculate_cog(geometry, pulses_map)
    cogz_sigma = hs.calculate_cog_z_sigma(geometry, pulses_map)

    fitname      = 'TrackFit'
    track        = frame.Get(fitname)
    reco_zenith  = track.dir.zenith
    reco_azimuth = track.dir.azimuth
    llhparam     = frame[fitname+'FitParams']
    rlogl        = llhparam.rlogl
    
    if fluxname=='nancy':
        nu_energy  = frame['I3MCWeightDict']['PrimaryNeutrinoEnergy']
        nu_zenith  = frame['I3MCWeightDict']['PrimaryNeutrinoZenith']
        nu_azimuth = frame['I3MCWeightDict']['PrimaryNeutrinoAzimuth']
        nu_type    = frame['I3MCWeightDict']['PrimaryNeutrinoType']
        oneweight  = frame['I3MCWeightDict']['OneWeight']
        print('nancy', nu_energy, nu_zenith, nu_azimuth, nu_type, oneweight)
    #elif fluxname=='genie':
    #    nu_energy  = frame
    #    nu_zenith  = frame
    #    nu_azimuth = frame
    #    nu_type    = frame
    #    oneweight  = frame

    frame.Put('RLogL'      , dataclasses.I3Double(rlogl))
    frame.Put('RecoZenith' , dataclasses.I3Double(reco_zenith))
    frame.Put('RecoAzimuth', dataclasses.I3Double(reco_azimuth))
    frame.Put('ZTravel'    , dataclasses.I3Double(z_travel))
    frame.Put('COGZ'       , dataclasses.I3Double(cog_vertex.z))
    frame.Put('COGZSigma'  , dataclasses.I3Double(cogz_sigma))
    frame.Put('NuEnergy'   , dataclasses.I3Double(nu_energy))
    frame.Put('NuZenith'   , dataclasses.I3Double(nu_zenith))
    frame.Put('NuAzimuth'  , dataclasses.I3Double(nu_azimuth))
    frame.Put('PrimaryType', dataclasses.I3Double(nu_type))
    frame.Put('oneweight'  , dataclasses.I3Double(oneweight))
    return True
