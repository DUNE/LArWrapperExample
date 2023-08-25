"""metacat CollectionCreatorClass"""
##
# @mainpage CollectionCreatorClass
#
# @section description_main  
#
#  You can invoke this with python CollectionCreatorClass --json=<json with list of required field values>
# optional arguments are --min_time (earliest date)  --max_time (latest date)
##
# @file CollectionCreatorClass.py


from ctypes.wintypes import tagSIZE
import samweb_client
samweb = samweb_client.SAMWebClient(experiment='dune')

 
DEBUG = False

from argparse import ArgumentParser as ap
import sys
import os
import subprocess
import json

from metacat.webapi import MetaCatClient 
mc_client = MetaCatClient(os.getenv("METACAT_SERVER_URL"))

class CollectionCreatorClass:

    ## initiatization - does very little

    def __init__(self):
        self.namespace = None
        self.name = None # actual name
        self.did = None # (namespace+defname)
        self.meta = None # (list of tags)
        self.metaquery = None # metacat query
        self.samquery = None # translation of metaquery into sam language
        self.user = os.getenv("USER") # default is person running the script
        self.info = None

    
    ## set up from another script by using a dictionary or a did name  -- parallels the command line

    def load (self,dict = None, did = None, namespace = None, test = False):
        if dict == None and did == None:
            print ("no dictionary or dataset name provided - perhaps you want to use the --json or --did argument to specify on command line")
            sys.exit(1)

        self.test = test

        # this inputs a did
        if did != None:
            self.did = did
            stuff = self.did.split(":")
            if len(stuff)!=2:
                print ("did", self.did, "has invalid format")
                sys.exit(1)
            if self.namespace == None:
                print ("getting namespace from --did", stuff[0])
                self.namespace = stuff[0]
            self.name = stuff[1]
            try:
                info = mc_client.get_dataset(self.did)
            except:
                print ("failure finding information for ", self.did)
                sys.exit(1)
            
            self.info = info

            if "datasetpar.query" in info["metadata"]:
                self.metaquery = info["metadata"]["datasetpar.query"]
            else:
                    print ("could not find a query in the dataset metadata for ", self.did, info)
                    print ("this only works for datasets made with CollectionCreatorClass")
                    sys.exit(1)
        
        if dict != None:
            self.meta = dict
        
        self.make_name()
        self.make_query()
        self.make_sam_query()

    def run(self,dict = None, did = None, namespace = None, test = False):
        if self.namespace == None:
            self.namespace = self.user
        if self.did == None and self.name == None:
            print ("need to run load first to get name or did")
            sys.exit(1)
        #self.load(self,dict = None, did = None, namespace = None, test = False)
        
        if not self.test:
            
            self.makeDataset()
            self.makeSamDataset()
        

        

        
        

    ## create a name from template in json file. If none exists use a list of fields. 
    def make_name(self):

        if self.did != None:
            names = self.did.split(":")
            self.name = names[1]
            self.namespace = names[0]
            return
        
        ignore = ["description","defname","namespace","ordered"]

        if "defname" in self.meta.keys():
            template = self.meta["defname"]
            namekeys = template.split("%")
            if DEBUG: print (namekeys)
            if DEBUG: print (self.meta)
            for x in self.meta.keys():
                if x in ignore: continue
                extend = "%"+x
                if DEBUG: print ("extend",extend)
                if extend in template:
                    if self.meta[x] == None:
                        template = template.replace(x,"none")
                    else:
                        template = template.replace(extend,self.meta[x])
                    continue
                else:
                    print ("keyword ",x,"not in defname, are you sure?")
            if "%" in template:
                print ("unrecognized tag in defname",template)
            
            # for x in namekeys:
            #     if DEBUG: print (x)
            #     if x == '': continue
            #     if x in self.meta.keys():
            #         if self.meta[x] == None:
            #             template = template.replace(x,"none")
            #         else:
            #             template = template.replace(x,self.meta[x])
            #     else:
            #         print ("asked for a string in the name that is not in the definition",x)
            #         sys.exit(1)
            
            template = template.replace("%",".")
            template = template.replace(":","-") # protect against ":" for ranges
            template = template.replace(",","_") # protect against "," in lists
            if template[0] == ".": template = template[1:]
            print ("dataset name will be: ",template)
            self.name = template
        
            
            


        
        else:
            order=["core.run_type","dune.campaign","core.file_type","core.data_tier","core.data_stream","dune_mc.gen_fcl_filename","core.application.version","min_time","max_time","deftag"]
            name = ""
            for i in order:
                if i in self.meta and self.meta[i]!= None:
                    new = self.meta[i]
                    new.replace(".fcl","")
            
                    if i == "max_time":
                        new ="le"+self.meta[i]
                    if i == "min_time":
                        new ="ge"+self.metas[i]
                    if i == "deftag":
                        new = self.meta[i]
                    name += new
                    name += "__"
            name = name[:-2]
            print ("name will be",name)
            self.name = name

    ## make a metacat query from the AND of the json inputs

    def make_query(self):

        # skip if already set (generally by did)
        if self.metaquery != None:
            if DEBUG: print ("found a query",self.metaquery)
            return
        
        query = "files where"
        
        
        for item in self.meta.keys():
            if item == "Comment": continue
            if (DEBUG): print (item)
            if self.meta[item] == None:
                continue
            if "." not in item:
                continue
            val = self.meta[item]
            # put quotes around values that have "-" in them because metacat doesn't interpret "-" well
            if type(val) == str and "-" in val and not "'" in val: val = "\'%s\'"%val
 
            query += " "+item+"="+str(val)
            query += " and"
            
        # strip off the last "and"
        query = query[:-4]
        if (DEBUG): print (query)
    
        if "runs" in self.meta:
            runs = self.meta["runs"]
            if ":" not in runs:
                runs = "(%s)"%runs
            rquery = " and core.runs[any] in %s"%runs
             
            query += rquery

        # do time range - takes some work as there are two possibilities

        min = ""
        max = ""
        
        if "min_time" not in self.meta or self.meta["min_time"] == None: 
            min = None

        if "max_time" not in self.meta or self.meta["max_time"] == None: 
            max = None

        if max != None and min != None:

            if min != None:
                min = self.meta["min_time"]
                    
            if max != None:
                max = self.meta["max_time"]
                
            
            var = "created_timestamp"
            
            timequery = "" 
            
            
            if min != None: timequery += " and %s >= '%s'"%(var,min)
            if max != None: timequery += " and %s <= '%s'"%(var,max)
            query += timequery
        else:
            print ("No time range set, use all files")

        query += " ordered "

        if (DEBUG): print(query)
        self.metaquery = query
        

    ## convert a metacat query into a sam query

    def make_sam_query(self):
        
        if self.metaquery == None:
            print (" no metacat query to make sam query from")
            sys.exit(1)
        s = self.metaquery.split("where")
        if len(s) < 2:
            return None
        r = s[1]
        # convert some fields
        r = r.replace("core.","")
        r = r.replace("dune_mc.","DUNE_MC.")
        r = r.replace("dune.","DUNE.")
        r = r.replace("application.","")
        r = r.replace("runs[any] in","run_number")
        r = r.replace(":","-")
        r = r.replace("'","")
        r = r.replace("ordered", "" )
        r = r.replace("created_timestamp","create_date")
        r = r.replace("limit "," with limit ")
        r = " availability:anylocation and " + r
        # if ("skip" in r): print ("skip doesn't work yet in sam")
        # print ("samweb list-files --summary \"", r, "\"")
        
        self.samquery = r

    ## parse sys.argv and either get existing query or read json and make a new query/dataset
    def setup(self):
            parser = ap()
            
            parser.add_argument('--namespace',type=str,default=os.getenv("USER"),help="metacat namespace for dataset")
            parser.add_argument('--user', type=str, help='user name')

            parser.add_argument('--json',type=str,default=None, help='filename for a json list of parameters to and')
            parser.add_argument('--did',type=str,default=None,help="<namespace>:<name> for existing dataset to append to")
            parser.add_argument('--test',type=bool,default=False,const=True,nargs="?",help='do in test mode')
           
            XtraTags = []

            args = parser.parse_args()
            if DEBUG: print (args)

            if args.user == None and os.environ["USER"] != None:  args.user = os.environ["USER"]

            self.user = args.user

            self.namespace = args.namespace

            # check if using prexisting did - if so reuse existing query

            if args.json == None:
                if args.did == None:
                    print ("no json or did file, in future you will be able to append to a dataset directly")
                    sys.exit(1)
                else:  # yes this is pre-existing dataset
                    self.load(did=args.did,test=args.test)
                    self.run(did=args.did,test=args.test)

            else:
                # read the data description tags from json file
                if not os.path.exists(args.json):
                    print ("json file",args.json," does not exist, quitting")
                    sys.exit(1)
                f = open(args.json,'r')
                if f:
                    Tags = json.load(f)
                    self.load(dict=Tags,test=args.test)
                    self.run(dict=Tags,test=args.test)
                else:
                    print ("could not open",args.json)
                    sys.exit(1)

                
                
            #     if f:
            #         Tags = json.load(f)
            #     for x in required:
            #         if x not in Tags:
            #             print("This constraint is required for all DUNE data", x)
            #             sys.exit(1)

            #         self.did = args.did
            #         stuff = self.did.split(":")
            #         if DEBUG: print ("did",stuff)
            #         if len(stuff)!=2:
            #             print ("did", self.did, "has invalid format")
            #             sys.exit(1)
            #         if self.namespace == os.getenv("USER"):
            #             print ("getting namespace from --did", stuff[0])
            #             self.namespace = stuff[0]
            #         self.name = stuff[1]
            #         info = mc_client.get_dataset(self.did)
            #         self.info = info
            #         if DEBUG: print(json.dumps(info,indent=4))

            #         if "datasetpar.query" in info["metadata"]:
            #             if DEBUG: print ("found the query", info["metadata"]["datasetpar.query"])
            #             self.metaquery = info["metadata"]["datasetpar.query"]
            #         else:
            #                 print ("could not find a query in the dataset metadata for ", self.did, info)
            #                 print ("this only works for datasets made with CollectionCreatorClass")
            #                 sys.exit(1)

            #     self.meta = None  # tell program you did not read json file
                    
    
            # else:
            # # read the data description tags from json file
            #     if not os.path.exists(args.json):
            #         print ("json file",args.json," does not exist, quitting")
            #         sys.exit(1)
            #     f = open(args.json,'r')
            #     required = ["core.file_type", "core.run_type"]
                
            #     if f:
            #         Tags = json.load(f)
            #     for x in required:
            #         if x not in Tags:
            #             print("This constraint is required for all DUNE data", x)
            #             sys.exit(1)
            #     
            #     if DEBUG: print (Tags)
            #     self.metaquery = None  # fill in later
            #     self.meta = Tags
            #     self.did = None # tell program you got info from json
                
            # self.test = args.test      
            
    ## just a nice reformatting of results

    def printSummary(self,results):
        nfiles = total_size = 0
        for f in results:
            nfiles += 1
            total_size += f.get("size", 0)
        print("Files:       ", nfiles)
        if total_size >= 1024*1024*1024*1024:
            unit = "TB"
            n = total_size / (1024*1024*1024*1024)
        elif total_size >= 1024*1024*1024:
            unit = "GB"
            n = total_size / (1024*1024*1024)
        elif total_size >= 1024*1024:
            unit = "MB"
            n = total_size / (1024*1024)
        elif total_size >= 1024:
            unit = "KB"
            n = total_size / 1024
        else:
            unit = "B"
            n = total_size
        print("Total size:  ", "%d (%.3f %s)" % (total_size, n, unit))
    
    ## use the query from make_query to make a metacat dataset

    def makeDataset(self):
        if self.metaquery == None:
             print ("ERROR: need to run make_query or supply an input dataset first")
             sys.exit(1)


        
        # already have a dataset - just want to update it

        if self.did != None:
            if not self.test:
                print ("add files to existing dataset", self.did)
                mc_client.add_files(self.did,query=self.metaquery)
                return
            else:
                print ("this was just a test with an existing dataset")
            return
        
        # need to make dataset metadata from json input in self.meta

        cleanmeta = self.meta.copy()
        # move dataset creation flags into dataset....
        for x in self.meta.keys():
            if not "." in x: # we have some extra parameters - need to store properly
                if DEBUG: print ("rename search params that are not . type")
                if x == "description":  # this goes in the real description field so skip
                    if x in cleanmeta:cleanmeta.pop(x)
                    continue
                cleanmeta["datasetpar."+x]=self.meta[x]
                if x in cleanmeta:cleanmeta.pop(x)
            
        for x in self.meta.keys():
            if x not in cleanmeta: continue
            
            if self.meta[x] == None:
                if DEBUG: print ("remove null key",x,self.meta[x])
                if x in cleanmeta: cleanmeta.pop(x)
            else:
                cleanmeta[x] = self.meta[x]
            
        if DEBUG: print (cleanmeta)

        # store the query used to make this dataset for future reuse
        cleanmeta["datasetpar.query"] = self.metaquery

        did = "%s:%s"%(self.namespace,self.name)

        
        try:
            already = mc_client.get_dataset(did)
        except:
            print ("no dataset of this name yet")
            already = None

        print ("look for an existing dataset",did, already)

        if already == None:
                print ("make a new dataset",did)
                print ("query",self.metaquery)
            #try:
                mc_client.create_dataset(did,files_query=self.metaquery,description=self.meta["description"],metadata=cleanmeta)
                self.did = did
                self.info = mc_client.get_dataset(did)
                print ("think I made one", self.did)
                #return 1
    #        except:
    #            print("metacat dataset creation failed - does it already exist?")
        else: # already there
                info = mc_client.get_dataset(did)
                if DEBUG: print ("info",info)
                print ("add files to dataset",did)
                print ("query was",self.metaquery)
                #try:
                mc_client.add_files(did,query=self.metaquery)
                self.did = did
                #except:
                #    print("metacat dataset addition failed - does it already exist?")
        
    ## make a samweb dataset

    def makeSamDataset(self):
        # do some sam stuff
        defname=os.getenv("USER")+"_"+self.name
        print ("Try to make a sam definition:",defname)
        #print ("query",self.samquery)
        if self.samquery != None :
            try:
                samweb.createDefinition(defname,dims=self.samquery,description=self.samquery)
            except:
                print ("failed to make sam definition")
        
    


## command line, explains the variables.
if __name__ == "__main__":
   
    creator = CollectionCreatorClass()
    
    # read in command line args
    creator.setup()
    
    
    # dump out information 

    print ("\n------------------------")
    print ("\n samweb query")

    print("samweb list-files --summary \"",creator.samquery,"\"\n")
    try:
        r = samweb.listFilesSummary(creator.samquery)
    except:
        print ("SAM got here")
    print("SAM FILES",r)
    print ("\n------------------------")
    print ("\n metacat query")
    print("metacat query \"",creator.metaquery,"\"\n")
    query_files = list(mc_client.query(creator.metaquery))
    creator.printSummary(query_files)
    print ("\n ------------------------")
    print ("\n dataset metadata")
    if creator.meta: print(json.dumps({"dataset.meta":creator.meta},indent=4))
    elif creator.did: 
        print(json.dumps(creator.info,indent=4))

    print ("\n ------------------------")
    
 
