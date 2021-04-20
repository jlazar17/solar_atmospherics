#!/bin/bash

export PYTHONPATH=$PYTHONPATH:/data/user/jlazar/.pylib
source /data/user/jlazar/solar/solar_atmospherics/env_nocombo.sh
BASEDIR=$SOLAR_BASE_DIR


for INPUTFILE in "$@";
do
    for INFILE in `cat $INPUTFILE`
    do
      /data/user/jlazar/combo37/build/env-shell.sh python ${BASEDIR}/event_selection/l3_a/process-l3_a.py -i ${INFILE};
    done
done
