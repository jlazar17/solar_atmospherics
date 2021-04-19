import numpy as np
from glob import glob
import pycondor
import os
from optparse import OptionParser

def initialize_parser():
    parser = OptionParser()
    parser.add_option('--simname', dest='simname', type=str, default='all')
    parser.add_option("-o", "--outfile", dest="outfile", type=str, default='')
    parser.add_option('-n', '--njobs', dest='njobs', type=int, default=20)

    options,args = parser.parse_args()
    return options, args

options, args = initialize_parser()

path   = os.environ.get('CONDOR_LOGS_DIR')+"/process-l3_a/"
print(path)
error  = "%s/error" % path
output = "%s/output" % path
log    = "%s/log" % path
submit = "%s/submit" % path

xlines = ["request_memory = (NumJobStarts is undefined) ? 2 * pow(2, 10) : 1024 * pow(2, NumJobStarts + 1)",
          "periodic_release = (HoldReasonCode =?= 21 && HoldReasonSubCode =?= 1001) || HoldReasonCode =?= 21",
          "periodic_remove = (JobStatus =?= 5 && (HoldReasonCode =!= 34 && HoldReasonCode =!= 21)) || (RequestMemory > 13192)"
         ]

dagman = pycondor.Dagman("process-l3_a_%s_dag" % options.simname, submit=submit, verbose=2)
run    = pycondor.Job("process-l3_a_%s" % options.simname, 
                      "/data/user/jvillarreal/sa_git/solar_atmospherics/event_selection/l3_a/process-l3_a.sh", 
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
infiles = glob('%s/event_selection/l3_a/input/i3/%s/x*' % (os.environ.get('SOLAR_BASE_DIR'), options.simname))
if options.simname=='data':
    infiles = infiles[::10] # Only run on 10% of the data
for i in range(njobs):
    slc = slice(i, None, njobs)
    run.add_arg(' '.join(infiles[slc]))
dagman.build()
