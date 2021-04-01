    # There is a difference in terminology between 2011 and all the other years.
def get_pulse_names(infile):
    if "NuFSGen2011" in infile or "IceCube/2011" in infile or "IC86NuFS" in infile:
        print('The year is 2011')
        if 'pass2' in infile:
            print('And processing Pass2')
            InIcePulses                             = "InIcePulses"
            SRTInIcePulses                          = "SRTInIcePulses"
            SRTInIcePulses_NoDC_Qtot        = "SRTInIcePulses_NoDC_Qtot"
            SRTInIcePulses_NoDC             = "SRTInIcePulses_NoDC"
        else:
            InIcePulses                             = "OfflinePulses"
            SRTInIcePulses                          = "SRTInIcePulses"
            SRTInIcePulses_NoDC_Qtot        = "SRTInIcePulses_NoDC_Qtot"
            SRTInIcePulses_NoDC             = "SRTInIcePulses_NoDC"
    else:
        InIcePulses                                         = "InIcePulses"
        SRTInIcePulses                                      = "SRTInIcePulses"
        SRTInIcePulses_NoDC_Qtot            = "SRTInIcePulses_NoDC_Qtot"
        SRTInIcePulses_NoDC                         = "SRTInIcePulses_NoDC"
    return InIcePulses, SRTInIcePulses, SRTInIcePulses_NoDC_Qtot, SRTInIcePulses_NoDC
