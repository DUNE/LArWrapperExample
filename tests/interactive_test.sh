# run an interactive test HMS 12-2-2022
export BEGIN_TIME=`date +"%d-%b-%Y %H:%M:%S %Z"`
python -m DDInterface --debug=True --dataset schellma:run5141Prod4Reco --workflowMethod=interactive --query_limit 3 --load_limit 1 -c pduneana_Prod4_data_reco2_6GeV.fcl --user $USER --appFamily=protoduneana --appName=test--appVersion=$PROTODUNEANA_VERSION  -n 2
# this does a minimal test reading n=2 events from load_limit=1 files
