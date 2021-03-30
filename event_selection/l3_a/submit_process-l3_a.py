import numpy as np
from glob import glob
import pycondor
import os
from optparse import OptionParser

def initialize_parser():
    parser = OptionParser()
    parser.add_option('--simname', dest='simname', type=str, default='nancy')
    #parser.add_option("-i", "--indir",
    #                  dest="indir",
    #                  type=str,
    #                  default = '/data/sim/IceCube/2016/filtered/level2/neutrino-generator/nancy001/NuMu/medium_energy/hole_ice/p1=0.3_p2=0.0/2/'
    #                 )
    parser.add_option("-o", "--outfile", dest="outfile", type=str, default='')
    parser.add_option('-n', '--njobs', dest='njobs', type=int, default=20)

    options,args = parser.parse_args()
    return options, args

options, args = initialize_parser()

path   = "/home/jvillarreal/condor_logs/process-l3_a/"
error  = "%s/error" % path
output = "%s/output" % path
log    = "%s/log" % path
submit = "%s/submit" % path

dagman = pycondor.Dagman("process-l3_a_dag", submit=submit, verbose=2)
run    = pycondor.Job("process-l3_a", 
                      "/data/user/jvillarreal/solar_atmospherics/event_selection/l3_a/process-l3_a.sh", 
                      error=error, 
                      output=output, 
                      log=log, 
                      submit=submit, 
                      universe="vanilla", 
                      notification="never",
                      dag=dagman,
                      verbose=2,
                     )

njobs = options.njobs
infiles = glob('/data/user/jvillarreal/solar_atmospherics/event_selection/l3_a/input/%s/x*' options.simname)
if options.simname==data:
    infiles = infiles[::10] # Only run on 10% of the data
for i in range(njobs):
    slc = slice(i, None, njobs)
    run.add_arg(' '.join(infiles[slc]))
dagman.build()
