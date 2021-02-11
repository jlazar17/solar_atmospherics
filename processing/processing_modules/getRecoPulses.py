from icecube import dataclasses
from I3Tray import *
from icecube import icetray, dataio, dataclasses, STTools, MuonInjector
from icecube import phys_services, DomTools, simclasses, VHESelfVeto
from icecube import lilliput, gulliver, gulliver_modules, paraboloid
from icecube import linefit, MuonGun, WaveCalibrator,wavedeform
from icecube import photonics_service
from icecube import RandomStuff
from icecube.STTools.seededRT.configuration_services import I3DOMLinkSeededRTConfigurationService
from icecube import TopologicalSplitter
import icecube.lilliput.segments
from icecube import tableio, hdfwriter
from icecube import MuonGun
from icecube.icetray import I3Units
from icecube.common_variables import direct_hits
from icecube.common_variables import hit_multiplicity
from icecube.common_variables import track_characteristics

def getRecoPulses(frame,name):
        pulses = frame[name]
        if pulses.__class__ == dataclasses.I3RecoPulseSeriesMapMask:
                #cal = frame['I3Calibration']
                pulses = pulses.apply(frame)
        return pulses
