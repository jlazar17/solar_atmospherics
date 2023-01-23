#!/bin/bash

export PYTHONPATH=$PYTHONPATH:/data/user/imartinez-soler/.pylib
source /data/user/imartinez-soler/solar/solar_atmospherics/env_nocombo.sh
BASEDIR=$SOLAR_BASE_DIR

INFILE=$1
OUTDIR=$2
THIN=$3

CMD="/data/user/imartinez-soler/combo37/build/env-shell.sh python ${BASEDIR}/event_selection/l3_a/process-l3_a.py -i `cat ${INFILE}` --outdir ${OUTDIR} --thin ${THIN}"
${CMD}
