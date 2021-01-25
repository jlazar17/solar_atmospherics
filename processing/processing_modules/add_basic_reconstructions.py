from icecube import lilliput, linefit
from selectFinalFit import selectFinalFit

def add_basic_reconstructions(tray,suffix,pulses,condition):
    tray.AddSegment(linefit.simple,"LineFit"+suffix,
        If=condition,
        inputResponse=pulses,
        fitName="LineFit"+suffix
        )

    tray.AddSegment(lilliput.segments.I3SinglePandelFitter,"SPEFitSingle"+suffix,
        If=condition,
        domllh="SPE1st",
        pulses=pulses,
        seeds=["LineFit"+suffix],
        )

    tray.AddSegment(lilliput.segments.I3IterativePandelFitter,"SPEFit4"+suffix,
        If=condition,
        domllh="SPE1st",
        n_iterations=4,
        pulses=pulses,
        seeds=["SPEFitSingle"+suffix],
        )

    tray.AddSegment(lilliput.segments.I3SinglePandelFitter,"MPEFit"+suffix,
        If=condition,
        domllh="MPE",
        pulses=pulses,
        seeds=["SPEFit4"+suffix],
        )

    tray.AddModule(selectFinalFit,"FinalFit")
