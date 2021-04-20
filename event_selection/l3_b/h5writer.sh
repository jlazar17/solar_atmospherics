#!/bin/bash

export PYTHONPATH=$PYTHONPATH:/data/user/jlazar/.pylib
source /data/user/jlazar/solar/solar_atmospherics/env_nocombo.sh;

for INFILE in "$@";
do
     /data/user/jlazar/combo37/build/env-shell.sh python $SOLAR_INSTALL_DIR/solar_atmospherics/event_selection/l3_b/h5writer.py -i ${INFILE};
done
