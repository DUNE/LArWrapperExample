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

class CollectionCreatorClass:

    ## create a name from template in json file. If none exists use a list of fields. 
    def make_name(self):

        if self.did != None:
            names = self.did.split(":")
            self.defname = names[1]
            self.namespace = names[0]
            return

        if "defname" in self.meta.keys():
            template = self.meta["defname"]
            namekeys = template.split("%")
            if DEBUG: print (namekeys)
            if DEBUG: print (self.meta)
            for x in namekeys:
                if DEBUG: print (x)
                if x == '': continue
                if x in self.meta.keys():
                    if self.meta[x] == None:
                        template = template.replace(x,"none")
                    else:
                        template = template.replace(x,self.meta[x])
                else:
                    print ("asked for a string in the name that is not in the definition",x)
                    sys.exit(1)
            
            template = template.replace("%",".")
            template = template.replace(":","-") # protect against ":" for ranges
            if template[0] == ".": template = template[1:]
            if DEBUG:  print ("draft name",template)
            self.defname = template


        
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
            self.defname = name

    ## make a metacat query from the AND of the json inputs

    def makequery(self):

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

        if self.meta["ordered"]: query += " ordered "

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
        r = r.replace("ordered","")
        r = r.replace("created_timestamp","create_date")
        r = r.replace("limit "," with limit ")
        r = " availability:anylocation and " + r
        # if ("skip" in r): print ("skip doesn't work yet in sam")
        print ("samweb list-files --summary \"", r, "\"")
        
        self.samquery = r

    ## parse sys.argv and either get existing query or read json and make a new query/dataset
    def setup(self):
            parser = ap()
            
            parser.add_argument('--namespace',type=str,default=os.getenv("USER"),help="metacat namespace for dataset")
            parser.add_argument('--user', type=str, help='user name')
            parser.add_argument('--ordered',default=True,const=True,nargs="?", help='return list ordered for reproducibility')
            parser.add_argument('--json',type=str,default=None, help='filename for a json list of parameters to and')
            parser.add_argument('--did',type=str,default=None,help="<namespace>:<name> for existing dataset to append to")
            parser.add_argument('--test',type=bool,default=False,const=True,nargs="?",help='do in test mode')
            XtraTags = []

            args = parser.parse_args()
            if DEBUG: print (args)

            if args.user == None and os.environ["USER"] != None:  args.user = os.environ["USER"]

            self.namespace = args.namespace

            # check if using prexisting did - if so reuse existing query

            if args.json == None:
                if args.did == None:
                    print ("no json or did file, in future you will be able to append to a dataset directly")
                    sys.exit(1)
                else:  # yes this is pre-existing dataset
                    self.did = args.did
                    stuff = self.did.split(":")
                    if DEBUG: print ("did",stuff)
                    if len(stuff)!=2:
                        print ("did", self.did, "has invalid format")
                        sys.exit(1)
                    if self.namespace == os.getenv("USER"):
                        print ("getting namespace from --did", stuff[0])
                        self.namespace = stuff[0]
                    self.defname = stuff[1]
                    info = mc_client.get_dataset(self.did)
                    self.info = info
                    if DEBUG: print(json.dumps(info,indent=4))

                    if "datasetpar.query" in info["metadata"]:
                        if DEBUG: print ("found the query", info["metadata"]["datasetpar.query"])
                        self.metaquery = info["metadata"]["datasetpar.query"]
                    else:
                            print ("could not find a query in the dataset metadata for ", self.did, info)
                            print ("this only works for datasets made with CollectionCreatorClass")
                            sys.exit(1)

                self.meta = None  # tell program you did not read json file
                    
    
            else:
            # read the data description tags from json file
                if not os.path.exists(args.json):
                    print ("json file",args.json," does not exist, quitting")
                    sys.exit(1)
                f = open(args.json,'r')
                required = ["core.file_type", "core.run_type"]
                
                if f:
                    Tags = json.load(f)
                for x in required:
                    if x not in Tags:
                        print("This constraint is required for all DUNE data", x)
                        sys.exit(1)
                if args.ordered:
                    Tags["ordered"]=True
                else:
                    Tags["ordered"]=False
                if DEBUG: print (Tags)
                self.metaquery = None  # fill in later
                self.meta = Tags
                self.did = None # tell program you got info from json
                
            self.test = args.test      
            
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
    
    ## use the query from makequery to make a metacat dataset

    def makeDataset(self):
        if self.metaquery == None:
             print ("ERROR: need to run make_query or supply an input dataset first")
             sys.exit(1)

        if DEBUG: print ("query",self.metaquery)
        
        # already have a dataset - just want to update it

        if self.did != None:
            if not self.test:
                print ("add files to existing dataset", self.did)
                mc_client.add_files(self.did,query=self.metaquery)
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

        did = "%s:%s"%(self.namespace,self.defname)
        
        test= mc_client.get_dataset(did)

        print ("look for an existing dataset",did)

        if test == None:
                print ("make a new dataset",did)
                print ("query",self.metaquery)
            #try:
                mc_client.create_dataset(did,files_query=self.metaquery,description=self.meta["description"],metadata=cleanmeta)
                self.did = did
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
        defname=os.getenv("USER")+"_"+self.defname
        print ("Try to make a sam definition:",defname)
        print ("query",self.samquery)
        if self.samquery != None :
            try:
                samweb.createDefinition(defname,dims=self.samquery,description=self.samquery)
            except:
                print ("failed to make sam definition")
        
    


## command line, explains the variables.
if __name__ == "__main__":
    mc_client = MetaCatClient(os.getenv("METACAT_SERVER_URL"))
    creator = CollectionCreatorClass()
    
    # read in command line args
    creator.setup()
    
    creator.make_name()
    # make metacat query
    creator.makequery() 
    
    print ("\n------------------------")
    print ("samweb query")
    # make a sam query
    creator.make_sam_query()
   # print("samweb list-files --summary \"",creator.samquery,"\"\n")
    r = samweb.listFilesSummary(creator.samquery)
    print(r)
    print ("\n------------------------")
    print ("metacat query")
    print("metacat query \"",creator.metaquery,"\"\n")
    query_files = list(mc_client.query(creator.metaquery))
    creator.printSummary(query_files)
    print ("\n dataset metadata")
    if creator.meta: print(json.dumps({"dataset.meta":creator.meta},indent=4))
    if creator.did: 
        print(json.dumps(creator.info,indent=4))

    # actually make the sam definition and metacat dataset
    print ("\n ------------------------")
    if not creator.test:
        print ("Try to make a samweb definition")
        creator.makeSamDataset()
        print ("Try to make a metacat definition")
        creator.makeDataset()
        #print ("creator.did",creator.did)
        info = mc_client.get_dataset(creator.did)
        print(json.dumps(info,indent=4))

    else:
        print ("this was just a test")
 
