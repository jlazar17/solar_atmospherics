from icecube.icetray import I3Units
from I3Tray import load

load("bayesian-priors")

zenithPrior = None
def add_bayesian_reconstruction(tray,pulses,condition,seedTrack):
    seedLikelihood=seedTrack+"_BayesianLikelihoodSeed"
    tray.AddService('I3GulliverIPDFPandelFactory', seedLikelihood)(
                                       ("InputReadout",pulses),
                                       ("EventType","InfiniteMuon"),
                                       ("Likelihood","SPE1st"),
                                       ("PEProb","GaussConvolutedFastApproximation"),
                                       ("JitterTime",15.*I3Units.ns),
                                       ("NoiseProbability",10.*I3Units.hertz)
                                      )

    global zenithPrior
    if(zenithPrior==None):
        zenithPrior="ZenithPrior"
        tray.AddService("I3PowExpZenithWeightServiceFactory",zenithPrior)(
                                       ("Amplitude",2.49655e-07),
                                       ("CosZenithRange",[-1,1]),
                                       ("DefaultWeight",1.383896526736738e-87),
                                       ("ExponentFactor",0.778393),
                                       ("FlipTrack",False),
                                       ("PenaltySlope",-1000),
                                       ("PenaltyValue",-200),
                                       ("Power",1.67721)
                                      )

    tray.AddService("I3BasicSeedServiceFactory", seedTrack+"_BayesianSeed")(
                                       ("InputReadout",pulses),
                                       ("FirstGuesses",[seedTrack]),
                                       ("TimeShiftType","TFirst")
                                      )

    tray.AddService("I3EventLogLikelihoodCombinerFactory",seedTrack+"_BayesianLikelihood")(
                                       ("InputLogLikelihoods",[seedLikelihood,zenithPrior])
                                      )

    tray.AddModule("I3IterativeFitter",seedTrack+"Bayesian")(
                                       ("OutputName",seedTrack+"Bayesian"),
                                       ("RandomService","SOBOL"),
                                       ("NIterations",8),
                                       ("SeedService",seedTrack+"_BayesianSeed"),
                                       ("Parametrization","default_simpletrack"),
                                       ("LogLikelihood",seedTrack+"_BayesianLikelihood"),
                                       ("CosZenithRange",[0, 1]),
                                       ("Minimizer","default_simplex"),
                                       ("If",condition)
                                      )
