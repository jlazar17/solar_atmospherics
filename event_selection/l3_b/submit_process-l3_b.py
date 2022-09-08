import numpy as np
from glob import glob
import pycondor, os, subprocess, time
from optparse import OptionParser

def initialize_parser():
    parser = OptionParser()
    parser.add_option('--simname', dest='simname', type=str, default='nancy')
    parser.add_option('-n', '--njobs', dest='njobs', type=int, default=20)

    options,args = parser.parse_args()
    return options, args

options, args = initialize_parser()
simname = options.simname
njobs = options.njobs

sbase_dir = os.environ.get('SOLAR_BASE_DIR')
split_fs_prefix = f'{sbase_dir}/event_selection/l3_b/input/i3/{simname}/x'
# Find all the files that have been processed to l3_a
fs = glob(f"{sbase_dir}/event_selection/l3_a/data/{simname}/i3/*.zst")
infile = f"/data/user/jlazar//big_files/solar_atmospherics/input_{simname}_l3_b_i3.txt"
# Delete the old file which may not have all available stuff
if os.path.isfile(infile):
    os.remove(infile)
# Write all the files that are available to one file
with open(infile, "w") as inf:
    for f in fs:
        inf.write(f"{f}\n")
# Run subprocess to split them into bite-sized chunks
bash_command = f"split -l 200 {infile} {split_fs_prefix}"
process = subprocess.Popen(bash_command.split())
# Wait for the process to finish
while process.poll() is None:
    time.sleep(1)
infiles = glob(f"{split_fs_prefix}*")
print(len(infiles))

# Configure the condor job
path   = os.environ.get('CONDOR_LOGS_DIR')+"/process-l3_b/"
error  = "%s/error" % path
output = "%s/output" % path
log    = "%s/log" % path
submit = "%s/submit" % path

xlines = ["request_memory = (NumJobStarts is undefined) ? 2 * pow(2, 10) : 1024 * pow(2, NumJobStarts + 1)",
          "periodic_release = (HoldReasonCode =?= 21 && HoldReasonSubCode =?= 1001) || HoldReasonCode =?= 21",
          "periodic_remove = (JobStatus =?= 5 && (HoldReasonCode =!= 34 && HoldReasonCode =!= 21)) || (RequestMemory > 13192)"
         ]

dagman = pycondor.Dagman("process-l3_b_%s_dag" % simname, submit=submit, verbose=2)
run    = pycondor.Job("process-l3_b_%s" % simname, 
                      os.environ.get('SOLAR_BASE_DIR')+"/event_selection/l3_b/process-l3_b.sh", 
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

for i in range(njobs):
    slc = slice(i, None, njobs)
    run.add_arg(' '.join(infiles[slc]))
dagman.build()
