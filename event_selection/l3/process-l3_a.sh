#!/bin/bash

export PYTHONPATH=$PYTHONPATH:/data/user/jlazar/.pylib
source /data/user/jlazar/solar/solar_atmospherics/env_nocombo.sh
BASEDIR=$SOLAR_BASE_DIR

INFILE=$1
OUTDIR=$2
THIN=$3
REST=$4

CMD="/data/user/jlazar/combo37/build/env-shell.sh python ${BASEDIR}/event_selection/l3/process-l3.py -i `cat ${INFILE}` --outdir ${OUTDIR} --thin ${THIN} ${REST} --l3_a"
${CMD}
