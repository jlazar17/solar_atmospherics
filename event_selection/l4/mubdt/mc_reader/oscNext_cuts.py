import numpy as np

as_cuts = [('gt', 'prob_nu_l7_as', 0.4), 
           ('gt', 'prob_nu_l4', 0.95), 
           ('gt', 'reco_z', -500.),
           ('lt', 'reco_z', -200.),
           ('lt', 'reco_rho', 300.),
           ('gt', 'n_hit', 2.5),
           ('lt', 'n_top15', 2.5),
           ('lt', 'n_outer', 7.5),
           ('lt', 'recotime', 14500.),
           ('gte', 'reco_e', 5.0),
           ('lte', 'reco_e', 300.0),
           ('gt', 'reco_coszen', 0.3),
          ]
 
