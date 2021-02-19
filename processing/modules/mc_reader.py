import numpy as np
import h5py as h5
from os import path

from controls import oscNext_nfiles
from helper_functions import mc_fname

params = {'oscNext' : ('oscNext',  
                       lambda path: h5.File(path, 'r'),
                       [('true_e',      '<f8'),
                        ('true_zen',    '<f8'),
                        ('true_az',     '<f8'),
                        ('reco_e',      '<f8'),
                        ('reco_zen',    '<f8'),
                        ('reco_az',     '<f8'),
                        ('oneweight',   '<f8'),
                        ('ptype',       '<i8'),
                        ('trackprob',   '<f8'),
                        ('rweight',     '<f8'),
                        ('passed_muon', '<i8'),
                        ('pass_lowup',  '<i8'),
                       ]
                      ),
          'intracks': ('intracks', 
                       lambda path: np.load(path)
                       [('true_e',    '<f8'),
                        ('true_zen',  '<f8'),
                        ('true_az',   '<f8'),
                        ('reco_e',    '<f8'),
                        ('reco_zen',  '<f8'),
                        ('reco_az',   '<f8'),
                        ('oneweight', '<f8'),
                        ('ptype',     '<i8'),
                       ]
                      ),
          'nancy'   : ('LowUp',
                       lambda path: h5.File(path, 'r'),
                       [('true_e',    '<f8'),
                        ('true_zen',  '<f8'),
                        ('true_az',   '<f8'),
                        #('reco_e',    '<f8'),
                        ('reco_zen',  '<f8'),
                        ('reco_az',   '<f8'),
                        ('oneweight', '<f8'),
                        ('eff_oneweight', '<f8'),
                        ('ptype',     '<i8'),
                        ('qtot',      '<f8'),
                        ('rlogl',     '<f8'),
                        ('ztravel',   '<f8'),
                        ('cogz',      '<f8'),
                        ('cogzsigma', '<f8'),
                       ]
                      ),
          'genie'   : ('LowUp',
                       lambda path: h5.File(path, 'r'),
                       [('true_e',    '<f8'),
                        ('true_zen',  '<f8'),
                        ('true_az',   '<f8'),
                        #('reco_e',    '<f8'),
                        ('reco_zen',  '<f8'),
                        ('reco_az',   '<f8'),
                        ('oneweight', '<f8'),
                        ('eff_oneweight', '<f8'),
                        ('ptype',     '<i8'),
                        ('qtot',      '<f8'),
                        ('rlogl',     '<f8'),
                        ('ztravel',   '<f8'),
                        ('cogz',      '<f8'),
                        ('cogzsigma', '<f8'),
                       ]
                      )
         }

