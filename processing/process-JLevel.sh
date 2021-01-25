#!/bin/bash

for INFILE in "$@";
do
    echo $INFILE
    /data/ana/SterileNeutrino/IC86/HighEnergy/MC/Metaprojects/icerec.XLevel/build/icerec.XLevel.RHEL_6_x86_64/env-shell.sh python /data/user/jlazar/solar_atmospherics/processing/process-JLevel.py -i $INFILE;
done
