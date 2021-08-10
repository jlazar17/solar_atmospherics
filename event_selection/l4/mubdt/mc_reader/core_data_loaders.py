
def core_lowup_data_patch(path):
    import h5py as h5
    mcf  = h5.File(path, 'r')
    data = [
            (mcf["TrueEnergy"][()],    'true_e',        '<f8'),
            (mcf["TrueZenith"][()],    'true_zen',      '<f8'),
            (mcf["TrueAzimuth"][()],   'true_az',       '<f8'),
            (mcf["RecoZenith"][()],    'reco_zen',      '<f8'),
            (mcf["RecoAzimuth"][()],   'reco_az',       '<f8'),
            (mcf["eff_oneweight"][()], 'oneweight',     '<f8'),
            (mcf["eff_oneweight"][()], 'eff_oneweight', '<f8'),
            (mcf['PrimaryType'][()],   'ptype',         '<f8'),
            (mcf['QTot'][()],          'qtot',          '<f8'),
            (mcf['RLogL'][()],         'rlogl',         '<f8'),
            (mcf['ZTravel'][()],       'ztravel',       '<f8'),
            (mcf['COGZ'][()],          'cogz',          '<f8'),
            (mcf['COGZSigma'][()],     'cogzsigma',     '<f8'),
           ]
    mcf.close()
    return data


def core_lowup_data(path):
    import h5py as h5
    mcf  = h5.File(path, 'r')
    data = [
            (mcf["TrueEnergy"][()],    'true_e',        '<f8'),
            (mcf["TrueZenith"][()],    'true_zen',      '<f8'),
            (mcf["TrueAzimuth"][()],   'true_az',       '<f8'),
            (mcf["RecoZenith"][()],    'reco_zen',      '<f8'),
            (mcf["RecoAzimuth"][()],   'reco_az',       '<f8'),
            (mcf["eff_oneweight"][()], 'oneweight',     '<f8'),
            (mcf["eff_oneweight"][()], 'eff_oneweight', '<f8'),
            (mcf['PrimaryType'][()],   'ptype',         '<i8'),
            (mcf['QTot'][()],          'qtot',          '<f8'),
            (mcf['RLogL'][()],         'rlogl',         '<f8'),
            (mcf['ZTravel'][()],       'ztravel',       '<f8'),
            (mcf['COGZ'][()],          'cogz',          '<f8'),
            (mcf['COGZSigma'][()],     'cogzsigma',     '<f8'),
           ]
    mcf.close()
    return data

def core_ps_data(path):
    import numpy as np
    mcf  = np.load(path)
    # TODO find actual particle type information
    np.random.seed(31415)
    ptype = np.where(np.random.rand(len(mcf['trueE']))<0.4511734444723442, 14,-14)
    data = [(mcf['trueE'],              'true_e',    '<f8'),
            (mcf['trueDec']+np.pi/2,    'true_zen',  '<f8'),
            (mcf['trueAzi'],            'true_az',   '<f8'),
            (np.power(10, mcf['logE']), 'reco_e',    '<f8'),
            (mcf['dec']+np.pi/2,        'reco_zen',  '<f8'),
            (mcf['azi'],                'reco_az',   '<f8'),
            (mcf['ow']/0.5,             'oneweight', '<f8'), # To account for nugen ratio
            (ptype,                     'ptype',     '<i8'),
           ]
    return data

def core_oscNext_data(path):
    from solar_common import oscNext_nfiles
    from .oscNext_definitions import oscNextDefs
    import h5py as h5
    import numpy as np
    mcf  = h5.File(path, 'r')
    data_dict = {}
    oneweight = []
    for key in oscNextDefs.keys():
        data_dict[key] = []

    for intkey in mcf.keys():
        oneweight = np.append(oneweight, mcf[intkey]['I3MCWeightDict.OneWeight'][()] / (mcf[intkey]['I3MCWeightDict.NEvents'][()] * mcf[intkey]['I3MCWeightDict.gen_ratio'][()] * oscNext_nfiles[intkey]))
        for key, val in oscNextDefs.items():
            data_dict[key] = np.append(data_dict[key], mcf[intkey][val][()])

    data = []
    for key in oscNextDefs.keys():
        if key in ['passed_lowup', 'passed_muon', 'ptype']:
            data.append((data_dict[key], key, 'i8'))
        else:
            data.append((data_dict[key], key, 'f8'))
    del data_dict
    mcf.close()
    return data

def core_oscNext_muon_data(path):
    from solar_common import oscNext_nfiles
    from .oscNext_definitions import oscNextDefs
    import h5py as h5
    import numpy as np
    mcf  = h5.File(path, 'r')
    data_dict = {}
    for key in oscNextDefs.keys():
        data_dict[key] = []

    for intkey in mcf.keys():
        for key, val in oscNextDefs.items():
            data_dict[key] = np.append(data_dict[key], mcf[intkey][val][()])

    data = []
    for key in oscNextDefs.keys():
        if key in ['passed_lowup', 'passed_muon', 'ptype']:
            data.append((data_dict[key], key, 'i8'))
        else:
            data.append((data_dict[key], key, 'f8'))
    del data_dict
    mcf.close()
    return data

core_data_loaders = {
                     'genie':core_lowup_data,
                     'nancy':core_lowup_data,
                     'oscNext':core_oscNext_data,
                     'oscNext_muon':core_oscNext_muon_data,
                     'intracks':core_ps_data,
                     'ntracks':core_ps_data,
                     'corsika':core_lowup_data_patch,
                    }
