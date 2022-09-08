#!/bin/bash

export PYTHONPATH=$PYTHONPATH:/data/user/jlazar/.pylib
source /data/user/jlazar/solar/solar_atmospherics/env_nocombo.sh;
FLUXNAME=$1

for RUNN in "${@:2}";
do
    OUTDIR=${L3_B_SAVEDIR}/${FLUXNAME}/h5/00${RUNN}/
    INFILE_STR=${SOLAR_BASE_DIR}/event_selection/l3_b/data/exp_data/i3/Level2'*'_IC86.'????'_data_Run00${RUNN}'_Subrun*.i3.zst'
    # Make outdir if it does not exist
    [ ! -d ${OUTDIR} ] && mkdir ${OUTDIR}
    python h5writer.py --infiles ${SOLAR_BASE_DIR}/event_selection/l3_b/data/exp_data/i3/'*'${RUNN}'_Subrun*.i3.zst' --fluxname $FLUXNAME --outfile ${OUTDIR}/L3_B_IC86.data_Run00${RUNN}.h5
done