class MCReader(object):

    def __init__(self, path=None, name=None, mc_data=None, options='00', additional_data=None):

        self.options         = options
        self._path           = path
        self.additional_data = additional_data
        if path is not None:
            self.fname = mc_fname(path)
            self.set_name()
            _, loader, self._dtypes = params[self.name]
            self.mcf  = loader(path)
        else:
            self.name    = name
            self._dtypes = []
            loader       = None
        self.set_mc_data()

        if hasattr(loader, 'close'):
            loader.close()

    def __add__(self, other):
        shared_dnames = list(set(self.mc_data.dtype.names) & set(other.mc_data.dtype.names))
        data          = [(np.append(self.mc_data[name], other.mc_data[name]), name, dtype)
                         for name, dtype in self.mc_data.dtype.descr
                         if name in shared_dnames
                        ]
        name = '%s-%s' % (self.name, other.name)
        return MCReader(additional_data=data, name=name)

    def __len__(self):
        return len(self.mc_data)

    def set_name(self):
        if 'hmniederhausen/' in self._path:
            self.name = 'intracks'
        elif ('oscNext' in self._path):
            self.name = 'oscNext'
        elif 'JLevel' in self._path:
            if 'nancy' in self._path:
                self.name = 'nancy'
            elif 'genie' in self._path:
                self.name = 'genie'
        else:
            print('Event selection not recognized')
            quit()

    def set_mc_data(self):
        if self.name=='nancy' or self.name=='genie':
            data = [
                    self.mcf["TrueEnergy"][()],
                    self.mcf["TrueZenith"][()],
                    self.mcf["TrueAzimuth"][()],
                    self.mcf["RecoZenith"][()],
                    self.mcf["RecoAzimuth"][()],
                    self.mcf["eff_oneweight"][()],
                    self.mcf["eff_oneweight"][()],
                    self.mcf['PrimaryType'][()],
                    self.mcf['QTot'][()],
                    self.mcf['RLogL'][()],
                    self.mcf['COGZ'][()],
                    self.mcf['COGZSigma'][()],
                    self.mcf['ZTravel'][()],
                   ]

        elif self.name=='intracks':
            data = [
                    self.mcf['trueE'],
                    self.mcf['trueDec']+np.pi/2,
                    self.mcf['trueAzi'],
                    np.power(10, self.mcf['logE']),
                    self.mcf['dec']+np.pi/2,
                    self.mcf['azi'],
                    self.mcf['ow'],
                    # TODO find actual particle type information
                    np.where(np.random.rand(len(self.nu_az))<0.4511734444723442, 14,-14),
                   ]
        elif self.name=='oscNext':
            nu_e         = []
            nu_az        = []
            nu_zen       = []
            reco_e       = []
            reco_az      = []
            reco_zen     = []
            ptype        = []
            trackprob    = []
            oneweight    = []
            rweight      = []
            passed_muon  = []
            passed_lowup = []
            for key in self.mcf.keys():
                true_e    = np.append(nu_e, self.mcf[key]['MCInIcePrimary.energy'][()])
                true_az   = np.append(nu_az, self.mcf[key]['MCInIcePrimary.dir.azimuth'][()])
                true_zen  = np.append(nu_zen, np.arccos(self.mcf[key]['MCInIcePrimary.dir.coszen'][()]))
                reco_e    = np.append(reco_e, self.mcf[key]['L7_reconstructed_total_energy'][()])
                reco_az   = np.append(reco_az, self.mcf[key]['L7_reconstructed_azimuth'][()])
                reco_zen  = np.append(reco_zen, np.arccos(self.mcf[key]['L7_reconstructed_coszen'][()]))
                ptype     = np.append(ptype, self.mcf[key]['MCInIcePrimary.pdg_encoding'][()])
                trackprob = np.append(trackprob, self.mcf[key]['L7_PIDClassifier_FullSky_ProbTrack'][()])
                oneweight = np.append(oneweight, self.mcf[key]['I3MCWeightDict.OneWeight'][()] / (self.mcf[key]['I3MCWeightDict.NEvents'][()] * self.mcf[key]['I3MCWeightDict.gen_ratio'][()] * oscNext_nfiles[key]))
                rweight   = np.append(rweight, self.mcf[key]['ReferenceWeight'][()])
                passed_lowup = np.append(passed_muon, 
                                              self.mcf[key]['FilterMask.LowUp_13.prescale_passed'][()] * self.mcf[key]['FilterMask.LowUp_13.condition_passed'][()]
                                             ) 
                passed_muon  = np.append(passed_muon, 
                                              self.mcf[key]['FilterMask.MuonFilter_13.prescale_passed'][()] * self.mcf[key]['FilterMask.MuonFilter_13.condition_passed'][()]
                                             )
            data = [
                    true_e,
                    true_zen,
                    true_az,
                    reco_e,
                    reco_zen,   
                    reco_az,
                    oneweight,
                    ptype,
                    trackprob,
                    rweight,
                    passed_muon,
                    passed_lowup,
                   ]
        else:
            data = []
        if self.additional_data is not None:
            for data_arr, dname, dtype in self.additional_data:
                data.append(data_arr)
                self._dtypes.append((dname,dtype))

        arr = np.array([tup for tup in zip(*tuple(data))],
                       dtype=self._dtypes
                      )
        self.mc_data = arr.view(np.recarray)

if __name__=='__main__':
    from  sys import argv as args
    path = args[1]
    mcr = MCReader(path)
    print(len(mcr.nu_e))
