#!/bin/bash

export PYTHONPATH=$PYTHONPATH:/data/user/jlazar/.pylib
export PYTHONPATH=$PYTHONPATH:/data/user/jlazar/solar/solar_atmospherics/processing/processing_modules/
export PYTHONPATH=$PYTHONPATH:/data/user/jlazar/solar/
source /home/jlazar/golemsolarwimp.sh

for INFILE in "$@";
do
    for JFILE in `cat $INFILE`
    do
        /data/user/jlazar/combo37/build/env-shell.sh python /data/user/jlazar/solar/solar_atmospherics/processing/process-h5.py -i ${JFILE} ;
    done
done
