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
from I3Tray import NaN
from icecube.common_variables import hit_statistics as hs
from icecube import lilliput, gulliver, gulliver_modules, paraboloid
from icecube import dataclasses, icetray

def RenameOutVars(frame, geometry, fluxname, corsika_set):

    if frame['I3EventHeader'].sub_event_stream!='TTrigger':
        return True

    # Get geometry from frame if none is specified
    if geometry is None:
        geometry = frame['I3Geometry']

    # Compute variables which are common across all file types
    pulses_map = dataclasses.I3RecoPulseSeriesMap.from_frame(frame, 'TTPulses')
    z_travel   = hs.calculate_z_travel(geometry, pulses_map)
    cog_vertex = hs.calculate_cog(geometry, pulses_map)
    cogz_sigma = hs.calculate_cog_z_sigma(geometry, pulses_map)
    qtot       = hs.calculate_q_tot_pulses(geometry, pulses_map)
    fitname      = 'MPEFit_TT'
    track        = frame.Get(fitname)
    reco_zenith  = track.dir.zenith
    reco_azimuth = track.dir.azimuth
    llhparam     = frame[fitname+'FitParams']
    rlogl        = llhparam.rlogl

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
        
    frame.Put('RLogL',        dataclasses.I3Double(rlogl))
    frame.Put('RecoZenith',   dataclasses.I3Double(reco_zenith))
    frame.Put('RecoAzimuth',  dataclasses.I3Double(reco_azimuth))
    frame.Put('ZTravel',      dataclasses.I3Double(z_travel))
    frame.Put('COGZ',         dataclasses.I3Double(cog_vertex.z))
    frame.Put('COGZSigma'   , dataclasses.I3Double(cogz_sigma))
    frame.Put('TrueEnergy'  , dataclasses.I3Double(true_energy))
    frame.Put('TrueZenith'  , dataclasses.I3Double(true_zenith))
    frame.Put('TrueAzimuth' , dataclasses.I3Double(true_azimuth))
    frame.Put('PrimaryType' , dataclasses.I3Double(ptype))
    frame.Put('oneweight'   , dataclasses.I3Double(oneweight))
    frame.Put('QTot'        , dataclasses.I3Double(qtot))

    return True
