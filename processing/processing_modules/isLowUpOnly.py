from selector import selector
from icecube import dataclasses

@selector
def isLowUpOnly(frame):
    if not frame.Has('FilterMask'):
        return(False)
    filterMask = filterMask = frame['FilterMask']

    if filterMask.has_key('MuonFilter_10'):
        muonFilter=filterMask['MuonFilter_10']
        passed_muon = (muonFilter.condition_passed and muonFilter.prescale_passed)
    elif filterMask.has_key('MuonFilter_11'):
        muonFilter=filterMask['MuonFilter_11']
        passed_muon = (muonFilter.condition_passed and muonFilter.prescale_passed)
    elif filterMask.has_key('MuonFilter_12'):
        muonFilter=filterMask['MuonFilter_12']
        passed_muon = (muonFilter.condition_passed and muonFilter.prescale_passed)
    elif filterMask.has_key('MuonFilter_13'):
        muonFilter=filterMask['MuonFilter_13']
        passed_muon = (muonFilter.condition_passed and muonFilter.prescale_passed)
    else:
        print("There is a problem! If none of the above exists, you are in the future. Hihao.")
    if filterMask.has_key('LowUp_12'):
        lowUpFilter=filterMask['LowUp_12']
        frame["PoleMPEFitName"]=dataclasses.I3String("MPEFit")
        passed_lowup = (lowUpFilter.condition_passed and lowUpFilter.prescale_passed)
    elif filterMask.has_key('LowUp_13'):
        lowUpFilter=filterMask['LowUp_13']
        frame["PoleMPEFitName"]=dataclasses.I3String("MPEFit")
        passed_lowup = (lowUpFilter.condition_passed and lowUpFilter.prescale_passed)
    else:
        print("There is a problem! If none of the above exists, you are in the future. Hihao.")
    return (passed_lowup and not passed_muon)
