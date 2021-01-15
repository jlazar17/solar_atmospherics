from selector import selector
from icecube import icetray
import numpy as np

def planL3Cut(frame):
	if((splitFrames & (afterpulses | ~keepL3))(frame)):
		frame.Put("CutL3",icetray.I3Bool(True))

@selector
def keepL3(frame, cut):
    if(frame.Stop!=icetray.I3Frame.Physics):
        return(True)
    id = frame["I3EventHeader"].run_id,frame["I3EventHeader"].event_id,frame["I3EventHeader"].sub_event_id

    # We require that we had a good enough fit. The fallback.value represents what level of fit was sucessfull.
    fallback = frame.Get("TrackFitFallback")
    if(fallback.value > 2):
        return(False)

    # Let's select some initial cuts.
    # dh: direct hit information
    # hm: hit multiplicity
    # Note: we typically cut while ignoring DeepCore.

    track         = frame.Get("TrackFit")
    track_NoDC_dh = frame.Get("TrackFit_NoDC_dh")
    pulse_NoDC_hm = frame.Get("TTPulses_NoDC_hm")

    #frame.Put("trackfit_cuts_noDC_nchan",dataclasses.I3Double(frame.Get("TrackFitCuts_NoDC").nchan))
    #cuts = frame.Get("TrackFitCuts_NoDC")
    #frame.Put("trackfit_cuts_noDC_nchan",dataclasses.I3Double(frame.Get("TTPulses_NoDC_hm").n_hit_doms))
    #frame.Put("trackfit_cuts_noDC_nchan",dataclasses.I3Double(frame.Get("TTPulses_NoDC_hm").n_hit_doms))

    if(np.cos(track.dir.zenith) > 0.1):
        if cut:
            return(False)
    if(float(pulse_NoDC_hm.n_hit_doms) < 30.):
        if cut:
            return(False)
    if(np.cos(track.dir.zenith) > 0.0 and float(pulse_NoDC_hm.n_hit_doms) < 30.0 * np.exp(17.0*np.cos(track.dir.zenith))):
        if cut:
            return(False)

    #frame.Put("trackfit_cuts_nchan",dataclasses.I3Double(frame.Get("TrackFitCuts").nchan))

    if(not doExpensiveRecos(frame)):
        return(False)
    sigma = frame.Get("CorrectedParaboloidSigma")
    llhparams = frame.Get("TrackFitFitParams")
    frame.Put("RLogL",dataclasses.I3Double(llhparams.rlogl))
    frame.Put("Sigma",dataclasses.I3Double(sigma.value))
    if(sigma.value<2.5679769135e-2 and (llhparams.rlogl>(-42.967631051274708*sigma.value+8.6))):
        if cut:
            return(False)
    if(sigma.value>2.5679769135e-2 and (llhparams.rlogl>(-5.0*sigma.value+7.625))):
        if cut:
            return(False);
    bayes = frame.Get("TrackFitBayesian")
    bayesparams = frame.Get("TrackFitBayesianFitParams")
    speparams = frame.Get("SPEFit4_TTFitParams")

    if(bayes.fit_status==dataclasses.I3Particle.OK):
        frame.Put("bayes_fit_status",dataclasses.I3Double(1))
        llhdiff=bayesparams.logl-speparams.logl
        frame.Put("BayesLLHR",dataclasses.I3Double(llhdiff))
        if(np.cos(track.dir.zenith)<0.0 and llhdiff<33):
            if cut:
                return(False)
        if(np.cos(track.dir.zenith)>=0.0):
            if(llhdiff<(33-86*np.cos(track.dir.zenith))):
                if cut:
                    return(False)
            if(llhdiff>(75.-45*np.sqrt(1-np.power((np.cos(track.dir.zenith)-.1)/.1,2)))):
                if cut:
                    return(False)
    else:
        #print("bayes_fit_status FAILED")
        frame.Put("bayes_fit_status",dataclasses.I3Double(0))
        frame.Put("BayesLLHR",dataclasses.I3Double(float('NaN')))

    track_dh = frame.Get("TrackFit_dh")

    geosplit1 = frame.Get("SPEFit4SplitGeo1")
    geosplit2 = frame.Get("SPEFit4SplitGeo2")
    if(geosplit1.fit_status==dataclasses.I3Particle.OK and geosplit2.fit_status==dataclasses.I3Particle.OK):
        geocuts1 = frame.Get("SPEFit4SplitGeo1_dh")
        geocuts2 = frame.Get("SPEFit4SplitGeo2_dh")
        if((geocuts1.n_dir_doms + geocuts2.n_dir_doms) > 2 * track_dh.n_dir_doms):
            return(False)
        else:
            pass
    
    timesplit1 = frame.Get("SPEFit4SplitTime1")
    timesplit2 = frame.Get("SPEFit4SplitTime2")
    if(timesplit1.fit_status == dataclasses.I3Particle.OK and timesplit2.fit_status == dataclasses.I3Particle.OK):
        timecuts1 = frame.Get("SPEFit4SplitTime1_dh")
        timecuts2 = frame.Get("SPEFit4SplitTime2_dh")
        if((timecuts1.n_dir_doms + timecuts2.n_dir_doms) > 2 * track_dh.n_dir_doms):
            return(False)
        else:
            pass
    '''
    if geosplit1.fit_status==dataclasses.I3Particle.OK:
            frame.Put("geo_split1_fit_status",dataclasses.I3Double(1))
            frame.Put("geo_split1_dir_n",dataclasses.I3Double(frame.Get("SPEFit4SplitGeo1Cuts").ndir))
    else:
            #print("geosplit1_status FAILED")
            frame.Put("geo_split1_fit_status",dataclasses.I3Double(0))
            frame.Put("geo_split1_dir_n",dataclasses.I3Double(float('NaN')))

            if geosplit2.fit_status==dataclasses.I3Particle.OK:
                            frame.Put("geo_split2_fit_status",dataclasses.I3Double(1))
            frame.Put("geo_split2_dir_n",dataclasses.I3Double(frame.Get("SPEFit4SplitGeo2Cuts").ndir))
            else:
            #print("geosplit2_status FAILED")
                            frame.Put("geo_split2_fit_status",dataclasses.I3Double(0))
            frame.Put("geo_split2_dir_n",dataclasses.I3Double(float('NaN')))

    if timesplit1.fit_status==dataclasses.I3Particle.OK:
            frame.Put("time_split1_fit_status",dataclasses.I3Double(1))
            frame.Put("time_split1_dir_n",dataclasses.I3Double(frame.Get("SPEFit4SplitTime1Cuts").ndir))
    else:
            #print("timesplit1_status FAILED")
            frame.Put("time_split1_fit_status",dataclasses.I3Double(0))
            frame.Put("time_split1_dir_n",dataclasses.I3Double(float('NaN')))

            if timesplit2.fit_status==dataclasses.I3Particle.OK:
                            frame.Put("time_split2_fit_status",dataclasses.I3Double(1))
                    frame.Put("time_split2_dir_n",dataclasses.I3Double(frame.Get("SPEFit4SplitTime2Cuts").ndir))
    else:
            #print("timesplit2_status FAILED")
                            frame.Put("time_split2_fit_status",dataclasses.I3Double(0))
            frame.Put("time_split2_dir_n",dataclasses.I3Double(float('NaN')))
    '''
    frame.Put("TTPulses_NChan",dataclasses.I3Double(frame.Get("TTPulses_hm").n_hit_doms))
    frame.Put("TTPulses_NoDC_NChan",dataclasses.I3Double(frame.Get("TTPulses_NoDC_hm").n_hit_doms))
    frame.Put("Dir_N",dataclasses.I3Double(frame.Get("TrackFit_dh").n_dir_doms))
    frame.Put("Dir_S",dataclasses.I3Double(frame.Get("TrackFit_dh").dir_track_hit_distribution_smoothness))
    frame.Put("Dir_L",dataclasses.I3Double(frame.Get("TrackFit_dh").dir_track_length))
    frame.Put("Dir_N_NoDC",dataclasses.I3Double(frame.Get("TrackFit_NoDC_dh").n_dir_doms))
    frame.Put("Dir_S_NoDC",dataclasses.I3Double(frame.Get("TrackFit_NoDC_dh").dir_track_hit_distribution_smoothness))
    frame.Put("Dir_L_NoDC",dataclasses.I3Double(frame.Get("TrackFit_NoDC_dh").dir_track_length))
    return(True)

