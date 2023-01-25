from icecube import dataclasses
def isNeutrinoType(pType):
    return(pType==dataclasses.I3Particle.ParticleType.NuE
           or pType==dataclasses.I3Particle.ParticleType.NuEBar
           or pType==dataclasses.I3Particle.ParticleType.NuMu
           or pType==dataclasses.I3Particle.ParticleType.NuMuBar
           or pType==dataclasses.I3Particle.ParticleType.NuTau
           or pType==dataclasses.I3Particle.ParticleType.NuTauBar
          )
