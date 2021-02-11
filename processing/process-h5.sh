#!/bin/bash

export PYTHONPATH=$PYTHONPATH:/data/user/jlazar/.pylib
export PYTHONPATH=$PYTHONPATH:/data/user/jlazar/solar_atmospherics/processing/processing_modules/

for INFILE in "$@";
do
    for JFILE in `cat $INFILE`
    do
        source /home/jlazar/golemsolarwimp.sh
        /data/user/jlazar/combo37/build/env-shell.sh python /data/user/jlazar/solar_atmospherics/processing/process-h5.py -i ${JFILE} ;
        #/data/user/jlazar/combo37/build/env-shell.sh python /data/user/jlazar/solar_atmospherics/processing/process-h5.py -i ${INFILE} 2> /dev/null;
    done
done
