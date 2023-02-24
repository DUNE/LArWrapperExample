# submission tests
source tarme.sh  # make the tar file up-to-date
#python -m submit_dd_jobs --debug=True --dataset=schellma:run5141recentReco --query_limit=10 -c fcl/test.fcl -n 10 --njobs=1  --load_limit=2 --appFamily=LArSoft --appName=test --appVersion=${DUNESW_VERSION}
#python -m submit_dd_jobs --debug=True --dataset=schellma:EarlyPhysicsFiles2 --query_limit=10 -c eventdump.fcl -n 1 --njobs=1  --load_limit=1 --appFamily=LArSoft --appName=eventdump --appVersion=${DUNESW_VERSION} --blacklist=Swan
python -m submit_dd_jobs --debug=True --dataset=schellma:PDSP-Raw-Run5387 --query_limit=3 --query_skip=200\
 -c  protoDUNE_SP_keepup_decoder_reco_stage1.fcl  --njobs=1 -n 2 --load_limit=3 --appFamily=LArSoft --appName=reco --appVersion=${DUNESW_VERSION} #--blacklist="BNL"
