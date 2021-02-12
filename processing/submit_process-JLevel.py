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

path   = "/home/jlazar/condor_logs/process-JLevel"
error  = "%s/error" % path
output = "%s/output" % path
log    = "%s/log" % path
submit = "%s/submit" % path

xlines = ["request_memory = (NumJobStarts is undefined) ? 2 * pow(2, 10) : 2048 * pow(2, NumJobStarts + 1)",
          "periodic_release = (HoldReasonCode =?= 21 && HoldReasonSubCode =?= 1001) || HoldReasonCode =?= 21",
          "periodic_remove = (JobStatus =?= 5 && (HoldReasonCode =!= 34 && HoldReasonCode =!= 21)) || (RequestMemory > 13192)"
         ]


dagman = pycondor.Dagman("process-JLevel_%s_dag" % options.simname, submit=submit, verbose=2)
run    = pycondor.Job("process-JLevel_%s" % options.simname, 
                      "/data/user/jlazar/solar_atmospherics/processing/process-JLevel.sh", 
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
infiles = glob('/data/user/jlazar/solar_atmospherics/processing/data/%s/input/x*' % options.simname)
for i in range(njobs):
    slc = slice(i, None, njobs)
    run.add_arg(' '.join(infiles[slc]))
dagman.build()
