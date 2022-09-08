#!/bin/bash

export PYTHONPATH=$PYTHONPATH:/data/user/jlazar/.pylib
source /data/user/jlazar/solar/solar_atmospherics/env_nocombo.sh
BASEDIR=$SOLAR_BASE_DIR

INFILE=$1
OUTDIR=$2
THIN=$3

CMD="/data/user/jlazar/combo37/build/env-shell.sh python ${BASEDIR}/event_selection/l3_a/process-l3_a.py -i `cat ${INFILE}` --outdir ${OUTDIR} --thin ${THIN}"
${CMD}
