import getopt, sys

import h5py as h5
import numpy as np
import pandas as pd

from sklearn.experimental import enable_hist_gradient_boosting
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split

# helper functions to read in big data files
from read_h5_chunk import read_file_in_chunks
from mc_reader import MCReader

# helper function to separate signal and background events
def sig_bkg_split(X, y, weights):
    '''
    Splits X and y into signal and background sets with weights
    
    Parameters
    ----------
    - X (DataFrame): features
    - y (DataFrame): signal indicator (1 if signal, 0 if background)
    - weights (DataFrame): weights of events
    
    Returns
    -------
    - X_sig, X_bkg, w_sig, w_bkg (dataFrame tuple): data organized according to signal/background status 
    '''
    # get signal and background mask
    sig_mask = y.loc[y.values==1].index
    bkg_mask = y.loc[y.values==0].index

    return X.loc[sig_mask], X.loc[bkg_mask], weights.loc[sig_mask], weights.loc[bkg_mask]

# helper function to compute score separation
def compute_separation(sig_probs, bkg_probs, sig_weights, bkg_weights, bins=300):
    '''
    Comuputes the maximum separation between two histograms. For classification tasks,
    this helper function is useful because if you can maximize this quantity, you can maximize the
    separation between classification probability distributions to improve accuracy.
    
    Parameters:
    -----------
    - sig_probs (ndarray): signal set prediction probabilities
    - bkg_probs (ndarray): background set prediction probabilities
    - sig_weights (ndarray): sample weights for signal set
    - bkg_probs (ndarray): sample weights for background set
    - bins (int): number of bins with which to create histogram to compute maximum separation
    
    Returns:
    --------
    - max_sep (float): maximum separation between cumulative weighted probability distributions
    '''
    
    # histogram data
    sig_hist, _ = np.histogram(sig_probs, weights=sig_weights, bins=bins)
    sig_hist = np.cumsum(sig_hist)
    bkg_hist, _ = np.histogram(bkg_probs, weights=bkg_weights, bins=bins)
    bkg_hist = np.cumsum(bkg_hist)
    
    return np.max(sig_hist - bkg_hist)

