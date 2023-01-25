from icecube import icetray, STTools
from icecube.icetray import I3Units
from icecube.STTools.seededRT.configuration_services import I3DOMLinkSeededRTConfigurationService
from icecube.common_variables import direct_hits

# Define a timewindow for getting the directhit and hit_multiplicity variables
dh_definitions = [direct_hits.I3DirectHitsDefinition("", -15*I3Units.ns, +200*I3Units.ns)]

stConfigService = STTools.seededRT.configuration_services.I3DOMLinkSeededRTConfigurationService(
                        allowSelfCoincidence    = False,            # Default: False.
                        useDustlayerCorrection  = True,             # Default: True.
                        dustlayerUpperZBoundary =    0*I3Units.m,   # Default: 0m.
                        dustlayerLowerZBoundary = -150*I3Units.m,   # Default: -150m.
                        ic_ic_RTTime            = 1000*I3Units.ns,  # Default: 1000m.
                        ic_ic_RTRadius          =  150*I3Units.m    # Default: 150m.
                       )

#i3streams = [icetray.I3Frame.Physics,icetray.I3Frame.TrayInfo]
i3streams = [icetray.I3Frame.DAQ,icetray.I3Frame.Physics,icetray.I3Frame.TrayInfo, icetray.I3Frame.Simulation]
outkeys = ['CVStatistics',
           'CVMultiplicity', 
           'MPEFit', 
           'MuExEnergy',
           'MuExZenith',
           'MuExAzimuth', 
           'NuEnergy', 
           'NuZenith',
           'NuAzimuth',
           'oneweight',
           'MuEx'
          ]

outer_string_list = [31,41,51,60,68,75,76,77,78,72,73,74,67,59,50,40,30,21,13,6,5,4,3,2,1,7,14,22]
top_bottom_om_list = [1,60]
deepCoreStrings = range(79,87)

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
