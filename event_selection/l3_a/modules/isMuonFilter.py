from selector import selector
from icecube import dataclasses

@selector
def IsMuonFilter(frame):
        if not frame.Has('FilterMask'):
                return(False)
        filterMask = filterMask = frame['FilterMask']

        if filterMask.has_key('MuonFilter_10'):
                muonFilter=filterMask['MuonFilter_10']
                if not frame.Has('PoleMPEFitName'):
                    frame["PoleMPEFitName"]=dataclasses.I3String("MPEFit_SLC")
                return(muonFilter.condition_passed and muonFilter.prescale_passed)
        elif filterMask.has_key('MuonFilter_11'):
                muonFilter=filterMask['MuonFilter_11']
                if not frame.Has('PoleMPEFitName'):
                    frame["PoleMPEFitName"]=dataclasses.I3String("MPEFit")
                return(muonFilter.condition_passed and muonFilter.prescale_passed)
        elif filterMask.has_key('MuonFilter_12'):
                muonFilter=filterMask['MuonFilter_12']
                if not frame.Has('PoleMPEFitName'):
                    frame["PoleMPEFitName"]=dataclasses.I3String("MPEFit")
                return(muonFilter.condition_passed and muonFilter.prescale_passed)
        elif filterMask.has_key('MuonFilter_13'):
                muonFilter=filterMask['MuonFilter_13']
                if not frame.Has('PoleMPEFitName'):
                    frame["PoleMPEFitName"]=dataclasses.I3String("MPEFit")
                return(muonFilter.condition_passed and muonFilter.prescale_passed)
        else:
                print("There is a problem! If none of the above exists, you are in the future. Hihao.")
                return(False)
