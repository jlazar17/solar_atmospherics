from icecube import VHESelfVeto,dataclasses,phys_services,icetray,dataio,MuonGun
from icecube.weighting.fluxes import GaisserH3a, GaisserH4a, Hoerandel5
from icecube.weighting import weighting, get_weighted_primary, SimprodNormalizations
from I3Tray import *
import pickle

import argparse, os, glob
import numpy as np
np.seterr(divide='ignore', invalid='ignore')
from scipy import interpolate

#simple dictionary for simprod number of files used
#simprod_nfiles={"10649":999,"11029":9902,"11057":74888,"11058":28239,"11499":99998,
#                "11808":100000,"11865":99996,"11905":100000,"11926":100000,"11937":100000,
#                "11943":35929,"12040":24800,"12161":99972,"12268":100000,"12332":100000,
#                "12379":34516,"20788":99986,"20789":99743,"20848":73653}
#muongun_nfiles={"highE":14999,"mediumE":39999,"lowE":199990}
simprod_nfiles={21002:9979,21217:21851,21218:11991,21219:15376,
                21220:9999,21221:10000,
                20904:740335, 20891: 497612, 20881: 99904,
                20852:99094, 20849:9948, 20848:99782, 20789:99998,
                20788:99998, 20787:99743}
muongun_nfiles={"highE":15000,"mediumE":40000,"lowE":200000,
                "set5":99598,"set4":99975,"set3":19994,"set2":39993,"set1":14997}
# this function simply parses which subfunctions to call for each data set
# also has a fail safe when testing
def wt(tray, data_name=""):
    if("burn_sample" in data_name):
        weighter_data(tray)
    elif("muongun" in data_name):
        weighter_muongun(tray)
    elif("corsika" in data_name):
        weighter_corsika(tray)
    elif("nugen" in data_name):
        weighter_astro(tray)
        weighter_atmos(tray)
    else:
        print("bad event, exit here and fix it")
        exit(0)

#simple for data, every event gets a weight of 1
def weighter_data(frame):
    frame['Weight']=dataclasses.I3Double(1.0)

#muon stuff
def weighter_muongun(frame):
    weights = frame["MuonWeight"].value
    frame['Weight']=dataclasses.I3Double(weights)
#extract all the generators used for muons
def harvest_generators(infiles):
    generator = None
    for fname in infiles:
        f = dataio.I3File(fname)
        fr = f.pop_frame(icetray.I3Frame.Stream('S'))
        f.close()
        if fr is not None:
            for k in fr.keys():
                if("I3TriggerHierarchy" in k): continue #hack due to I3TriggerHierchy bug
                v = fr[k]
                if isinstance(v, MuonGun.GenerationProbability):
                    print("found MG GP")
                    if generator is None:
                        generator = v
                    else:
                        generator += v
    return generator
