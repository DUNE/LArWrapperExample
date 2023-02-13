# some example metacat queries and dataset creations

metacat query "files from dune:all where namespace=np04_pdspprod2_reco and core.file_type=detector and core.run_type='protodune-sp' and \
core.data_tier=full-reconstructed and core.data_stream=physics and core.runs[any] in (5141)"

5387

metacat query "files from dune:all  where core.file_type=detector and core.run_type='protodune-sp' and \
core.data_tier=raw and core.data_stream=physics and core.runs[any] in (5387)"

metacat dataset create -f"files from dune:all  where core.file_type=detector and core.run_type='protodune-sp' and core.data_tier=raw and core.data_stream=physics and core.runs[any] in (5387)" 'schellma:PDSP-Raw-Run5387' "files from dune:all  where core.file_type=detector and core.run_type='protodune-sp' and core.data_tier=raw and core.data_stream=physics and core.runs[any] in (5387)" 

metacat dataset create -f "files from dune:all where namespace=np04_pdspprod2_reco and core.file_type=detector and core.run_type='protodune-sp' and \
core.data_tier=full-reconstructed and core.data_stream=physics and core.runs[any] in (5141)" schellma:run5141Prod2Reco "Prod2 Run 5141"

samweb list-files --summary "run_type=protodune-sp and file_type=mc and data_tier=full-reconstructed and DUNE_MC.beam_energy=1.0 and DUNE.Campaign=PDSPProd4a"

metacat query "files from dune:all where namespace='pdsp_mc_reco' and core.file_type=mc and core.data_tier='full_reconstructed' and

metacat query  "files from dune:all where namespace='pdsp_mc_reco' and core.file_type=mc and core.data_tier='full-reconstructed' and DUNE.campaign=PDSPProd4a and MC.space_charge=yes"

metacat dataset create -f "files from dune:all where namespace='pdsp_mc_reco' and core.file_type=mc and core.data_tier='full-reconstructed' and DUNE.campaign=PDSPProd4a and MC.space_charge=yes" schellma:PDSPProd4a_mc_1GeV_sce  "files from dune:all where namespace='pdsp_mc_reco' and core.file_type=mc and core.data_tier='full-reconstructed' and DUNE.campaign=PDSPProd4a and MC.space_charge=yes"

"files from dune:all with DUNE.campaign PDSPProd4a and code.data_tier 'full-reconstructed' ordered with limit 200"

metacat dataset create -f "files from dune:all where core.run_type=protodune-sp and core.data_tier=full-reconstructed and core.data_stream=physics and DUNE.campaign=PDSPProd4 and core.first_event_number < 200 " schellma:EarlyPhysicsFiles2

metacat query "files from dune:all where core.file_type=detector and core.run_type='protodune-sp' and \
core.data_tier=full-reconstructed and core.data_stream=physics and core.first_event_number < 100"

---

metacat query "files from dune:all where DUNE.campaign=PDSPProd4  and core.run_type='protodune-sp'\
 and core.data_tier='full-reconstructed' and  core.first_event_number <  1000 and core.file_type=detector"

metacat  dataset  create -f "files from dune:all where DUNE.campaign=PDSPProd4  and core.run_type='protodune-sp'and core.data_tier='full-reconstructed' and  core.first_event_number <  1000 and core.file_type=detector"   schellma:RandomPDSPData1 "files from dune:all where DUNE.campaign=PDSPProd4  and core.run_type='protodune-sp' and core.data_tier='full-reconstructed' and  core.first_event_number <  1000 and core.file_type=detector"

metacat query "files from dune:all where DUNE.campaign=PDSPProd4a  and core.run_type='protodune-sp' \
and core.data_tier='full-reconstructed' and core.first_event_number=1001 and core.file_type=mc"

metacat dataset create -f"files from dune:all where DUNE.campaign=PDSPProd4a  and core.run_type='protodune-sp' and core.data_tier='full-reconstructed' and core.first_event_number=1001 and core.file_type=mc" schellma:RandomPDSPMC1 "files from dune:all where DUNE.campaign=PDSPProd4a  and core.run_type='protodune-sp'  and core.data_tier='full-reconstructed' and core.first_event_number=1001 and core.file_type=mc"
