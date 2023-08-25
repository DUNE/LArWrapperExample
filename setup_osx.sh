export DWORK=dunegpvm11.fnal.gov:/dune/data/users/schellma/LArWrapperExample
export DDTEST=dunegpvm11.fnal.gov:/pnfs/dune/scratch/users/$USER/ddtest
export HERE=$HOME/Dropbox/LArWrapperExample
export PATH=${HOME}/.local/bin:$PATH
export SQL_QUERY_PATH=${HERE}/sql
export PYTHONPATH=$HERE/python:${PYTHONPATH}

export DATA_DISPATCHER_URL=https://metacat.fnal.gov:9443/dune/dd/data
export DATA_DISPATCHER_AUTH_URL=https://metacat.fnal.gov:8143/auth/dune
export METACAT_SERVER_URL=https://metacat.fnal.gov:9443/dune_meta_prod/app
export METACAT_AUTH_SERVER_URL=https://metacat.fnal.gov:8143/auth/dune
source $HOME/setup_samweb.sh
