export DWORK=dunegpvm07.fnal.gov:/dune/data/users/schellma/LArWrapperExample
scp *.sh $DWORK
scp tests/*.sh $DWORK/tests/.
scp batch/* $DWORK/batch/.
scp python/*.py $DWORK/python/.
scp fcl/*.fcl $DWORK/fcl/.
scp sql/*.sql $DWORK/sql/.
scp datasets/*.json $DWORK/datasets/.
scp scripts/*.py $DWORK/scripts/.
