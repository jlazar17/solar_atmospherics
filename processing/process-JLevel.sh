#!/bin/bash

export PYTHONPATH=$PYTHONPATH:/data/user/jlazar/.pylib

for INPUTFILE in "$@";
do
    for INFILE in `cat $INPUTFILE`
    do
        /data/ana/SterileNeutrino/IC86/HighEnergy/MC/Metaprojects/icerec.XLevel/build/icerec.XLevel.RHEL_6_x86_64/env-shell.sh python /data/user/jlazar/solar_atmospherics/processing/process-JLevel.py -i ${INFILE} 2> /dev/null;
    done
done
