from controls import process_params
from firstHits import firstHits
from dumbOMSelection import dumbOMSelection
from ComputeChargeWeightedDist import ComputeChargeWeightedDist
from icecube.common_variables import hit_multiplicity, direct_hits
from get_NChan import get_NChan

deepCoreStrings = process_params()['deepCoreStrings']
dh_definitions  = process_params()['dh_definitions']

def computeSimpleCutVars(tray,condition):
    tray.Add(firstHits,
             inputPulses = "TTPulses",
             outputPulses = "TTPulses_first"
            )

    #Save the direct hit informaiton from the CommomVariables project
    tray.AddSegment(direct_hits.I3DirectHitsCalculatorSegment, 'dh',
                    DirectHitsDefinitionSeries       = dh_definitions,
                    PulseSeriesMapName               = "TTPulses_first",
                    ParticleName                     = "TrackFit",
                    OutputI3DirectHitsValuesBaseName = "TrackFit_dh",
                    BookIt                           = True,
                    If                               = condition
                   )

    tray.AddSegment(hit_multiplicity.I3HitMultiplicityCalculatorSegment, '_hm',
                    PulseSeriesMapName                = "TTPulses_first",
                    OutputI3HitMultiplicityValuesName = 'TTPulses_hm',
                    BookIt                            = True,
                    If                                = condition
                   )

    tray.Add(get_NChan)

    #=============Now do it without DeepCore================#

    # Select all the TTPulses that were not part of DeepCore
    tray.AddModule(dumbOMSelection,"NoDeepCore2",
                   IfCond=condition,
                   pulses="TTPulses",
                   output="TTPulses_NoDC",
                   omittedStrings=deepCoreStrings
                  )

    tray.AddModule(firstHits,"FirstHits2",
                   inputPulses = "TTPulses_NoDC",
                   outputPulses = "TTPulses_NoDC_first"
                  )

    #Save the direct hit informaiton from teh CommomVariables project
    tray.AddSegment(direct_hits.I3DirectHitsCalculatorSegment, 'dh_NoDC',
                    DirectHitsDefinitionSeries       = dh_definitions,
                    PulseSeriesMapName               = "TTPulses_NoDC_first",
                    ParticleName                     = "TrackFit",
                    OutputI3DirectHitsValuesBaseName = "TrackFit_NoDC_dh",
                    BookIt                           = True,
                    If                               = condition
                   )

    # Save the hit multiplicity information as well.
    tray.AddSegment(hit_multiplicity.I3HitMultiplicityCalculatorSegment, 'hm_NoDC',
                    PulseSeriesMapName                = "TTPulses_NoDC_first",
                    OutputI3HitMultiplicityValuesName = "TTPulses_NoDC_hm",
                    BookIt                            = True,
                    If                                = condition
                   )
    
    tray.AddModule(ComputeChargeWeightedDist,"CCWD2",Pulses="TTPulses_NoDC",Track="TrackFit")

