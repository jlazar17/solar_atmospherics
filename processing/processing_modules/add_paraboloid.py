from icecube.icetray import I3Units

def add_paraboloid(tray,pulses,condition,seed):
    tray.AddService("I3BasicSeedServiceFactory",seed+"_ParaboloidSeed")(
        ("InputReadout",pulses),
        ("FirstGuesses",[seed]),
        ("TimeShiftType","TFirst")
        )

    tray.AddService("I3GulliverIPDFPandelFactory",seed+"_ParaboloidLikelihood")(
        ("InputReadout",pulses),
        ("Likelihood","MPE"),
        ("PEProb","GaussConvolutedFastApproximation"),
        ("NoiseProbability",10 * I3Units.hertz),
        ("JitterTime",4.0 * I3Units.ns),
        ("EventType","InfiniteMuon")
        )

    tray.AddModule("I3ParaboloidFitter", seed+"Paraboloid")(
        ("OutputName",seed+"Paraboloid"),
        ("If",condition),
        ("SeedService",seed+"_ParaboloidSeed"),
        ("LogLikelihood",seed+"_ParaboloidLikelihood"),
        ("MaxMissingGridPoints",1),
        ("VertexStepSize",5.0 * I3Units.m),
        ("ZenithReach",2.0 * I3Units.degree),
        ("AzimuthReach",2.0 * I3Units.degree),
        ("GridpointVertexCorrection",seed+"_ParaboloidSeed"),
        ("Minimizer","default_simplex"),
        ("NumberOfSamplingPoints",8),
        ("NumberOfSteps",3),
        ("MCTruthName","")
        )
