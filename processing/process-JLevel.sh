#!/bin/bash

export PYTHONPATH=$PYTHONPATH:/data/user/jlazar/.pylib
source /home/jlazar/golemsolarwimp.sh

for INPUTFILE in "$@";
do
    for INFILE in `cat $INPUTFILE`
    do
        /data/user/jlazar/combo37/build/env-shell.sh python /data/user/jlazar/solar/solar_atmospherics/processing/process-JLevel.py -i ${INFILE};
    done
done
