from icecube import dataclasses
from is_simulation import is_simulation

def finalNeutrino(frame):
    if not (finalSample & is_simulation)(frame):
        return
    mcTree = frame["I3MCTree"]
    try:
        primaryNeutrino = dataclasses.get_most_energetic_primary(mcTree)
    except:
        primaryNeutrino = mcTree.most_energetic_primary

    if(primaryNeutrino==None or not isNeutrinoType(primaryNeutrino.type)):
        return

    #walk down the tree to find the first daughter neutrino which is 'InIce'
    neutrino=primaryNeutrino
    while(neutrino.location_type!=dataclasses.I3Particle.LocationType.InIce):
        children=mcTree.get_daughters(neutrino)
        foundNext=False
        #take the first child which is a neutrino;
        #for in-Earth NC interactions it should be the only one anyway
        for child in children:
            if(isNeutrinoType(child.type)):
                neutrino=child
                foundNext=True
                break
        if(not foundNext):
            #print " did not find a daughter neutrino"
            return #bail out
    frame["InteractingNeutrino"]=neutrino

