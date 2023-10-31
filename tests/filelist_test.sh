# run an interactive test HMS 12-2-2022
export BEGIN_TIME=`date +"%d-%b-%Y %H:%M:%S %Z"`
# for now, hack a file list - need to learn how to make a location list from JustIn or rucio
samweb get-file-access-url np04_raw_run005141_0006_dl8_reco1_18127108_0_20210318T104112Z_reco2_51834818_0_20211231T143125Z.root --schema=root > filelist.txt
samweb get-file-access-url np04_raw_run005141_0003_dl11_reco1_18126308_0_20210318T102237Z_reco2_51835497_0_20211231T143546Z.root --schema=root >> filelist.txt




#flist="root://fndca1.fnal.gov:1094/pnfs/fnal.gov/usr/dune/tape_backed/dunepro/protodune-sp/reco-recalibrated/2021/detector/physics/PDSPProd4/00/00/51/41/np04_raw_run005141_0006_dl8_reco1_18127108_0_20210318T104112Z_reco2_51834818_0_20211231T143125Z.root root://fndca1.fnal.gov:1094/pnfs/fnal.gov/usr/dune/tape_backed/dunepro/protodune-sp/reco-recalibrated/2021/detector/physics/PDSPProd4/00/00/51/41/np04_raw_run005141_0003_dl11_reco1_18126308_0_20210318T102237Z_reco2_51835497_0_20211231T143546Z.root"
python -m LArWrapper -n 20 --nskip=100 --debug=True  --flist="filelist.txt" --delivery_method=list --workflow_method=interactive -c pduneana_Prod4_data_reco2_6GeV.fcl  --user $USER --appFamily=protoduneana --appName=test --appVersion=$PROTODUNEANA_VERSION --dataTier=root-tuple --dataStream=physics --namespace=dune # this does a minimal test
