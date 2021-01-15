import icecube.lilliput.segments as segments
from icecube.common_variables import direct_hits
from icecube.common_variables import hit_multiplicity
from icecube import linefit
from firstHits import firstHits
from I3Tray import load

from controls import dh_definitions

load("double-muon")

from add_bayesian_reconstruction import add_bayesian_reconstruction

def add_split_fits(tray,splitName,idx,pulses,condition):
    tray.AddSegment(linefit.simple,"LineFit"+splitName+idx,
                    If=condition,
                    inputResponse=pulses+splitName+idx,
                    fitName="LineFit"+splitName+idx
                   )

    tray.AddSegment(segments.I3IterativePandelFitter,"SPEFit4"+splitName+idx,
                    If=condition,
                    domllh="SPE1st",
                    n_iterations=4,
                    pulses=pulses+splitName+idx,
                    seeds=["LineFit"+splitName+idx]
                   )

    add_bayesian_reconstruction(tray,pulses,condition,"SPEFit4"+splitName+idx)

    # The firstHits function is a mask that grabs only the first pulses on each DOM
    tray.Add(firstHits,
             inputPulses = pulses+splitName+idx,
             outputPulses = pulses+splitName+idx+"_first"
            )

    # Save the direct hit informaiton from the CommomVariables project
    tray.AddSegment(direct_hits.I3DirectHitsCalculatorSegment, 'dh_'+splitName+idx,
                    DirectHitsDefinitionSeries=dh_definitions,
                    PulseSeriesMapName=pulses+splitName+idx+"_first",
                    ParticleName="SPEFit4"+splitName+idx,
                    OutputI3DirectHitsValuesBaseName="SPEFit4"+splitName+idx+'_dh',
                    BookIt=True,
                    If=condition
                   )
        
    # Save the hit multiplicity information as well.
    tray.AddSegment(hit_multiplicity.I3HitMultiplicityCalculatorSegment, 'hm_'+splitName+idx,
                    PulseSeriesMapName=pulses+splitName+idx+"_first",
                    OutputI3HitMultiplicityValuesName=pulses+splitName+idx+"_hm",
                    BookIt=True,
                    If=condition
                   )

    tray.AddModule("Delete",splitName+idx+"Cleanup")(
        ("If",condition),
        ("Keys",[pulses+splitName+idx+"_first"])
        )

def add_split_reconstructions(tray,pulses,condition,seed):
    tray.AddModule("I3ResponseMapSplitter",pulses+"SplitTime")(
        ("If",condition),
        ("InputPulseMap",pulses),
        ("InputTrackName","") # deliberately blank
        )

    tray.AddModule("I3ResponseMapSplitter",pulses+"SplitGeo")(
        ("If",condition),
        ("InputPulseMap",pulses),
        ("InputTrackName",seed)
        )

    add_split_fits(tray,"SplitTime","1",pulses,condition)
    add_split_fits(tray,"SplitTime","2",pulses,condition)
    add_split_fits(tray,"SplitGeo","1",pulses,condition)
    add_split_fits(tray,"SplitGeo","2",pulses,condition)
