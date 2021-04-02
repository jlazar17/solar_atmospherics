corsika_gcdc_dict = {20787:"/cvmfs/icecube.opensciencegrid.org/data/GCD/GeoCalibDetectorStatus_AVG_55697-57531_PASS2_SPE_withStdNoise.i3.gz",
                     20788:"/cvmfs/icecube.opensciencegrid.org/data/GCD/GeoCalibDetectorStatus_AVG_55697-57531_PASS2_SPE_withStdNoise.i3.gz",
                     20789:"/cvmfs/icecube.opensciencegrid.org/data/GCD/GeoCalibDetectorStatus_AVG_55697-57531_PASS2_SPE_withStdNoise.i3.gz",
                     20848:"/cvmfs/icecube.opensciencegrid.org/data/GCD/GeoCalibDetectorStatus_AVG_55697-57531_PASS2_SPE_withStdNoise.i3.gz",
                     20849:"/cvmfs/icecube.opensciencegrid.org/data/GCD/GeoCalibDetectorStatus_AVG_55697-57531_PASS2_SPE_withStdNoise.i3.gz",
                     20852:"/cvmfs/icecube.opensciencegrid.org/data/GCD/GeoCalibDetectorStatus_AVG_55697-57531_PASS2_SPE_withStdNoise.i3.gz",
                     20881:"/cvmfs/icecube.opensciencegrid.org/data/GCD/GeoCalibDetectorStatus_AVG_55697-57531_PASS2_SPE_withStdNoise.i3.gz",
                     20891:"/cvmfs/icecube.opensciencegrid.org/data/GCD/GeoCalibDetectorStatus_AVG_55697-57531_PASS2_SPE_withStdNoise.i3.gz"
                     20904:"/cvmfs/icecube.opensciencegrid.org/data/GCD/GeoCalibDetectorStatus_AVG_55697-57531_PASS2_SPE_withStdNoise.i3.gz"
                    }

def get_data_gcd(infile):
    return glob('/'.join(infile.split('/')[:-1])+'/*GCD*')[0]

def figure_out_gcd(infile):
    if 'corsika' in infile.lower():
        corsika_set = infile.split('.')[-4]
        print(corsika_set)
        gcd_file = corsika_gcdc_dict[corsika_set]
    elif 'genie' in infile.lower():
        gcd_file = "/cvmfs/icecube.opensciencegrid.org/data/GCD/GeoCalibDetectorStatus_AVG_55697-57531_PASS2_SPE_withScaledNoise.i3.gz"
    elif 'nancy' in infile.lower():
        gcd_file = "/cvmfs/icecube.opensciencegrid.org/data/GCD/GeoCalibDetectorStatus_IC86_Merged.i3.gz"
    elif 'exp' in infile.lower():
        gcd_file = get_data_gcd(infile)
    else:
       raise ValueError('Cannot figure out what kind of infile you have')
