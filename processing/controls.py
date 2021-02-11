import numpy as np

from physicsconstants import PhysicsConstants
units = PhysicsConstants()

datadir = '/data/user/jlazar/solar_WIMP_v2/data/'
czens    = np.linspace(-1, 1, 150)

def process_params():
    from icecube import icetray, STTools
    from icecube.common_variables import direct_hits
    from icecube.icetray import I3Units
    from icecube.STTools.seededRT.configuration_services import I3DOMLinkSeededRTConfigurationService

    stConfigService = STTools.seededRT.configuration_services.I3DOMLinkSeededRTConfigurationService(
            allowSelfCoincidence    = False,            # Default: False.
            useDustlayerCorrection  = True,             # Default: True.
            dustlayerUpperZBoundary =    0*I3Units.m,   # Default: 0m.
            dustlayerLowerZBoundary = -150*I3Units.m,   # Default: -150m.
            ic_ic_RTTime            = 1000*I3Units.ns,  # Default: 1000m.
            ic_ic_RTRadius          =  150*I3Units.m    # Default: 150m.
            )
    dh_definitions = [direct_hits.I3DirectHitsDefinition("", -15*I3Units.ns, +200*I3Units.ns)]
    outer_string_list = [31,41,51,60,68,75,76,77,78,72,73,74,67,59,50,40,30,21,13,6,5,4,3,2,1,7,14,22]
    top_bottom_om_list = [1,60]
    deepCoreStrings = range(79,87)
    i3streams = [icetray.I3Frame.DAQ,icetray.I3Frame.Physics,icetray.I3Frame.TrayInfo, icetray.I3Frame.Simulation]
    delkeys = ['InIceRawData',
               'I3MCPulseSeriesMap',
               'I3MCPulseSeriesMapParticleIDMap',
               'CleanIceTopRawData',
               'ClusterCleaningExcludedTanks',
               #'IceTopDSTPulses',
               'IceTopPulses',
               'IceTopRawData',
               'FilterMask_NullSplit0',
               'FilterMask_NullSplit1',
               'FilterMask_NullSplit2',
               'FilterMask_NullSplit3',
               'FilterMask_NullSplit4',
               'FilterMask_NullSplit5',
               'FilterMask_NullSplit6',
               'OfflineIceTopHLCTankPulses',
               'OfflineIceTopHLCVEMPulses',
               'OfflineIceTopSLCVEMPulses',
               'TankPulseMergerExcludedTanks']
    params = {'stConfigService'    : stConfigService,
              'dh_definitions'     : dh_definitions,
              'outer_string_list'  : outer_string_list,
              'top_bottom_om_list' : top_bottom_om_list,
              'deepCoreStrings'    : deepCoreStrings,
              'i3streams'          : i3streams
             }
    return params

def weighting_params():
    params  = {}
    nevents = {
              ('nancy', 'low') : 50000.0,
              ('nancy', 'medium') : 10000.0,
              'genie' : 50000.0
             }
    descs = [
             ('ZTravel',       '<i8'),
             ('oneweight',     '<i8'),
             ('COGZ',          '<i8'),
             ('COGZSigma',     '<i8'),
             ('TrueEnergy',    '<i8'),
             ('TrueZenith',    '<i8'),
             ('TrueAzimuth',   '<i8'),
             ('PrimaryType',   '<i8'),
             ('RLogL',         '<i8'),
             ('RecoAzimuth',   '<i8'),
             ('RecoZenith',    '<i8'),
             ('QTot',          '<i8'),
             #('RecoEnergy',    '<i8'),
             ('eff_oneweight', '<i8'),
            ]
    params['nevents'] = nevents
    params['descs'] = descs
    return params

def fluxmaker_params():

    start = 2455349.5
    stop  = 2456810.5 # 4 years
    n     = 18000
    #n     = 350
    params = dict(
                  jds      = np.linspace(start, stop, n), # roughly every hour
                  azimuths = np.random.rand(n)*np.pi*2,
                  r_sun    = 6.9e10, # cm
                 )
    return params
