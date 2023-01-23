#!/bin/bash

export PYTHONPATH=$PYTHONPATH:/data/user/jlazar/.pylib
source /data/user/jlazar/solar/solar_atmospherics/env_nocombo.sh  


echo "step1"
#/data/user/jlazar/solar/solar_atmospherics/env.sh python /data/user/jlazar/solar/solar_common/sunnify/sunnify.py -f $1 -m $2 -j $3;
/data/user/jlazar/combo37/build/env-shell.sh python /data/user/jlazar/solar/solar_atmospherics/modules/merge-h5/merge-h5.py --level $1 --simname $2 --jump $3;
