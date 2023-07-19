# submission tests
source tarme.sh  # make the tar file up-to-date
# run a test with more jobs than files to deliver
python -m submit_dd_jobs --debug=True --dataset=schellma:EarlyPhysicsFiles2 --query_limit=50 --query_skip=200\
 -c  fcl/test.fcl --njobs=50 -n 10 --load_limit=1 --appFamily=LArSoft --appName=test --appVersion=${DUNESW_VERSION} #--blacklist="BNL"
