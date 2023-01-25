from icecube import dataclasses
def isChargedLepton(pType):
    return(pType==dataclasses.I3Particle.ParticleType.EMinus
           or pType==dataclasses.I3Particle.ParticleType.EPlus
           or pType==dataclasses.I3Particle.ParticleType.MuMinus
           or pType==dataclasses.I3Particle.ParticleType.MuPlus
           or pType==dataclasses.I3Particle.ParticleType.TauMinus
           or pType==dataclasses.I3Particle.ParticleType.TauPlus
          )
