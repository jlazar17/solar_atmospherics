#!/bin/bash

export PYTHONPATH=$PYTHONPATH:/data/user/jlazar/.pylib
source /home/jlazar/golemsolarwimp.sh
BASEDIR=/data/user/jvillareal/

for INPUTFILE in "$@";
do
    for INFILE in `cat $INPUTFILE`
    do
        /data/user/jlazar/combo37/build/env-shell.sh python ${BASEDIR}/solar_atmospherics/event_selection/l3_a/process-l3_a.py -i ${INFILE};
    done
done
