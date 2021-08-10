#!/bin/bash

eval `/cvmfs/icecube.opensciencegrid.org/py3-v4.1.0/setup.sh`

LEARNINGRATE=$1
REGULARIZATION=$2
MAXLEAFNODES=$3

python /data/user/jvillarreal/solar_atmospherics/bdt/mubdt_cross_validate.py -l ${LEARNINGRATE} -r ${REGULARIZATION} -m ${MAXLEAFNODES}
