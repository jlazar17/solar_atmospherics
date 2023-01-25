from icecube import icetray

#In a fair number of events TopologicalSplitting does nothing, so we can save
#computation by just copying the results from the L2a reconstructions
class SamePulseChecker(icetray.I3PacketModule):
        copyKeys = {"MPEFit_SLC":"MPEFit_TT","MPEFit_SLCFitParams":"MPEFit_TTFitParams",
                "SPEFit4_SLC":"SPEFit4_TT","SPEFit4_SLCFitParams":"SPEFit4_TTFitParams",
                "SPEFitSingle_SLC":"SPEFitSingle_TT","SPEFitSingle_SLCFitParams":"SPEFitSingle_TTFitParams",
                "LineFit_SLC":"LineFit_TT"}

        def __init__(self, ctx):
                icetray.I3PacketModule.__init__(self, ctx, icetray.I3Frame.DAQ)
                self.oldPulseName = 'SRTInIcePulses'
                self.newPulseName = "TTPulses"
                self.AddOutBox("OutBox")

        def Configure(self):
                pass
