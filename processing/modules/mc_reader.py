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
          'LowUp'   : ('LowUp',
                       lambda path: h5.File(path, 'r'),
                       [('true_e',    '<f8'),
                        ('true_zen',  '<f8'),
                        ('true_az',   '<f8'),
                        #('reco_e',    '<f8'),
                        ('reco_zen',  '<f8'),
                        ('reco_az',   '<f8'),
                        ('oneweight', '<f8'),
                        ('ptype',     '<i8'),
                        ('qtot',      '<f8'),
                        ('rlogl',     '<f8'),
                       ]
                      )
         }

class MCReader():

    def __init__(self, path, flux=None, slc=slice(None), emin=0, emax=np.inf, options='00'):
        self.path  = path
        self.fname = mc_fname(path)
        if flux is not None:
            self.flux  = flux[slc]
        else:
            self.flux = flux
        self.slc   = slc
        self.emin  = emin
        self.emax  = emax
        self.options = options

        self.set_event_selection()
        _, loader, self._dtypes = params[self.event_selection]
        self.mcf  = loader(self.path)

        self.set_mc_quantities()
        if self.event_selection=='oscNext': # Cut requires information only available in ON
            self.apply_filter_mask()
        if not (self.emin==0 and self.emax==np.inf): # don't do cut if trivial
            self.apply_energy_mask()

        if hasattr(loader, 'close'):
            loader.close()

    def set_event_selection(self):
        if 'hmniederhausen/' in self.path:
            self.event_selection = 'intracks'
        elif ('oscNext' in self.path):
            self.event_selection = 'oscNext'
        elif 'JLevel' in self.path:
            self.event_selection = 'LowUp'
        else:
            print('Event selection not recognized')
            quit()

    def apply_energy_mask(self):
        mask = np.where(np.logical_and(self.mc_data.nu_e>self.emin, self.mc_data.nu_e<self.emax))[0]
        self.mc_data = self.mc_data[mask]
        if self.flux is not None:
            self.flux      = self.flux[mask]

    def apply_filter_mask(self):
        if self.options=='00':
            return
        elif self.options=='11': # Omit both lowup and muon filter
            mask = np.where((1-self.passed_muon)*(1-self.passed_lowup)==1)[0]
        elif self.options=='01': # Omit lowup filter only
            mask = np.where(self.passed_lowup==0)
        elif self.options=='10': # Omit muon filter only
            mask = np.where(self.passed_lowup==0)
        else:
            raise RuntimeError
        self.mc_data = self.mc_data[mask]
        if self.flux is not None:
            self.flux      = self.flux[mask]

    def set_mc_quantities(self):
        if self.event_selection=='LowUp':
            true_e    = self.mcf["TrueEnergy"][()][self.slc]
            true_zen  = self.mcf["TrueZenith"][()][self.slc]
            true_az   = self.mcf["TrueAzimuth"][()][self.slc]
            #self.reco_e    = self.mcf["MuExEnergy"][()][self.slc]
            reco_zen  = self.mcf["RecoZenith"][()][self.slc]
            reco_az   = self.mcf["RecoAzimuth"][()][self.slc]
            oneweight = self.mcf["eff_oneweight"][()][self.slc]
            ptype     = self.mcf['PrimaryType'][()][self.slc]
            qtot      = self.mcf['QTot'][()][self.slc]
            rlogl     = self.mcf['RLogL'][()][self.slc]
            arr = np.array([tup for tup in zip(true_e, 
                                               true_zen, 
                                               true_az, 
                                               #reco_e, 
                                               reco_zen, 
                                               reco_az, 
                                               oneweight, 
                                               ptype,
                                               qtot,
                                               rlogl,
                                              )
                           ],
                           dtype=self._dtypes
                          )
            self.mc_data = arr.view(np.recarray)
        if self.event_selection=='intracks':
            nu_e      = self.mcf['trueE']
            nu_az     = self.mcf['trueAzi']
            nu_zen    = self.mcf['trueDec']+np.pi/2
            reco_e    = np.power(10, self.mcf['logE'])
            reco_az   = self.mcf['azi']
            reco_zen  = self.mcf['dec']+np.pi/2
            oneweight = self.mcf['ow']
            # TODO find actual particle type information
            ptype     = np.where(np.random.rand(len(self.nu_az))<0.4511734444723442, 14,-14)
            arr = np.array([tup for tup in zip(true_e, 
                                               true_zen, 
                                               true_az, 
                                               reco_e, 
                                               reco_zen, 
                                               reco_az, 
                                               oneweight, 
                                               ptype
                                              )
                           ],
                           dtype=self._dtypes
                          )
            self.mc_data = arr.view(np.recarray)
        elif self.event_selection=='oscNext':
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
            arr = np.array([tup for tup in zip(true_e, 
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
                                              )
                           ],
                           dtype=self._dtypes
                          ),
            self.mc_data = arr.view(np.recarray)

if __name__=='__main__':
    from  sys import argv as args
    path = args[1]
    mcr = MCReader(path)
    print(len(mcr.nu_e))
