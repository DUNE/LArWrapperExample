# setup for running metacat and data dispatcher tests
# assumes you have already done: 
#source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh
export DATA_DISPATCHER_URL=https://metacat.fnal.gov:9443/dune/dd/data
export DATA_DISPATCHER_AUTH_URL=https://metacat.fnal.gov:8143/auth/dune
export METACAT_SERVER_URL=https://metacat.fnal.gov:9443/dune_meta_prod/app
export METACAT_AUTH_SERVER_URL=https://metacat.fnal.gov:8143/auth/dune
#export PATH=$HOME/.local/bin/:$PATH
export HERE=$PWD
export PYTHONPATH=$HERE/python:$HERE/scripts:${PYTHONPATH}
export SQL_QUERY_PATH=$HERE/sql
ksu dunepro
setup metacat
. $HOME/mcruciosam/profile.sh
# get some credentials
# kx509
# voms-proxy-init -rfc -noregen -voms=dune:/dune/Role=Analysis -valid 120:00
# voms-proxy-info
# export X509_USER_PROXY=/tmp/x509up_u$(id -u)  #
# metacat auth login -m x509 schellma
# metacat auth whoami
