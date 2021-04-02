eval `/cvmfs/icecube.opensciencegrid.org/py3-v4.1.0/setup.sh`
export SOLAR_INSTALL_DIR=/data/user/jlazar/solar/

export LD_LIBRARY_PATH=$SROOT/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$SROOT/lib64:$LD_LIBRARY_PATH
export C_INCLUDE_PATH=$SROOT/include:$C_INCLUDE_PATH
export CPLUS_INCLUDE_PATH=$SROOT/include:$CPLUS_INCLUDE_PATH

export CXX=g++
export CC=gcc
export GOLEMSPACE=/data/user/jlazar/software/solar/
export GOLEMBUILDPATH=$GOLEMSPACE/local
export GOLEMSOURCEPATH=$GOLEMSPACE/sources
export PREFIX=$GOLEMBUILDPATH
export PATH=$GOLEMBUILDPATH/bin:$PATH
export LD_LIBRARY_PATH=$GOLEMBUILDPATH/lib/:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$GOLEMBUILDPATH/lib64/:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/cvmfs/icecube.opensciencegrid.org/py2-v3/Ubuntu_14.04_x86_64/lib/:$LD_LIBRARY_PATH
export C_INCLUDE_PATH=$GOLEMBUILDPATH/include/:$C_INCLUDE_PATH
export CPLUS_INCLUDE_PATH=$GOLEMBUILDPATH/include/:$CPLUS_INCLUDE_PATH
export CXX_INCLUDE_PATH=$GOLEMBUILDPATH/include/:$CPLUS_INCLUDE_PATH
export PKG_CONFIG_PATH=$GOLEMBUILDPATH/lib/pkgconfig:$GOLEMBUILDPATH/lib64/pkgconfig:$PKG_CONFIG_PATH


export PKG_CONFIG_PATH=$SROOT/lib/pkgconfig:$SROOT/include:$PKG_CONFIG_PATH
export PYTHONPATH=$GOLEMBUILDPATH/lib/python3.7/site-packages:$PYTHONPATH
export PYTHONPATH=$GOLEMBUILDPATH/lib/:$PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$SOLAR_INSTALL_DIR
export BOOST_ROOT=$SROOT
export HDF5_DISABLE_VERSION_CHECK=1
export HDF5_USE_FILE_LOCKING='FALSE'
export PLOT_DIR='/data/user/jlazar/solar/plots/'
export DATA_DIR='/data/user/jlazar/solar/data/'
/data/user/jlazar/combo37/build/env-shell.sh
