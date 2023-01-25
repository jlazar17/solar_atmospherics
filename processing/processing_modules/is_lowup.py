from selector import selector
from icecube import dataclasses

@selector
def IsLowUp(frame):
    if not frame.Has('FilterMask'):
        return(False)
    filter_mask = filter_mask = frame['FilterMask']

    if filter_mask.has_key('LowUp_12'):
        if not frame.Has("PoleMPEFitName"):
            frame["PoleMPEFitName"]=dataclasses.I3String("MPEFit")
        lowup_filter=filter_mask['LowUp_12']
        passed_lowup = (lowup_filter.condition_passed and lowup_filter.prescale_passed)
    elif filter_mask.has_key('LowUp_13'):
        if not frame.Has("PoleMPEFitName"):
            frame["PoleMPEFitName"]=dataclasses.I3String("MPEFit")
        lowup_filter=filter_mask['LowUp_13']
        passed_lowup = (lowup_filter.condition_passed and lowup_filter.prescale_passed)
    else:
        print("There is a problem! If none of the above exists, you are in the future. Hihao.")
    return passed_lowup
