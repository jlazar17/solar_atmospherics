import numpy as np
from glob import glob
import pycondor
import os
from optparse import OptionParser

def initialize_parser():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--indir",
        dest="indir",
        required=True,
        type=str
    )
    parser.add_argument(
        "--outdir",
        dest="outdir",
        default=".",
        type=str,
    )
    args = parser.parse_args()
    return args

args = initialize_parser()

path   = os.environ.get('CONDOR_LOGS_DIR')+"/write-l3_a/"
error  = "%s/error" % path
output = "%s/output" % path
log    = "%s/log" % path
submit = "%s/submit" % path

xlines = [
    "request_memory = (NumJobStarts is undefined) ? pow(2, 10) : 1024 * pow(2, NumJobStarts)",
    "periodic_release = (HoldReasonCode =?= 21 && HoldReasonSubCode =?= 1001) || HoldReasonCode =?= 21",
    "periodic_remove = (JobStatus =?= 5 && (HoldReasonCode =!= 34 && HoldReasonCode =!= 21)) || (RequestMemory > 13192)"
]

dagman = pycondor.Dagman("write_h5-l3_a_dag", submit=submit, verbose=2)
run = pycondor.Job(
    "write_h5-l3_a", 
    "/data/user/jlazar/solar/solar_atmospherics/event_selection/l3/write_h5_l3_a.sh", 
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
infiles = glob(f"{args.indir}/x*")
for infile in infiles:
    s = f"{infile} {args.outdir}"
    run.add_arg(s)
dagman.build()
