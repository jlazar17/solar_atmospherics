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

def prepare_l3_a_vars(frame):
    
    if frame['I3EventHeader'].sub_event_stream!='TTrigger':
        return True

    # Check whether our event passed ANY of the reconstructions
    # LineFit doesn't count cuz it literally doesn't have a rlogl
    best_fit = ""
    best_idx = 0
    fit_names = ["SPEFitSingle_TT", "SPEFit4_TT", "MPEFit_TT"]
    for idx,  fit_name in enumerate(fit_names):
        fit = frame[fit_name]
        if str(fit.fit_status)=="OK":
            best_fit = fit_name
            best_idx = idx
    # Cut the frame if it literally didn't pass anything.
    # I don't know if this is possible
    if not best_fit:
        return False
    best_fit_params = best_fit + "FitParams"

    # HitStats
    hit_stats = frame.Get('TTPulses_HitStatistics')
    z_travel = hit_stats.z_travel
    cog_vertex = hit_stats.cog
    cogz_sigma = hit_stats.cog_z_sigma
    # Reco
    fit = frame[best_fit]
    rlogl = frame[best_fit_params].rlogl
    zenith_reco = fit.dir.zenith
    azimuth_reco = fit.dir.azimuth

    # Truth
    # This information varies depending on the the simset
    if frame["Simname"]=='nancy':
        e_true= frame['I3MCWeightDict']['PrimaryNeutrinoEnergy']
        zenith_true = frame['I3MCWeightDict']['PrimaryNeutrinoZenith']
        azimuth_true = frame['I3MCWeightDict']['PrimaryNeutrinoAzimuth']
        ptype = frame['I3MCWeightDict']['PrimaryNeutrinoType']
        oneweight = frame['I3MCWeightDict']['OneWeight']

    elif frame["Simname"]=='genie':
        e_true = frame['I3MCTree'][0].energy
        zenith_true = frame['I3MCTree'][0].dir.zenith
        azimuth_true = frame['I3MCTree'][0].dir.azimuth
        ptype = frame['I3MCTree'][0].pdg_encoding
        oneweight = frame['I3MCWeightDict']['OneWeight']
        
    elif frame["Simname"]=='corsika':
        from .weight_tool import weighter_corsika
        weighter_corsika(frame)
        energy = frame['CorsikaWeightMap']['PrimaryEnergy']
        ptype = frame['CorsikaWeightMap']['PrimaryType']
        e_true  = dataclasses.get_most_energetic_muon(frame['I3MCTree']).energy
        zenith_true = dataclasses.get_most_energetic_muon(
            frame['I3MCTree']
        ).dir.zenith
        azimuth_true = dataclasses.get_most_energetic_muon(
            frame['I3MCTree']
        ).dir.azimuth
        oneweight = frame.Get('Weight')
    # Thre is no truth in data, so we save NaN
    else:
        e_true = np.nan
        zenith_true = np.nan
        azimuth_true = np.nan
        ptype = np.nan
        oneweight = np.nan

    frame.Put('ZTravel', dataclasses.I3Double(z_travel))
    frame.Put('COGZVertex', dataclasses.I3Double(cog_vertex.z))
    frame.Put('COGZSigma' , dataclasses.I3Double(cogz_sigma))
    frame.Put("BestFitIdx", dataclasses.I3Double(best_idx))
    frame.Put('RLogL', dataclasses.I3Double(rlogl))
    frame.Put('ZenithReco', dataclasses.I3Double(zenith_reco))
    frame.Put('AzimuthReco', dataclasses.I3Double(azimuth_reco))
    frame.Put('ETrue'  , dataclasses.I3Double(e_true))
    frame.Put('ZenithTrue'  , dataclasses.I3Double(zenith_true))
    frame.Put('AzimuthTrue' , dataclasses.I3Double(azimuth_true))
    frame.Put('PrimaryType' , dataclasses.I3Double(ptype))
    frame.Put('OneWeight'   , dataclasses.I3Double(oneweight))
    return True

def rename_out_vars(frame):

    if frame['I3EventHeader'].sub_event_stream!='TTrigger':
        return True

    # Compute variables which are common across all file types
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
    EDir         = frame.Get('MPEFit_DirectHitsClassE')

    

    # Compute MC variables that vary from simulation to simulation
    if fluxname=='nancy':
        e_true  = frame['I3MCWeightDict']['PrimaryNeutrinoEnergy']
        zenith_true  = frame['I3MCWeightDict']['PrimaryNeutrinoZenith']
        azimuth_true = frame['I3MCWeightDict']['PrimaryNeutrinoAzimuth']
        ptype        = frame['I3MCWeightDict']['PrimaryNeutrinoType']
        oneweight    = frame['I3MCWeightDict']['OneWeight']

    elif fluxname=='genie':
        e_true  = frame['I3MCTree'][0].energy
        zenith_true  = frame['I3MCTree'][0].dir.zenith
        azimuth_true = frame['I3MCTree'][0].dir.azimuth
        ptype        = frame['I3MCTree'][0].pdg_encoding
        oneweight    = frame['I3MCWeightDict']['OneWeight']
        
    elif fluxname=='corsika':
        from .weight_tool import weighter_corsika
        weighter_corsika(frame)
        energy       = frame['CorsikaWeightMap']['PrimaryEnergy']
        ptype        = frame['CorsikaWeightMap']['PrimaryType']
        e_true  = dataclasses.get_most_energetic_muon(frame['I3MCTree']).energy
        zenith_true  = dataclasses.get_most_energetic_muon(frame['I3MCTree']).dir.zenith
        azimuth_true = dataclasses.get_most_energetic_muon(frame['I3MCTree']).dir.azimuth
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
    frame.Put('QTot'        , dataclasses.I3Double(qtot))
    # Put MC informtion in simulation sets
    if fluxname in "corsika genie nancy".split():
        frame.Put('TrueEnergy'  , dataclasses.I3Double(e_true))
        frame.Put('TrueZenith'  , dataclasses.I3Double(zenith_true))
        frame.Put('TrueAzimuth' , dataclasses.I3Double(azimuth_true))
        frame.Put('PrimaryType' , dataclasses.I3Double(ptype))
        frame.Put('oneweight'   , dataclasses.I3Double(oneweight))

    return True
