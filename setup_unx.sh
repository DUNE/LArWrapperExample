# setup for running data dispatcher tests
export DATA_DISPATCHER_URL=https://metacat.fnal.gov:9443/dune/dd/data
export DATA_DISPATCHER_AUTH_URL=https://metacat.fnal.gov:8143/auth/dune
export METACAT_SERVER_URL=https://metacat.fnal.gov:9443/dune_meta_prod/app
export METACAT_AUTH_SERVER_URL=https://metacat.fnal.gov:8143/auth/dune
#export PATH=$HOME/.local/bin/:$PATH
export HERE=$PWD
#export PYTHONPATH=$HERE/python:${PYTHONPATH}
#export SQL_QUERY_PATH=$HERE/sql
source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh
setup python v3_9_2 -z /cvmfs/larsoft.opensciencegrid.org/products

kx509
voms-proxy-init -rfc -noregen -voms=dune:/dune/Role=Analysis -valid 120:00
voms-proxy-info
export X509_USER_PROXY=/tmp/x509up_u$(id -u)  #
setup metacat
setup rucio
setup python
export MYAPP=/dune/app/users/$USER
export LWE_CODE=$PWD
export PYTHONPATH=$LWE_CODE/python:${PYTHONPATH}


