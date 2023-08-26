import sys,os,string,json
from CollectionCreatorClass import CollectionCreatorClass
import samweb_client
samweb = samweb_client.SAMWebClient(experiment='dune')
from metacat.webapi import MetaCatClient 
mc_client = MetaCatClient(os.getenv("METACAT_SERVER_URL"))

## script that loops over detectors and fcl files for fd_mc_2023a and creates datasets

if __name__ == "__main__":

    # setup
    
    creator = CollectionCreatorClass()
    experiments = ["fardet-hd","fardet-vd"]

    # make a template
    template = {
        "description":"mc files from fd_mc_2023a",
        "defnamespace":"schellma",
        "defname":"%core.file_type.%core.run_type.%dune.campaign.%core.application.version.%core.data_tier.%dune_mc.gen_fcl_filename.%deftag",
        "core.application.version": "v09_75_03d00",
        "core.data_tier": "hit-reconstructed",
        "core.file_type": "mc",
        "core.run_type": "fardet-hd",
        "dune.campaign": "fd_mc_2023a",
        "dune.requestid": "ritm1780305",
        "dune_mc.beam_polarity": "fhc",
        "dune_mc.gen_fcl_filename": "prodgenie_nutau_dune10kt_1x2x6.fcl",
        "deftag": "test11"
    }

    # list the fcl's by run_type

    # from https://wiki.dunescience.org/wiki/Production 8/25/23
    fcls = {}
    fcls["fardet-hd"] = ["prodgenie_nu_dune10kt_1x2x6.fcl",
                        "prodgenie_nutau_dune10kt_1x2x6.fcl",
                        "prodgenie_nue_dune10kt_1x2x6.fcl",
                        "prodgenie_anu_dune10kt_1x2x6.fcl",
                        "prodgenie_anutau_dune10kt_1x2x6.fcl",
                        "prodgenie_anue_dune10kt_1x2x6.fcl"]

    fcls["fardet-vd"] = ["prodgenie_nu_dunevd10kt_1x8x6_3view_30deg.fcl",
        "prodgenie_nu_numu2nue_nue2nutau_dunevd10kt_1x8x6_3view_30deg.fcl",
        "prodgenie_nu_numu2nutau_nue2numu_dunevd10kt_1x8x6_3view_30deg.fcl",
        "prodgenie_anu_dunevd10kt_1x8x6_3view_30deg.fcl",
        "prodgenie_anu_numu2nue_nue2nutau_dunevd10kt_1x8x6_3view_30deg.fcl",
        "prodgenie_anu_numu2nutau_nue2numu_dunevd10kt_1x8x6_3view_30deg.fcl"]
    # get the code versions right
    versions={}
    versions["fardet-hd"] = "v09_78_01d01"
    versions["fardet-vd"] = "v09_75_03d00"

# the version #, fcl file and polarity need to be set for each

    # this only actually makes datasets if there is a command line argument run
    test =  True
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        test = False
    
    for det in experiments:
        for fcl in fcls[det]:
            print ("\n------------------------------------------------------------------------\n")
            md = template
            md["core.run_type"] = det
            md["core.application.version"] = versions[det]
            md["dune_mc.gen_fcl_filename"] = fcl
            if "anu" in fcl:
                md["dune_mc.beam_polarity"] = "rhc"
            else:
                md["dune_mc.beam_polarity"] = "fhc"
            creator = CollectionCreatorClass()
            creator.load(md,test=test)
            #print ("name", creator.name)

            #print ("\nMETA", creator.metaquery)
            #print ("\nSAM",creator.samquery)
            r = samweb.listFilesSummary(creator.samquery)
            print ("SAM", r,"\n")
            #print("----------------------\n make metacat query \"",creator.metaquery,"\"\n")
            
            query_files = list(mc_client.query(creator.metaquery))
            creator.printSummary(query_files)
            #(json.dumps(md,indent=4))
            fname = creator.name+".json"
            f = open(fname,'w')
            json.dump(md, f,indent=4)
            f.close()
            if not test:                
                creator.run(md,test=test)
                print (json.dumps(creator.info,indent=4))
                
            
    if test:
        print ("If you don't want to test, run with arg 'run'")
