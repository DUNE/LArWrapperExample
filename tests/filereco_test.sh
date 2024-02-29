# run an interactive test HMS 12-2-2022
export BEGIN_TIME=`date +"%d-%b-%Y %H:%M:%S %Z"`
# for now, hack a file list - need to learn how to make a location list from JustIn or rucio
samweb get-file-access-url np04_raw_run005141_0006_dl8.root --schema=root | grep fnal > filelist.txt
#samweb get-file-access-url np04_raw_run005141_0003_dl11.root --schema=root >> filelist.txt

REQUEST_ID=1
JOBSUB_ID=1
now=$(date -u +"%Y-%m-%dT_%H%M%SZ")
OUTFILE="${OUTPREFIX:-duneana_ntuple}.${REQUEST_ID}"
OUTFILE="$OUTFILE.$JOBSUB_ID.${now}.root"


#flist="root://fndca1.fnal.gov:1094/pnfs/fnal.gov/usr/dune/tape_backed/dunepro/protodune-sp/reco-recalibrated/2021/detector/physics/PDSPProd4/00/00/51/41/np04_raw_run005141_0006_dl8_reco1_18127108_0_20210318T104112Z_reco2_51834818_0_20211231T143125Z.root root://fndca1.fnal.gov:1094/pnfs/fnal.gov/usr/dune/tape_backed/dunepro/protodune-sp/reco-recalibrated/2021/detector/physics/PDSPProd4/00/00/51/41/np04_raw_run005141_0003_dl11_reco1_18126308_0_20210318T102237Z_reco2_51835497_0_20211231T143546Z.root"
python -m LArWrapper -n 2 --nskip=0 --debug=True  --flist="filelist.txt"\
 --delivery_method=list --workflow_method=interactive -c protoDUNE_SP_keepup_decoder_reco_stage1.fcl\
   --user $USER --appFamily=test --appName=test --appVersion=$DUNESW_VERSION\
    --dataTier=full-reconstructed--dataStream=physics --namespace=dune --TFileName=$OUTFILE 
