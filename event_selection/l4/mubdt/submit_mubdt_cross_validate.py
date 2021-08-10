import numpy as np
import os
import pycondor

path   = '/home/jvillarreal/condor_logs/mubdt_cross_validate/'
error  = "%s/error" % path
output = "%s/output" % path
log    = "%s/log" % path
submit = "%s/submit" % path

xlines = ["request_memory = (NumJobStarts is undefined) ? 2 * pow(2, 10) : 1024 * pow(2, NumJobStarts + 1)",
          "periodic_release = (HoldReasonCode =?= 21 && HoldReasonSubCode =?= 1001) || HoldReasonCode =?= 21",
          "periodic_remove = (JobStatus =?= 5 && (HoldReasonCode =!= 34 && HoldReasonCode =!= 21)) || (RequestMemory > 13192)"
         ]

dagman = pycondor.Dagman("mubdt_cross_validate_dag", submit=submit, verbose=2)
run    = pycondor.Job("mubdt_cross_validate", 
                      "/data/user/jvillarreal/solar_atmospherics/bdt/mubdt_cross_validate.sh",
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

lrs = np.linspace(0.1, 0.9, 5)
rgs = np.logspace(-4, 4, 5)
mlns = [30, 50, 70, 100, 1000]

for lr in lrs:
    for rg in rgs:
        for mln in mlns:
            args = '%f %f %d' % (lr, rg, mln)
            run.add_arg(args)

run.build()
