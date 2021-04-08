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

path   = "/home/jvillarreal/condor_logs/process-l3_b/"
error  = "%s/error" % path
output = "%s/output" % path
log    = "%s/log" % path
submit = "%s/submit" % path

xlines = ["request_memory = (NumJobStarts is undefined) ? 2 * pow(2, 10) : 1024 * pow(2, NumJobStarts + 1)",
          "periodic_release = (HoldReasonCode =?= 21 && HoldReasonSubCode =?= 1001) || HoldReasonCode =?= 21",
          "periodic_remove = (JobStatus =?= 5 && (HoldReasonCode =!= 34 && HoldReasonCode =!= 21)) || (RequestMemory > 13192)"
         ]

dagman = pycondor.Dagman("process-l3_b_%s dag" % options.simname, submit=submit, verbose=2)
run    = pycondor.Job("process-l3_b_%s" % options.simname, 
                      "/data/user/jvillarreal/sa_git/solar_atmospherics/event_selection/l3_b/process-l3_b.sh", 
                      error=error, 
                      output=output, 
                      log=log, 
                      submit=submit, 
                      universe="vanilla", 
                      notification="never",
                      dag=dagman,
                      verbose=2,
		      extra_lines=xlines
                     )

njobs = options.njobs
infiles = glob('/data/user/jlazar/solar/solar_atmospherics/event_selection/l3_b/input/i3/%s/x*' % options.simname)
for i in range(njobs):
    slc = slice(i, None, njobs)
    run.add_arg(' '.join(infiles[slc]))
dagman.build()