#weight according to the initial sample used
def muongun_generator(mctype):
    if "nancy" in mctype:
        generator_highE_infile=glob.glob("/data/ana/Cscd/StartingEvents/MuonGun/high_energy/IC86_2012/l2/*/l2*")
        generator_highE=harvest_generators([generator_highE_infile[0]])
        infiles_highE = muongun_nfiles["highE"]
        generator_lowE_infile=glob.glob("/data/ana/Cscd/StartingEvents/MuonGun/low_energy/IC86_2012/l2/*/l2*")
        generator_lowE=harvest_generators([generator_lowE_infile[0]])
        infiles_lowE = muongun_nfiles["lowE"]
        generator_mediumE_infile=glob.glob("/data/ana/Cscd/StartingEvents/MuonGun/medium_energy/IC86_2012/l2/*/l2*")
        generator_mediumE=harvest_generators([generator_mediumE_infile[0]])
        infiles_mediumE = muongun_nfiles["mediumE"]
        generator=((infiles_lowE*generator_lowE) +
                   (infiles_mediumE*generator_mediumE) +
                   (infiles_highE*generator_highE))
    else:
        generator_set1_infile=glob.glob("/data/sim/IceCube/2016/generated/MuonGun/21315/*/*.i3.zst")
        generator_set1=harvest_generators([generator_set1_infile[0]]); infiles_set1 = muongun_nfiles["set1"]
        generator_set2_infile=glob.glob("/data/sim/IceCube/2016/generated/MuonGun/21316/*/*.i3.zst")
        generator_set2=harvest_generators([generator_set2_infile[0]]); infiles_set2 = muongun_nfiles["set2"]
        generator_set3_infile=glob.glob("/data/sim/IceCube/2016/generated/MuonGun/21317/*/*.i3.zst")
        generator_set3=harvest_generators([generator_set3_infile[0]]); infiles_set3 = muongun_nfiles["set3"]
        generator_set4_infile=glob.glob("/data/sim/IceCube/2016/generated/MuonGun/21318/*/*.i3.zst")
        generator_set4=harvest_generators([generator_set4_infile[0]]); infiles_set4 = muongun_nfiles["set4"]
        generator_set5_infile=glob.glob("/data/sim/IceCube/2016/generated/MuonGun/21319/*/*.i3.zst")
        generator_set5=harvest_generators([generator_set5_infile[0]]); infiles_set5 = muongun_nfiles["set5"]
        generator=((infiles_set1*generator_set1) +
                   (infiles_set2*generator_set2) +
                   (infiles_set3*generator_set3) +
                   (infiles_set4*generator_set4) +
                   (infiles_set5*generator_set5))
    model = MuonGun.load_model('Hoerandel5_atmod12_SIBYLL')
    return model, generator

#weight Corsika sample now!
corsika_dids = [20891, 20881, 20852, 20849, 20848, 20789, 20788, 20787, 20904] 
def weighter_corsika(frame):
    with open('/data/user/jlazar/solar/solar_atmospherics/event_selection/l3/utils/corsika_generator_dict.pkl', 'rb') as f:
        gen_dict = pickle.load(f)
    if not frame.Has("MCPrimary"):
        get_weighted_primary(frame, MCPrimary="MCPrimary")
    MCPrimary = frame["MCPrimary"]
    energy = MCPrimary.energy
    ptype = MCPrimary.type
    generator = None
    for DID in corsika_dids:
        if is None: 
            generator = gen_dict[DID];
        else: 
            generator += gen_dict[DID];
    gaisser = GaisserH4a()
    hoerandel = Hoerandel5()
    gaisser_weights = gaisser(energy, ptype) / generator(energy, ptype)
    hoerandel_weights = hoerandel(energy, ptype) / generator(energy, ptype)
    if np.isnan(gaisser_weights):
        weights=0.0;
    frame['Weight']=dataclasses.I3Double(gaisser_weights)
    frame['GaisserWeight']=dataclasses.I3Double(gaisser_weights)
    frame['HoerandelWeight']=dataclasses.I3Double(hoerandel_weights)
    #do a little cleanup now
    flux = 0
    generator = 0
    weights = 0
    MCPrimary = 0

#weight NuGen sample now! default value is mese 2 year flux
#def flux_val(energy,norm=2.06, gamma=2.46): #MESE
def flux_val(energy,norm=2.06, gamma=2.46): #per GeV per cm^2 per sr per s
    E=energy
    return (norm*10**-18)*((E/(100000.))**-gamma) #*(10000) #10000 term comes from converting cm^2 to m^2
def weighter_astro(frame):
    I3EventHeader = frame["I3EventHeader"]
    I3MCWeightDict = frame["I3MCWeightDict"]   
    energy = I3MCWeightDict["PrimaryNeutrinoEnergy"]
    oneweight = I3MCWeightDict["OneWeight"]#GeV cm^2 sr
    nevts = I3MCWeightDict["NEvents"]
    nfiles = simprod_nfiles[I3EventHeader.run_id]
    frame['Weight_MESE']=dataclasses.I3Double(flux_val(energy,norm=2.06, gamma=2.46) * oneweight / (nevts * nfiles/2))
    frame['Weight_HESE']=dataclasses.I3Double(flux_val(energy,norm=6.45, gamma=2.89) * oneweight / (nevts * nfiles/2))
    frame['Weight_numu']=dataclasses.I3Double(flux_val(energy,norm=1.44, gamma=2.28) * oneweight / (nevts * nfiles/2))
