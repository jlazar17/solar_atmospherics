def interaction_type(frame):
    if not (finalSample & is_simulation)(frame):
        return
    mcTree = frame['I3MCTree']
    
    if 'NuFSGen' in options.infile:
        # for NuFSGen, the neutrino is the primary. There is no background.
        neutrino = dataclasses.get_most_energetic_primary(mcTree)
    else:
        # NuGEn is different. Let's find the highest energy neutrino and use that.
        neutrino =  dataclasses.get_most_energetic_neutrino(mcTree)

    # Let's go through the neutrino daughters to see what kind of interaction it was. If there are no children,
    # the interaction was probably just from a cosmic ray. It looks like the injected CORSIKA just propagates muons. so
    # I don't think we have any extra neutrinos.

    PrimaryMuonEnergy     = 0
    PrimaryMuonDir        = 0
    PrimaryMuonAzimuth    = 0
    PrimaryCascadeEnergy  = 0
    PrimaryCascadeDir     = 0
    PrimaryCascadeAzimuth = 0
    neutral_current       = 0
    neutral_current_type  = 0
    charged_current       = 0
    charged_current_type  = 0

    if not neutrino:
        CORSIKA = 1
        print('There is a problem. This better be CORSIKA, there are no neutrinos.')
        return

    children = mcTree.get_daughters(neutrino)
    if len(children) == 0:
        CORSIKA = 1
        #print('This neutrino had no children, CORSIKA. We had a neutrino, but it didn't interact. It could be a CORSIKA event with secondary neutrinos.')
            #print(frame['I3MCTree'])
        print('There is no children on the neutrino! Check this. Probably CORSIKA. Setting CORSIKA =1')
        return
    else:
        CORSIKA = 0

    neutrino_energy = neutrino.energy
    count = 0

    #let's start by talking the total energy of the mu+hadrons. This variable defines the NuFSGen energy range.
    total_energy = 0
    for child in children:
        #check for charged current. Neutral current won't have a Mu- or Mu+.
        if child.type == dataclasses.I3Particle.ParticleType.MuMinus or child.type == dataclasses.I3Particle.ParticleType.MuPlus:
            #if CC add the total energy
            for c in children:
                total_energy += c.energy
    frame.Put("CC_energy",dataclasses.I3Double(total_energy))

    for child in children:
        if(isNeutrinoType(child.type)):
            if child.type == dataclasses.I3Particle.ParticleType.NuE:
                neutral_current_type = 12
                neutral_current = 1
            elif child.type == dataclasses.I3Particle.ParticleType.NuEBar:
                neutral_current_type = -12
                neutral_current = 1
            elif child.type == dataclasses.I3Particle.ParticleType.NuMu:
                neutral_current_type = 14
                neutral_current = 1
            elif child.type == dataclasses.I3Particle.ParticleType.NuMuBar:
                neutral_current_type = -14
                neutral_current = 1
            elif child.type == dataclasses.I3Particle.ParticleType.NuTau:
                neutral_current_type = 16
                neutral_current = 1
            elif child.type == dataclasses.I3Particle.ParticleType.NuTauBar:
                neutral_current_type = -16
                neutral_current = 1
            else:
                neutral_current_type = 0
                neutral_current = 0
                charged_current_type = 0
                charged_current = 0

                PrimaryMuonEnergy = NaN
                PrimaryMuonZenith = NaN
                PrimaryMuonAzimuth = NaN
                PrimaryMuonType = NaN
                print('-- I think this is a Neutral Current interaction:')
                print(frame['I3MCTree'])
                break

        elif (isChargedLepton(child.type)):
            if child.type == dataclasses.I3Particle.ParticleType.EMinus:
                charged_current_type = 12
                charged_current = 1

            elif child.type == dataclasses.I3Particle.ParticleType.EPlus:
                charged_current_type = -12
                charged_current = 1

            elif child.type == dataclasses.I3Particle.ParticleType.MuMinus:
                charged_current_type = 14
                charged_current = 1
            
            PrimaryMuonEnergy = child.energy
            PrimaryMuonZenith = child.dir.zenith
            PrimaryMuonAzimuth = child.dir.azimuth
            PrimaryMuonType = 14

        elif child.type == dataclasses.I3Particle.ParticleType.MuPlus:
            charged_current_type = -14
            charged_current = 1
            PrimaryMuonEnergy = child.energy
            PrimaryMuonZenith = child.dir.zenith
            PrimaryMuonAzimuth = child.dir.azimuth
            PrimaryMuonType = -14

        elif child.type == dataclasses.I3Particle.ParticleType.TauMinus:
            charged_current_type = 16
            charged_current = 1

        elif child.type == dataclasses.I3Particle.ParticleType.TauPlus:
            charged_current_type = -16
            charged_current = 1
        else:
            print('There is a problem with how we are looking for CC events. This event had a lepton as a child, but unknown type.')
            print(frame['I3MCTree'])
    
    #NuGen seems to have a problem, some events don't have secondaries (except Hadrons). These will show up as 0000, and CORSIKA = 0.

    # both CC and NC have cascades.
    cascade_energy = dataclasses.get_most_energetic_cascade(frame['I3MCTree']).energy
    cascade_dir = dataclasses.get_most_energetic_cascade(frame['I3MCTree']).dir.zenith
    cascade_dir = dataclasses.get_most_energetic_cascade(frame['I3MCTree']).dir.azimuth
    '''
    frame.Put("PrimaryMuonEnergy",dataclasses.I3Double(PrimaryMuonEnergy))
    frame.Put("PrimaryMuonDir",dataclasses.I3Double(PrimaryMuonDir))
    frame.Put("PrimaryMuonAzimuth",dataclasses.I3Double(PrimaryMuonAzimuth))
    frame.Put("PrimaryMuonType",dataclasses.I3Double(PrimaryMuonType))
    '''
    frame.Put("injectedMuonEnergy",dataclasses.I3Double(PrimaryMuonEnergy))
    frame.Put("injectedMuonZenith",dataclasses.I3Double(PrimaryMuonDir))
    frame.Put("injectedMuonAzimuth",dataclasses.I3Double(PrimaryMuonAzimuth))
    frame.Put("primaryType",dataclasses.I3Double(PrimaryMuonType))

    frame.Put("PrimaryCascadeEnergy",dataclasses.I3Double(PrimaryCascadeEnergy))
    frame.Put("PrimaryCascadeDir",dataclasses.I3Double(PrimaryCascadeDir))
    frame.Put("PrimaryCascadeAzimuth",dataclasses.I3Double(PrimaryCascadeAzimuth))

    frame.Put("neutral_current",dataclasses.I3Double(neutral_current))
    frame.Put("neutral_current_type",dataclasses.I3Double(neutral_current_type))
    frame.Put("charged_current",dataclasses.I3Double(charged_current))
    frame.Put("charged_current_type",dataclasses.I3Double(charged_current_type))
    frame.Put("CORSIKA",dataclasses.I3Double(CORSIKA))

