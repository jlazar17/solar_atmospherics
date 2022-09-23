#!/bin/bash

export PYTHONPATH=$PYTHONPATH:/data/user/jlazar/.pylib
source /data/user/jlazar/solar/solar_atmospherics/env_nocombo.sh
BASEDIR=$SOLAR_BASE_DIR

INFILE=$1
OUTDIR=$2
REST=$3

CMD="/data/user/jlazar/combo37/build/env-shell.sh python ${BASEDIR}/event_selection/l3/write_h5.py -i `cat ${INFILE}` --level l3_a --outdir ${OUTDIR} ${REST}"
${CMD}