def main(argv):

    # instantiate  hyperparameters for testing
    learning_rate = 0.1
    regularization = 0.1
    max_leaf_nodes = 45

    # usage and parameter parsing
    try:
        opts, args = getopt.getopt(argv, 'hl:r:m:', ['learning_rate=','regularization=','max_leaf_nodes='])
    except getopt.GetoptError:
        print('Usage: test.py -l <learning_rate> -r <regularization> -m <max_leaf_nodes>', flush=True)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('Usage: test.py -l <learning_rate> -r <regularization> -m <max_leaf_nodes>', flush=True)
            sys.exit()
        elif opt in ('-l', '--learning_rate'):
            learning_rate = float(arg)
        elif opt in ('-r', '--regularization'):
            regularization = float(arg)
        elif opt in ('-m', '--max_leaf_nodes'):
            max_leaf_nodes = int(arg)

    # get outkeys
    all_keys = [
                ('ZTravel',       '<f8'),
                ('oneweight',     '<f8'),
                ('eff_oneweight', '<f8'),
                ('COGZ',          '<f8'),
                ('COGZSigma',     '<f8'),
                ('TrueEnergy',    '<f8'),
                ('TrueZenith',    '<f8'),
                ('TrueAzimuth',   '<f8'),
                ('PrimaryType',   '<f8'),
                ('RLogL',         '<f8'),
                ('RecoAzimuth',   '<f8'),
                ('RecoZenith',    '<f8'),
                ('QTot',          '<f8'),
                ('LDir_A',        '<f8'),
                ('NDirPulse_A',   '<f8'),
                ('NDirDOM_A',     '<f8'),
                ('NDirStr_A',     '<f8'),
                ('LDir_B',        '<f8'),
                ('NDirPulse_B',   '<f8'),
                ('NDirDOM_B',     '<f8'),
                ('NDirStr_B',     '<f8'),
                ('LDir_C',        '<f8'),
                ('NDirPulse_C',   '<f8'),
                ('NDirDOM_C',     '<f8'),
                ('NDirStr_C',     '<f8'),
                ('LDir_E',        '<f8'),
                ('NDirPulse_E',   '<f8'),
                ('NDirDOM_E',     '<f8'),
                ('NDirStr_E',     '<f8'),
                ('RecoAngSep',    '<f8'),
                ('BayesRatio',    '<f8')
               ]

    dropkeys = ['oneweight', 'TrueEnergy', 'TrueZenith', 'TrueAzimuth', 'PrimaryType', 'RecoAzimuth', 'NDirDOM_C', 'NDirDOM_E', 'BayesRatio']
    outkeys = [key for key, _ in all_keys if key not in dropkeys]

    # thinning for MC reading
    thin = 100

    # read in fluxes
    print('reading in fluxes...', flush=True)
    conv_flux_nancy_path = '/data/user/jlazar/solar/data/mc_dn_dz/sibyll23c_conv_l3_b_nancy_merged_holeice-0300_2.npy'
    solar_flux_nancy_path = '/data/user/jlazar/solar/data/mc_dn_dz/SIBYLL2.3_pp_HillasGaisser_H4a_l3_b_nancy_merged_holeice-0300_2.npy'
    conv_flux_genie_path = '/data/user/jlazar/solar/data/mc_dn_dz/sibyll23c_conv_l3_b_genie_merged_holeice-0300_2.npy'
    solar_flux_genie_path = '/data/user/jlazar/solar/data/mc_dn_dz/SIBYLL2.3_pp_HillasGaisser_H4a_l3_b_genie_merged_holeice-0300_2.npy'
    
    conv_flux_nancy = np.load(conv_flux_nancy_path)[::thin]
    solar_flux_nancy = np.load(solar_flux_nancy_path)[::thin]
    conv_flux_genie = np.load(conv_flux_genie_path)[::thin]
    solar_flux_genie = np.load(solar_flux_genie_path)[::thin]

    # read in data
    print('reading in data...', flush=True)
    genie_path = '/data/user/jlazar/big_files/solar_atmospherics/l3_b_genie_merged_holeice-0300_2.h5'
    genie = read_file_in_chunks(genie_path, outkeys, thin=thin)
    
    nancy_path = '/data/user/jlazar/big_files/solar_atmospherics/l3_b_nancy_merged_holeice-0300_2.h5'
    nancy = read_file_in_chunks(nancy_path, outkeys, thin=thin)
    
    corsika_path = '/data/user/jlazar/big_files/solar_atmospherics/l3_b_corsika_merged_holeice-0300_2.h5'
    corsika = read_file_in_chunks(corsika_path, outkeys, thin=thin)

    ### convert data into pandas dataframes ###
    print('converting data...', flush=True)
    # convert to particle-specific dataframes
    solar_df = pd.concat([pd.DataFrame(nancy), pd.DataFrame(genie)])
    conv_df = pd.concat([pd.DataFrame(nancy), pd.DataFrame(genie)])
    muon_df = pd.DataFrame(corsika)
    
    # total flux
    solar_flux = np.concatenate([solar_flux_nancy, solar_flux_genie])
    conv_flux = np.concatenate([conv_flux_nancy, conv_flux_genie])
    
    # normalized rate information
    muon_df['norm-rate'] = muon_df['eff_oneweight'].values / np.sum(muon_df['eff_oneweight'])
    solar_df['norm-rate'] = solar_df['eff_oneweight'] * solar_flux / np.sum(solar_df['eff_oneweight']*solar_flux)
    conv_df['norm-rate'] = conv_df['eff_oneweight'] * conv_flux / np.sum(conv_df['eff_oneweight']*conv_flux)
    
    # add in solar atmospheric info
    solar_df['solar'] = 1
    conv_df['solar'] = 0
    muon_df['solar'] = 0
    
    # add in muon info
    solar_df['muon'] = 0
    conv_df['muon'] = 0
    muon_df['muon'] = 1

    # combine all dataframes
    data = pd.concat([muon_df, solar_df, conv_df])
    data = data.reset_index(drop=True)
    data = data.drop(columns=['eff_oneweight'])

    # split into training and test sets (for muon BDT)
    X, y_muon, y_solar = data.drop(columns=['solar', 'muon']), data['muon'], data['solar']
    X_train, X_test, y_train, y_test = train_test_split(X, y_muon)
    test_weights = X_test['norm-rate']
    X_test = X_test.drop(columns='norm-rate')

    ### training and cross-validating ###
    # accuracy scores
    acc_train, acc_val = [], []

    # separation scores
    sep_train, sep_val = [], []

    # perform 5fold CV
    print('training and CV...', flush=True)
    for i in range(1):
        
        # split into training and validation (validation frac 20%)
        X_train1, X_val, y_train1, y_val = train_test_split(X_train, y_train, test_size=0.2)
        train_weights, val_weights = X_train1['norm-rate'], X_val['norm-rate']
        X_train1 = X_train1.drop(columns='norm-rate')
        X_val = X_val.drop(columns='norm-rate')

        # instantiate BDT
        bdt = HistGradientBoostingClassifier(learning_rate=learning_rate, max_leaf_nodes=max_leaf_nodes, l2_regularization=regularization,
                                             max_iter=5000, tol=5e-8, verbose=0)
        print(f'fitting BDT {i}...', flush=True)
        # train
        bdt.fit(X_train1, y_train1, train_weights)

        # get training and validation background/signal sets
        train_sig, train_bkg, train_sig_weights, train_bkg_weights = sig_bkg_split(X_train1, y_train1, train_weights)
        val_sig, val_bkg, val_sig_weights, val_bkg_weights = sig_bkg_split(X_val, y_val, val_weights)
        
        # get accuracy scores
        print(f'scoring BDT {i}...', flush=True)
        acc_train.append(bdt.score(X_train1, y_train1, train_weights))
        acc_val.append(bdt.score(X_val, y_val, val_weights))

        # get predicted probabilities
        train_sig_probs = muBDT.predict_proba(train_sig)[:, 1]
        train_bkg_probs = muBDT.predict_proba(train_bkg)[:, 1]
        val_sig_probs = muBDT.predict_proba(val_sig)[:, 1]
        val_bkg_probs = muBDT.predict_proba(val_bkg)[:, 1]

        # compute separation
        bins = 300
        sep_train.append(compute_separation(train_sig_probs, train_bkg_probs, train_sig_weights, train_bkg_weights, bins=bins))
        sep_val.append(compute_separation(val_sig_probs, val_bkg_probs, val_sig_weights, val_bkg_weights, bins=bins))
        
    # compute outputs
    acc_train_mean, acc_train_std = np.mean(acc_train), np.std(acc_train)
    sep_train_mean, sep_train_std = np.mean(sep_train), np.std(sep_train)
    acc_val_mean, acc_val_std = np.mean(acc_val), np.std(acc_val)
    sep_val_mean, sep_val_std = np.mean(sep_val), np.std(sep_val)    
    
    # write to file
    print('writing...', flush=True)
    with open('/data/user/jvillarreal/solar_atmospherics/bdt/out_mubdt.csv', 'a') as file:
        file.write(f'{learning_rate},{regularization},{max_leaf_nodes},{acc_train_mean},{acc_train_std},{sep_train_mean},{sep_train_std},{acc_val_mean},{acc_val_std},{sep_val_mean},{sep_val_std}\n')
    
    print(f'results for {learning_rate} {regularization} {max_leaf_nodes}', flush=True)    
    print('acc train mean:', acc_train_mean, flush=True)
    print('sep train mean:', sep_train_mean, flush=True)
    print('acc val mean:', acc_val_mean, flush=True)
    print('sep val std:', sep_val_std, flush=True)

    return 0

if __name__ == '__main__':
    main(sys.argv[1:]) 
