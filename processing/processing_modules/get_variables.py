
from icecube import LeptonInjector

def get_variables(frame):
    if not "I3EventHeader" in frame:
        print("Frame Failed: No I3EventHeader")
        return False
    #event_id = str(frame["I3EventHeader"].run_id)+ '_' + str(frame["I3EventHeader"].event_id) + '_'+str(frame["I3EventHeader"].sub_event_id)
    #print(float(str(frame["I3EventHeader"].run_id)+'.'+str(frame["I3EventHeader"].event_id)))
    event_id = float(str(frame["I3EventHeader"].run_id)+'.'+str(frame["I3EventHeader"].event_id))
    #print(event_id)
    frame.Put("EventID"         ,dataclasses.I3Double(frame["I3EventHeader"].event_id))
    frame.Put("RunID"           ,dataclasses.I3Double(frame["I3EventHeader"].run_id))
    if isMC:
        if corsika_file:
            energy = frame['MCPrimaries'][0].energy
            ptype = frame['MCPrimaries'][0].type
            weights = flux(energy, ptype)/generator(energy, ptype)
            #print(weights)
            #if weights < 4.5e-06:
            #    return False
            frame.Put("FinalStateX"             ,dataclasses.I3Double(NaN))
            frame.Put("FinalStateY"             ,dataclasses.I3Double(NaN))
            frame.Put("TotalColumnDepth",dataclasses.I3Double(NaN))
            frame.Put("ImpactParameter" ,dataclasses.I3Double(NaN))
            frame.Put("NuEnergy"                ,dataclasses.I3Double(NaN))
            frame.Put("NuZenith"                ,dataclasses.I3Double(NaN))
            frame.Put("PassedMuon"               ,dataclasses.I3Double(NaN))
            frame.Put("PassedLowUp"               ,dataclasses.I3Double(NaN))
            muon_energy         =  dataclasses.get_most_energetic_muon(frame['I3MCTree']).energy
            muon_energy         =  dataclasses.get_most_energetic_muon(frame['I3MCTree']).energy
            muon_zenith         =  dataclasses.get_most_energetic_muon(frame['I3MCTree']).dir.zenith
            muon_azimuth        =  dataclasses.get_most_energetic_muon(frame['I3MCTree']).dir.azimuth
            muon_Z                      =  dataclasses.get_most_energetic_muon(frame['I3MCTree']).pos.z
            #print(muon_energy)
            frame.Put("MuonEnergy"              ,dataclasses.I3Double(muon_energy))
            frame.Put("MuonZenith"              ,dataclasses.I3Double(muon_zenith))
            frame.Put("MuonZ"                   ,dataclasses.I3Double(muon_Z))
            frame.Put("MuonAzimuth"             ,dataclasses.I3Double(muon_azimuth))
            frame.Put("HadronEnergy"    ,dataclasses.I3Double(NaN))
            frame.Put("HadronZenith"    ,dataclasses.I3Double(NaN))
            frame.Put("weights"                 ,dataclasses.I3Double(weights))
            frame.Put("TrueMuExEnergy"  ,dataclasses.I3Double(NaN))
            frame.Put("InjectionRadius" ,dataclasses.I3Double(NaN)) 
            frame.Put("TrueMuExZenith"  ,dataclasses.I3Double(NaN))

        else:
            LWevent                                             = LW.Event()
            EventProperties                             = frame['I3MCWeightDict']
            #LeptonInjectorProperties            = frame['LeptonInjectorProperties']
            LWevent.primary_type                        = LW.ParticleType(EventProperties[])
            LWevent.final_state_particle_0      = LW.ParticleType(EventProperties.finalType1)
            LWevent.final_state_particle_1      = LW.ParticleType(EventProperties.finalType2)
            frame.Put("PrimaryType"                     ,dataclasses.I3Double(LW.ParticleType(EventProperties.initialType)))
            frame.Put("FinalType0"                      ,dataclasses.I3Double(LW.ParticleType(EventProperties.finalType1)))
            frame.Put("FinalType1"                      ,dataclasses.I3Double(LW.ParticleType(EventProperties.finalType2)))
            LWevent.zenith                                      = EventProperties.zenith
            LWevent.energy                                      = EventProperties.totalEnergy
            LWevent.azimuth                             = EventProperties.azimuth
            frame.Put("NuEnergy"                        ,dataclasses.I3Double(EventProperties.totalEnergy))
            frame.Put("NuZenith"                        ,dataclasses.I3Double(EventProperties.zenith))
            frame.Put("NuAzimuth"                       ,dataclasses.I3Double(EventProperties.azimuth))
            LWevent.interaction_x                       = EventProperties.finalStateX
            LWevent.interaction_y                       = EventProperties.finalStateY
            LWevent.total_column_depth          = EventProperties.totalColumnDepth
            LWevent.radius                                      = EventProperties.impactParameter
            frame.Put("FinalStateX"                     ,dataclasses.I3Double(EventProperties.finalStateX))
            frame.Put("FinalStateY"                     ,dataclasses.I3Double(EventProperties.finalStateY))
            frame.Put("TotalColumnDepth"        ,dataclasses.I3Double(EventProperties.totalColumnDepth))
            frame.Put("ImpactParameter"         ,dataclasses.I3Double(EventProperties.impactParameter))
            LWevent.x = 0. 
            LWevent.y = 0.
            LWevent.z = 0.
            pion_weight = weight_pions(LWevent)/2.
            kaon_weight = weight_kaons(LWevent)/2.
            
            #oneweight = pion_weight.get_oneweight((LWevent))
            oneweight = weight_pions.get_oneweight(LWevent)
            #print(oneweight)

            frame.Put("oneweight"                       ,dataclasses.I3Double(oneweight))
            weights = (weight_pions(LWevent) + weight_kaons(LWevent))/2.
            
            '''
            print('\n')
            print('IntX '+str(EventProperties.finalStateX))
            print('IntY '+str(EventProperties.finalStateY))
            print('Total Energy '+str(EventProperties.totalEnergy))
            print('Azimuth '+str(EventProperties.azimuth))
            print('Zenith '+str(EventProperties.zenith))
            print('Impact Parameter '+str(EventProperties.impactParameter))
            print('Total column Depth '+str(EventProperties.totalColumnDepth))
            print('Weight '+str(weights))
            print('MuEx energy '+str(frame['MuExTrue'].energy))
            print('MuEx zenith '+str(frame['MuExTrue'].dir.zenith))
            '''
            frame.Put("weights"                 ,dataclasses.I3Double(weights))
            
            #if frame.Stop==icetray.I3Frame.Physics:
            
            #print(frame['I3MCTree'])

            I3MCTree = frame['I3MCTree']
            muon = I3MCTree[1]
            hadron = I3MCTree[2]

            x = -muon.pos.x
            y = -muon.pos.y
            z = -muon.pos.z
            theta = muon.dir.zenith
            phi   = muon.dir.azimuth
            r     = 100000.
            x2 = r * np.sin(theta) * np.cos(phi)
            y2 = r * np.sin(theta) * np.sin(phi)
            z2 = r * np.cos(theta)
            p2 = np.asarray([x2,y2,z2])
            p1 = np.asarray([0,0,0])
            p  = np.asarray([x,y,z])
            dist = (p-p1)-np.dot((p-p1),(p2-p1))*(p2-p1)/np.linalg.norm(p2-p1)**2
            injection_radius = np.linalg.norm(dist)

            frame.Put("InjectionRadius" ,dataclasses.I3Double(injection_radius)) 
            frame.Put("MuonEnergy"              ,dataclasses.I3Double(I3MCTree[1].energy))
            frame.Put("MuonZenith"              ,dataclasses.I3Double(I3MCTree[1].dir.zenith))
            frame.Put("MuonZ"                   ,dataclasses.I3Double(I3MCTree[1].dir.z))
            frame.Put("MuonAzimuth"             ,dataclasses.I3Double(I3MCTree[1].dir.azimuth))
            frame.Put("HadronEnergy"    ,dataclasses.I3Double(I3MCTree[2].energy))
            frame.Put("HadronZenith"    ,dataclasses.I3Double(I3MCTree[2].dir.zenith))
            #frame.Put("TrueMuExEnergy"  ,dataclasses.I3Double(frame['MuExTrue'].energy))
            #frame.Put("TrueMuExZenith"  ,dataclasses.I3Double(frame['MuExTrue'].dir.zenith))
            #frame.Put("PionWeight"              ,dataclasses.I3Double(pion_weight))
            #frame.Put("KaonWeight"              ,dataclasses.I3Double(kaon_weight))

    else:
        frame.Put("FinalStateX"         ,dataclasses.I3Double(NaN))
        frame.Put("FinalStateY"         ,dataclasses.I3Double(NaN))
        frame.Put("TotalColumnDepth",dataclasses.I3Double(NaN))
        frame.Put("ImpactParameter"     ,dataclasses.I3Double(NaN))
        frame.Put("NuEnergy"            ,dataclasses.I3Double(NaN))
        frame.Put("NuZenith"            ,dataclasses.I3Double(NaN))
        frame.Put("NuAzimuth"           ,dataclasses.I3Double(NaN))
        frame.Put("MuonEnergy"          ,dataclasses.I3Double(NaN))
        frame.Put("MuonZenith"          ,dataclasses.I3Double(NaN))
        frame.Put("MuonZ"                       ,dataclasses.I3Double(NaN))
        frame.Put("MuonAzimuth"         ,dataclasses.I3Double(NaN))
        frame.Put("HadronEnergy"        ,dataclasses.I3Double(NaN))
        frame.Put("HadronZenith"        ,dataclasses.I3Double(NaN))
        weights = 1.0
        frame.Put("weights"                     ,dataclasses.I3Double(weights))
        frame.Put("TrueMuExEnergy"      ,dataclasses.I3Double(NaN))
        frame.Put("InjectionRadius" ,dataclasses.I3Double(NaN)) 
        frame.Put("TrueMuExZenith"      ,dataclasses.I3Double(NaN))
        frame.Put("RunNum"              ,dataclasses.I3Double(run_num))

    frame.Put("MuExEnergy"              ,dataclasses.I3Double(frame['MuEx'].energy))
    frame.Put("MuExZenith"              ,dataclasses.I3Double(frame['MuEx'].dir.zenith))
    frame.Put("MuExAzimuth"             ,dataclasses.I3Double(frame['MuEx'].dir.azimuth))
    frame.Put("MuExCOGR"                ,dataclasses.I3Double(frame['MuEx'].pos.r))
    frame.Put("MuExCOGZ"                ,dataclasses.I3Double(frame['MuEx'].pos.z))
    frame.Put("SplitGeo1DirN"           ,dataclasses.I3Double(frame['SPEFit4SplitGeo1_dh'].n_dir_doms))
    frame.Put("SplitGeo2DirN"           ,dataclasses.I3Double(frame['SPEFit4SplitGeo2_dh'].n_dir_doms))
    frame.Put("SplitTime1DirN"          ,dataclasses.I3Double(frame['SPEFit4SplitTime1_dh'].n_dir_doms))
    frame.Put("SplitTime2DirN"          ,dataclasses.I3Double(frame['SPEFit4SplitTime2_dh'].n_dir_doms))
    frame.Put("TrackFitDirN"                    ,dataclasses.I3Double(frame['TrackFit_dh'].n_dir_doms))
    
    #frame.Put("SplitGeo1NChan"         ,dataclasses.I3Double(frame['SPEFit4SplitGeo1_hm'].n_hit_doms))
    #frame.Put("SplitGeo2NChan"         ,dataclasses.I3Double(frame['SPEFit4SplitGeo2_hm'].n_hit_doms))
    #frame.Put("SplitTime1NChan"                ,dataclasses.I3Double(frame['SPEFit4SplitTime1_hm'].n_hit_doms))
    #frame.Put("SplitTime2NChan"                ,dataclasses.I3Double(frame['SPEFit4SplitTime2_hm'].n_hit_doms))

    #frame.Put("MuExZenith"             ,dataclasses.I3Double(frame['MuExCompat'].dir.zenith))
    #frame.Put("MuExAzimuth"            ,dataclasses.I3Double(frame['MuExCompat'].dir.azimuth))
    #frame.Put("MuExCOGR"               ,dataclasses.I3Double(frame['MuExCompat'].pos.r))
    #frame.Put("MuExCOGZ"               ,dataclasses.I3Double(frame['MuExCompat'].pos.z))
   
    #print(frame['MuExCompat'].energy,frame['MuEx'].energy)
    if Multisim == True:
        MultisimAmplitudes = frame['MultisimAmplitudes'][:7]
        MultisimPhases = frame['MultisimPhases'][:7]
        del frame['MultisimAmplitudes']
        del frame['MultisimPhases']
        del frame['MultisimModes']
        #print(MultisimAmplitudes)
        frame.Put('MultisimAmplitudes' ,dataclasses.I3VectorDouble(MultisimAmplitudes))
        frame.Put('MultisimPhases'     ,dataclasses.I3VectorDouble(MultisimPhases))
        #frame.Put('MultisimModes'      ,dataclasses.I3VectorDouble(MultisimModes))

    pulse_series        = dataclasses.I3RecoPulseSeriesMap.from_frame(frame,'TTPulses_NoDC')
    geo                         = frame.Get('I3Geometry')
    om_geo                      = geo.omgeo
    Qtot                        = 0
    SrQ                         = 0
    SzQ                         = 0
    ASzQ                        = 0
    ASrQ                        = 0
    Sr                          = 0
    Sz                          = 0
    SrQN                        = 0
    SzQN                        = 0
    NChan = len(pulse_series)
    charges             = []
    depth                       = []
    depth_charges       = []
    for om, pulses in pulse_series:
        om_pos = om_geo[om].position
        om_z = om_pos[2]
        om_r = np.sqrt(om_pos[0]**2+om_pos[1]**2+om_pos[2]**2)
        Qom = 0
        for pulse in pulses:
            Qom += pulse.charge
        charges.append(Qom)
        depth.append(om_z)
        depth_charges.append(Qom)
        SrQ += om_r * Qom
        SzQ += om_z * Qom
        SrQN += om_r * Qom * len(pulses)
        SzQN += om_z * Qom * len(pulses)
        Qtot += Qom
        Sr += om_r
        Sz += om_z
    if int(Qtot) == 0:
        ASzQ = NaN
        ASrQ = NaN
    else:
        ASzQ = SzQ/Qtot
        ASrQ = SrQ/Qtot

    charge_counts, bin_edges   = np.histogram(charges, bins = 60, range = (0,3), weights = np.ones(len(charges))*weights)
    charge_err   , bin_edges   = np.histogram(charges, bins = 60, range = (0,3), weights = np.ones(len(charges))*(weights**2))
    frame.Put('charges'         ,dataclasses.I3VectorDouble(charge_counts))
    frame.Put('charges_sw2' ,dataclasses.I3VectorDouble(charge_err))

    depth_counts, bin_edges = np.histogram(depth, bins = 60, range = (-500,500),weights = depth_charges)
    frame.Put('SrQ_NoDC'        ,dataclasses.I3Double(SrQ))
    frame.Put('SzQ_NoDC'        ,dataclasses.I3Double(SzQ))
    frame.Put('SrQN_NoDC'       ,dataclasses.I3Double(SrQN))
    frame.Put('SzQN_NoDC'       ,dataclasses.I3Double(SzQN))
    frame.Put('ASrQ_NoDC'       ,dataclasses.I3Double(ASrQ))
    frame.Put('ASzQ_NoDC'       ,dataclasses.I3Double(ASzQ))
    frame.Put('NChan_NoDC'      ,dataclasses.I3Double(NChan))
    frame.Put('Qtot_NoDC'       ,dataclasses.I3Double(Qtot))
    frame.Put('Sz_NoDC'         ,dataclasses.I3Double(Sz))
    frame.Put('Sr_NoDC'         ,dataclasses.I3Double(Sr))
    #frame.Put('depth'          ,dataclasses.I3VectorDouble(depth_counts))
    frame.Put('event_id'        ,dataclasses.I3Double(event_id))

    pulse_series        = dataclasses.I3RecoPulseSeriesMap.from_frame(frame,'TTPulses')
    Qtot                        = 0
    SrQ                         = 0
    SzQ                         = 0
    ASzQ                        = 0
    ASrQ                        = 0
    Sr                          = 0
    Sz                          = 0
    SrQN                        = 0
    SzQN                        = 0
    NChan = len(pulse_series)
    charges             = []
    depth                       = []
    depth_charges       = []
    for om, pulses in pulse_series:
        om_pos = om_geo[om].position
        om_z = om_pos[2]
        om_r = np.sqrt(om_pos[0]**2+om_pos[1]**2+om_pos[2]**2)
        Qom = 0
        for pulse in pulses:
            Qom += pulse.charge
        SrQ += om_r * Qom
        SzQ += om_z * Qom
        SrQN += om_r * Qom * len(pulses)
        SzQN += om_z * Qom * len(pulses)
        Qtot += Qom
        Sr += om_r
        Sz += om_z
    if int(Qtot) == 0:
        ASzQ = NaN
        ASrQ = NaN
    else:
        ASzQ = SzQ/Qtot
        ASrQ = SrQ/Qtot
    frame.Put('SrQ'             ,dataclasses.I3Double(SrQ))
    frame.Put('SzQ'             ,dataclasses.I3Double(SzQ))
    frame.Put('SrQN'    ,dataclasses.I3Double(SrQN))
    frame.Put('SzQN'    ,dataclasses.I3Double(SzQN))
    frame.Put('ASrQ'    ,dataclasses.I3Double(ASrQ))
    frame.Put('ASzQ'    ,dataclasses.I3Double(ASzQ))
    frame.Put('NChan'   ,dataclasses.I3Double(NChan))
    frame.Put('Qtot'    ,dataclasses.I3Double(Qtot))
    frame.Put('Sz'              ,dataclasses.I3Double(Sz))
    frame.Put('Sr'              ,dataclasses.I3Double(Sr))

    deepCoreStrings = range(79,87)
    TTpulses = dataclasses.I3RecoPulseSeriesMap.from_frame(frame, 'TTPulses')
    track=frame['TrackFit']

    AvgDistQ_NoDC = 0
    AvgDistQ_DC = 0
    Qtot_NoDC = 0
    Qtot_DC = 0

    SzQ_NoDC = 0
    SzQ_DC = 0

    SrQ_NoDC = 0
    SrQ_DC = 0

    for omkey,pulse in TTpulses:
        if omkey[0] in deepCoreStrings:
            om_pos = om_geo[omkey].position
            Dist = phys_services.I3Calculator.closest_approach_distance(track,om_pos)
            Z = om_pos[2]
            R = np.sqrt(om_pos[0]**2+om_pos[1]**2+om_pos[2]**2)
            Qdom = 0
            for q in pulse:
                Qdom+=q.charge
            Qtot_DC += Qdom
            AvgDistQ_DC += Dist * Qdom
            SzQ_DC += Z*Qdom
            SrQ_DC += R*Qdom
        else:
            om_pos=om_geo[omkey].position
            Dist=phys_services.I3Calculator.closest_approach_distance(track,om_pos)
            Z = om_pos[2]
            R = np.sqrt(om_pos[0]**2+om_pos[1]**2+om_pos[2]**2)
            Qdom=0
            for q in pulse:
                Qdom+=q.charge
            Qtot_NoDC += Qdom
            AvgDistQ_NoDC += Dist*Qdom
            SzQ_NoDC += Z*Qdom
            SrQ_NoDC += R*Qdom

    if(Qtot_DC == 0):
        COGz_DC = NaN
        COGr_DC = NaN
        AvgDistQ_DC=NaN
    else:
        COGz_DC = SzQ_DC/Qtot_DC
        COGr_DC = SrQ_DC/Qtot_DC
        AvgDistQ_DC /= Qtot_DC

    if(Qtot_NoDC == 0):
        COGz_NoDC = NaN
        COGr_NoDC = NaN
        AvgDistQ_NoDC=NaN
    else:
        COGz_NoDC = SzQ_NoDC/Qtot_NoDC
        COGr_NoDC = SrQ_NoDC/Qtot_NoDC
        AvgDistQ_NoDC /= Qtot_NoDC

    frame.Put("AvgDistQ_DC"             ,dataclasses.I3Double(AvgDistQ_DC))
    frame.Put("AvgDistQ_NoDC"   ,dataclasses.I3Double(AvgDistQ_NoDC))
    frame.Put("COGz_DC"                 ,dataclasses.I3Double(COGz_DC))
    frame.Put("COGz_NoDC"               ,dataclasses.I3Double(COGz_NoDC))
    frame.Put("COGr_DC"                 ,dataclasses.I3Double(COGr_DC))
    frame.Put("COGr_NoDC"               ,dataclasses.I3Double(COGr_NoDC))

    '''
    TTpulses = dataclasses.I3RecoPulseSeriesMap.from_frame(frame, 'TTPulses')
    track       = frame['TrackFit']
    phi         = track.dir.zenith
    theta   = track.dir.azimuth
    x           = track.pos.x
    y           = track.pos.y
    z           = track.pos.z
    e_x = np.sin(phi)*np.cos(theta)
    e_y = np.sin(phi)*np.sin(theta)
    e_z = np.cos(phi)
    x1 = x + 10000 * e_x
    y1 = y + 10000 * e_y
    z1 = z + 10000 * e_z
    p1 = np.asarray([x1,y1,z1])
    x2 = x - 10000 * e_x
    y2 = y - 10000 * e_y
    z2 = z - 10000 * e_z
    p2 = np.asarray([x2,y2,z2])
    AvgDistQ = 0
    Qtot = 0
    for om, pulses in TTpulses:
        om_pos = om_geo[om].position
        p0 = np.asarray([om_pos[0],om_pos[1],om_pos[2]])
        dist = np.linalg.norm(np.cross(p0-p1,p0-p2))/np.linalg.norm(p2-p1)
        Qdom = 0
        for q in pulse:
            Qdom+=q.charge
        Qtot += Qdom
        AvgDistQ += dist*Qdom
    AvgDistQ = AvgDistQ/Qtot
    frame.Put("my_AvgDistQ"             ,dataclasses.I3Double(AvgDistQ))
    '''
    return True

