"""metacat MetaFixer"""
##
# @mainpage MetaFixer
#
# @section description_main
#
#  
# @file MetaFixer.py

# pylint: disable=C0303
# pylint: disable=C0321 
# pylint: disable=C0301  
# pylint: disable=C0209
# pylint: disable=C0103 
# pylint: disable=C0325 
# pylint: disable=C0123



from argparse import ArgumentParser as ap

import sys
import os
import json

import samweb_client

from metacat.webapi import MetaCatClient
samweb = samweb_client.SAMWebClient(experiment='dune')

DEBUG = False

mc_client = MetaCatClient(os.getenv("METACAT_SERVER_URL"))


class MetaFixer:
    ''' Class to create data collections'''

    def __init__(self,verbose=False):
        ''' 
        __init__ initialization, does very little

        :param verbose: print out a lot of things

        '''
        self.query_files=None
        self.verbose = verbose
        self.fix=None
        self.limit=1000000
        self.skip=0

    
    

    def getInput(self,query=None,limit=10000000,skip=0):
        ''' 
        get a query and return a list of did's
        '''
        self.skip = skip
        self.limit = limit
        thequery = query + " skip %d limit %d "%(self.skip,self.limit)

        if self.verbose: print ("thequery:",thequery)
        try:
            self.query_files = list(mc_client.query(thequery))
            print ("getinput returned:",len(self.query_files), "files") 
        except:
            print("metacat query ", thequery, " failed")
            sys.exit(0)
        
        return self.query_files
    
    def explore(self):
        " see what there is in a general query "
        if not os.path.exists("metadata"):
            os.mkdir("metadata")
        " this explores and counts things"
        datatypes = ["core.data_tier","core.run_type","dune.campaign","dune_mc.gen_fcl_filename","core.application","dune.requestid"]
        typecount = {}
        for datatype in datatypes:
            typecount[datatype]={}
        typecount["namespace"]={}
        count = self.skip
        for file in self.query_files :
            count += 1
            #if self.verbose:print (file)
            thedid = "%s:%s"%(file["namespace"],file["name"])

            if count%10 == 0 and self.verbose:
                print (count, thedid)
            try:
                md = mc_client.get_file(did=thedid,with_metadata=True,with_provenance=True)
            except:
                print ("failed at file",count,did)
                break
            self.checker(md,"parentage")
            # if self.verbose:
            #     print(json.dumps(md,indent=4))
            # count namespaces
            value = file["namespace"]
            if value in typecount["namespace"]:
                typecount["namespace"][value] +=1
            else:
                typecount["namespace"][value]=1
                f = open("metadata/namepace.json",'w')
                data = json.dumps(md,indent=4)
                
                f.write(data)
                f.close()
                
                    
            #
            metadata = md["metadata"]
            for datatype in datatypes:
                if datatype in metadata.keys():
                    value = metadata[datatype]
                    if value in typecount[datatype]:
                        typecount[datatype][value] = typecount[datatype][value]+1
                    else:
                        typecount[datatype][value] = 1
        
                        f = open("metadata/"+datatype+"__"+value+".json",'w')
                        data = json.dumps(md,indent=4)
                        f.write(data)
                        f.close()
            
        print(json.dumps(typecount,indent=4))

    def checker(self, filemd=None,check="parentage"):
        ' check various aspects of the file '
        if check == "parentage":
            if "parents" in filemd and len(filemd["parents"])> 0:
                # has some parentage, look at it. 
                parents = filemd["parents"]
                if self.verbose:
                    print ("parents",parents)
                    for p in parents:
                        parentmd = mc_client.get_file(fid=p["fid"])
                        print(parentmd["namespace"],parentmd["name"],jsondump(p))
            else:
                metadata = filemd["metadata"]
                if "core.parents" in metadata:
                    print ("core.parents", metadata["core.parents"])
                    for p in metadata["core.parents"]:
                        if ":" in p["file_name"]:
                            print ("ok)")
                        else:
                            print ("ERROR missing namespace for parent in  this file",filemd["namespace"],filemd["name"])
                    
                else:
                    print ("neither parents or core.parents for ", filemd["namespace"],filemd["name"])
                            
def jsondump(dict):
        return json.dumps(dict,indent=4)                   

def parentchecker(query):
        newquery = " %s - children ( parents ( %s ))"% (query,query)
        return newquery



                    
                

for workflow in [1633,1638]:     

    testquery =  "files from dune:all where dune.workflow['workflow_id'] in (%d) "%(workflow)

    p =  (parentchecker(testquery))



    fixer=MetaFixer(verbose=True)
    thelist = fixer.getInput(query=testquery,limit=20,skip=0)

    fixer.explore()
