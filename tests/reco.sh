# run an interactive test HMS 12-2-2022
export BEGIN_TIME=`date +"%d-%b-%Y %H:%M:%S %Z"`
python -m DDInterface --debug=True --dataset schellma:rawPhysics_5141_5143 --workflowMethod=interactive --query_limit 1 --load_limit 1 -c protoDUNE_SP_keepup_decoder_reco_stage1.fcl --user $USER --appFamily=reconstruction --appName=reco --appVersion=$DUNERECO_VERSION  -n 2
# this does a minimal test reading n=20 events from load_limit=1 files
