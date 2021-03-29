from icecube.icetray import I3Frame
from I3Tray import *
from icecube import icetray, dataio, dataclasses
from icecube.common_variables import direct_hits
from icecube.common_variables import hit_multiplicity
from icecube.icetray import I3Units
from icecube.common_variables import track_characteristics
from icecube import phys_services

from icecube import VHESelfVeto, DomTools

from icecube import weighting
from icecube.weighting.weighting import from_simprod
from icecube.weighting.fluxes import GaisserH3a
from icecube import truncated_energy
from icecube.common_variables import hit_statistics as hs
from icecube import lilliput, gulliver, gulliver_modules, paraboloid
from icecube import dataclasses, icetray

from solar_common import opening_angle

def RenameOutVars(frame, geometry, fluxname, corsika_set):

    if frame['I3EventHeader'].sub_event_stream!='TTrigger':
        return True

    # Get geometry from frame if none is specified
    if geometry is None:
        geometry = frame['I3Geometry']

    # Compute variables which are common across all file types
    pulses_map   = dataclasses.I3RecoPulseSeriesMap.from_frame(frame, 'TTPulses')
    hit_stats    = frame.Get('TTPulses_HitStatistics')
    z_travel     = hit_stats.z_travel
    cog_vertex   = hit_stats.cog
    cogz_sigma   = hit_stats.cog_z_sigma
    qtot         = hit_stats.q_tot_pulses
    t_extent     = hit_stats.max_pulse_time-hit_stats.min_pulse_time
    fitname      = 'MPEFit_TT'
    track        = frame.Get(fitname)
    reco_zenith  = track.dir.zenith
    reco_azimuth = track.dir.azimuth
    SPEtrack     = frame.Get('SPEFit4_TT')
    ang_sep      = opening_angle(reco_zenith, reco_azimuth, SPEtrack.dir.zenith, SPEtrack.dir.azimuth)
    llhparam     = frame[fitname+'FitParams']
    bayesratio   = frame['MPEFit_TT_BayesianFitParams'].logl/llhparam.logl
    rlogl        = llhparam.rlogl
    ADir         = frame.Get('MPEFit_DirectHitsClassA')
    BDir         = frame.Get('MPEFit_DirectHitsClassB')
    CDir         = frame.Get('MPEFit_DirectHitsClassC')
    DDir         = frame.Get('MPEFit_DirectHitsClassD')
    EDir         = frame.Get('MPEFit_DirectHitsClassE')

    

    # Compute variables that vary from file to file
    if fluxname=='nancy':
        true_energy  = frame['I3MCWeightDict']['PrimaryNeutrinoEnergy']
        true_zenith  = frame['I3MCWeightDict']['PrimaryNeutrinoZenith']
        true_azimuth = frame['I3MCWeightDict']['PrimaryNeutrinoAzimuth']
        ptype        = frame['I3MCWeightDict']['PrimaryNeutrinoType']
        oneweight    = frame['I3MCWeightDict']['OneWeight']

    elif fluxname=='genie':
        true_energy  = frame['I3MCTree'][0].energy
        true_zenith  = frame['I3MCTree'][0].dir.zenith
        true_azimuth = frame['I3MCTree'][0].dir.azimuth
        ptype        = frame['I3MCTree'][0].pdg_encoding
        oneweight    = frame['I3MCWeightDict']['OneWeight']
        
    elif fluxname=='corsika':
        from weight_tool import weighter_corsika
        weighter_corsika(frame)
        energy       = frame['CorsikaWeightMap']['PrimaryEnergy']
        ptype        = frame['CorsikaWeightMap']['PrimaryType']
        true_energy  = dataclasses.get_most_energetic_muon(frame['I3MCTree']).energy
        true_zenith  = dataclasses.get_most_energetic_muon(frame['I3MCTree']).dir.zenith
        true_azimuth = dataclasses.get_most_energetic_muon(frame['I3MCTree']).dir.azimuth
        oneweight    = frame.Get('Weight')

    # Write all direct hit information
    frame.Put('LDir_A',      dataclasses.I3Double(ADir.dir_track_length))
    frame.Put('NDirPulse_A', dataclasses.I3Double(ADir.n_dir_pulses))
    frame.Put('NDirDOM_A',   dataclasses.I3Double(ADir.n_dir_doms))
    frame.Put('NDirStr_A',   dataclasses.I3Double(ADir.n_dir_strings))
    frame.Put('LDir_B',      dataclasses.I3Double(BDir.dir_track_length))
    frame.Put('NDirPulse_B', dataclasses.I3Double(BDir.n_dir_pulses))
    frame.Put('NDirDOM_B',   dataclasses.I3Double(BDir.n_dir_doms))
    frame.Put('NDirStr_B',   dataclasses.I3Double(BDir.n_dir_strings))
    frame.Put('LDir_C',      dataclasses.I3Double(CDir.dir_track_length))
    frame.Put('NDirPulse_C', dataclasses.I3Double(CDir.n_dir_pulses))
    frame.Put('NDirDOM_C',   dataclasses.I3Double(CDir.n_dir_doms))
    frame.Put('NDirStr_C',   dataclasses.I3Double(CDir.n_dir_strings))
    frame.Put('LDir_D',      dataclasses.I3Double(DDir.dir_track_length))
    frame.Put('NDirPulse_D', dataclasses.I3Double(DDir.n_dir_pulses))
    frame.Put('NDirDOM_D',   dataclasses.I3Double(DDir.n_dir_doms))
    frame.Put('NDirStr_D',   dataclasses.I3Double(DDir.n_dir_strings))
    frame.Put('LDir_E',      dataclasses.I3Double(EDir.dir_track_length))
    frame.Put('NDirPulse_E', dataclasses.I3Double(EDir.n_dir_pulses))
    frame.Put('NDirDOM_E',   dataclasses.I3Double(EDir.n_dir_doms))
    frame.Put('NDirStr_E',   dataclasses.I3Double(EDir.n_dir_strings))
        
    frame.Put('RLogL',        dataclasses.I3Double(rlogl))
    frame.Put('TExtent',      dataclasses.I3Double(t_extent))
    frame.Put('BayesRatio',   dataclasses.I3Double(bayesratio))
    frame.Put('RecoZenith',   dataclasses.I3Double(reco_zenith))
    frame.Put('RecoAzimuth',  dataclasses.I3Double(reco_azimuth))
    frame.Put('RecoAngSep',   dataclasses.I3Double(ang_sep))
    frame.Put('ZTravel',      dataclasses.I3Double(z_travel))
    frame.Put('COGX',         dataclasses.I3Double(cog_vertex.x))
    frame.Put('COGY',         dataclasses.I3Double(cog_vertex.y))
    frame.Put('COGZ',         dataclasses.I3Double(cog_vertex.z))
    frame.Put('COGZSigma'   , dataclasses.I3Double(cogz_sigma))
    frame.Put('TrueEnergy'  , dataclasses.I3Double(true_energy))
    frame.Put('TrueZenith'  , dataclasses.I3Double(true_zenith))
    frame.Put('TrueAzimuth' , dataclasses.I3Double(true_azimuth))
    frame.Put('PrimaryType' , dataclasses.I3Double(ptype))
    frame.Put('oneweight'   , dataclasses.I3Double(oneweight))
    frame.Put('QTot'        , dataclasses.I3Double(qtot))

    return True