conv_dict = {dataclasses.I3Particle.NuE:'conv_nu_e', dataclasses.I3Particle.NuMu:'conv_nu_mu',
             dataclasses.I3Particle.NuEBar:'conv_nu_e', dataclasses.I3Particle.NuMuBar:'conv_nu_mu'}
pr_dict   = {dataclasses.I3Particle.NuE:'pr_nu_e', dataclasses.I3Particle.NuMu:'pr_nu_mu', dataclasses.I3Particle.NuTau:'pr_nu_tau',
             dataclasses.I3Particle.NuEBar:'pr_nu_e', dataclasses.I3Particle.NuMuBar:'pr_nu_mu', dataclasses.I3Particle.NuTauBar:"pr_nu_tau"}#tau only has prompt component
def final_flux(primary_tree):
    primary = primary_tree[0]
    energy = primary.energy
    zenith = np.cos(primary.dir.zenith)
    ptype = primary.type
    surface = MuonGun.ExtrudedPolygon.from_file("/cvmfs/icecube.opensciencegrid.org/data/GCD/GeoCalibDetectorStatus_AVG_55697-57531_PASS2_SPE_withScaledNoise.i3.gz")
    intersections_dist = surface.intersection(primary.pos, primary.dir)
    intersect_z = (1948.07-(primary.pos + intersections_dist.first*primary.dir).z)/1000.0
    angles= np.linspace(-1,1,51); angle=0.
    depths = np.linspace(1.5,2.5,21); depth=1.5
    for temp_angle in angles:
        if (zenith      < temp_angle):
            angle=temp_angle; break;
    if zenith < 0:
        depth=1.50
    else:
        for temp_depth in depths:
            if (intersect_z < temp_depth):
                depth=temp_depth; break;
    paths = "/data/user/msilva/ESTES_systematics/raw_fluxes/final_flux_step_10GeV_energy_100GeV_10PeV_coszen_"
    pr_neut      = pr_dict[ptype]
    filename_pr  = "%1.2f_neut_%s_depth_%1.2fkm"%(angle,pr_neut,depth)
    passing_prfluxes = np.load(paths+filename_pr+"_crflux_HillasGaisser2012_H3a_himodel_DPMJET-III-19.1_atmos_average.npy")
    energies = np.logspace(2,9,71)
    interp_pr = interpolate.interp1d(energies, passing_prfluxes, kind='slinear')
    final_pr  = interp_pr(energy); 
    if "tau" in pr_neut:
        return 0, final_pr
    conv_neut      = conv_dict[ptype]
    filename_conv  = "%1.2f_neut_%s_depth_%1.2fkm"%(angle,conv_neut,depth)
    passing_convfluxes = np.load(paths+filename_conv+"_crflux_HillasGaisser2012_H3a_himodel_DPMJET-III-19.1_atmos_average.npy")
    interp_conv = interpolate.interp1d(energies, passing_convfluxes, kind='slinear')
    final_conv  = interp_conv(energy);
    return final_conv, final_pr

def weighter_atmos(frame):
    I3EventHeader = frame["I3EventHeader"]
    I3MCWeightDict = frame["I3MCWeightDict"]
    ptype = I3MCWeightDict["PrimaryNeutrinoType"]
    cos_theta = np.cos(I3MCWeightDict["PrimaryNeutrinoZenith"])
    energy = I3MCWeightDict["PrimaryNeutrinoEnergy"]
    oneweight = I3MCWeightDict["OneWeight"]
    nevts = I3MCWeightDict["NEvents"]
    nfiles = simprod_nfiles[I3EventHeader.run_id]
    genweight = oneweight / (nevts * nfiles/2)
    flux = final_flux(frame["I3MCTree_preMuonProp"])
    frame['Weight_H3a_conv']=dataclasses.I3Double(genweight*flux[0])
    frame['Weight_H3a_pr']=dataclasses.I3Double(genweight*flux[1])
