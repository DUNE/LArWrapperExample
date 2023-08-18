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

 
DEBUG = True

from argparse import ArgumentParser as ap
import sys
import os
import subprocess
import json

from metacat.webapi import MetaCatClient 

class CollectionCreatorClass:

    # make a version that takes a template instead of this list
    def make_name(self):

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
            if DEBUG:  print ("draft name",template)
            self.name = template


        
        else:
            order=["core.run_type","dune.campaign","core.file_type","core.data_tier","core.data_stream","dune_mc.gen_fcl_filename","core.application.version","min_time","max_time","skip","limit","deftag"]
            name = ""
            for i in order:
                if i in self.meta and self.meta[i]!= None:
                    new = self.meta[i]
                    new.replace(".fcl","")
                    if i == "skip":
                        new="skip%d"%self.meta[i]
                    if i == "limit":
                        new="limit%d"%self.meta[i]
                    
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

    # make a metacat query from the json inputs
    def makequery(self):
        
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
            if (DEBUG): print(query)
        # strip off the last "and"
        query = query[:-4]
        if (DEBUG): print (query)
    

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

        if self.meta["limit"] != None:
                query += " limit %s"%self.meta["limit"]
        
        if self.meta["skip"] != None:
                query += " skip %s"%self.meta["skip"]
        
        self.metaquery = query
        
    def make_sam_query(self):
        s = self.metaquery.split("where")
        if len(s) < 2:
            return None
        r = s[1]
        r = r.replace("core.","")
        r = r.replace("dune_mc.","DUNE_MC.")
        r = r.replace("dune.","DUNE.")
        r = r.replace("application.","")
    
        r = r.replace("'","")
        r = r.replace("ordered","")
        r = r.replace("created_timestamp","create_date")
        r = r.replace("limit "," with limit ")
        r = " availability:anylocation and " + r
        if ("skip" in r): print ("skip doesn't work yet in sam")
        print ("samweb list-files --summary \"", r, "\"")
        
        self.samquery = r

    def setup(self):
            parser = ap()
            
            parser.add_argument('--namespace',type=str,default=os.getenv("USER"),help="metacat namespace for dataset")

            #parser.add_argument('--min_time',type=str,help='min time range (inclusive) YYYY-MM-DD UTC')
            #parser.add_argument('--max_time',type=str,help='end time range (inclusive) YYYY-MM-DD UTC')
            
            parser.add_argument('--user', type=str, help='user name')
            parser.add_argument('--ordered',default=True,const=True,nargs="?", help='return list ordered for reproducibility')
            parser.add_argument('--limit',type=int, help='limit on # to return')
            parser.add_argument('--skip',type=int, help='skip N files')
            parser.add_argument('--json',type=str,default=None, help='filename for a json list of parameters to and')
            #parser.add_argument('--deftag',type=str,default="test",help='tag to distinguish different runs of this script, default is test')
            parser.add_argument('--summary',default=False,const=True,nargs="?", help='print a summary')
            parser.add_argument('--test',type=bool,default=False,const=True,nargs="?",help='do in test mode')
            XtraTags = ["ordered","limit","skip"]
            args = parser.parse_args()
            if DEBUG: print (args)

            if args.user == None and os.environ["USER"] != None:  args.user = os.environ["USER"]

            self.namespace = args.namespace

            if args.json == None:
                print ("no json file, in future you will be able to append to a dataset directly")
                sys.exit(1)
    
            else:
            # read the data description tags from json file
                if not os.path.exists(args.json):
                    print ("json file",args.json," does not exist, quitting")
                    sys.exit(1)
                f = open(args.json,'r')
                
                if f:
                    Tags = json.load(f)
                if DEBUG: print (Tags)
                # add the extra tags
                for tag in XtraTags:
                    if DEBUG: print (tag,XtraTags)
                    argis=tag
                    val = getattr(args,argis)
                    if DEBUG: print (tag,argis,val)
                    Tags[tag] = val
                    if DEBUG: print (tag,argis,val,type(val))
                    if type(val) == 'str' and "-" in val:
                        Tags[tag] = "\'%s\'"%(val)
            self.meta = Tags
            self.test = args.test      
            

    
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
    
    def makeDataset(self):
        if DEBUG: print ("query",self.metaquery)
        
        cleanmeta = self.meta.copy()
        # move dataset creation flags into dataset....
        for x in self.meta.keys():
            if not "." in x:
                print ("rename search params that are not . type")
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
        
        did = "%s:%s"%(self.namespace,self.name)
        test= mc_client.get_dataset(did)
        print ("look for an existing dataset",did)


        if test == None:
                print ("make a new dataset",did)
                print ("query",self.metaquery)
            #try:
                mc_client.create_dataset(did,files_query=self.metaquery,description=self.metaquery,metadata=cleanmeta)
                #return 1
    #        except:
    #            print("metacat dataset creation failed - does it already exist?")
        else: # already there
                info = mc_client.get_dataset(did)
                print ("info",info)
                print ("add files to dataset",did)
                print ("query",self.metaquery)
                #try:
                mc_client.add_files(did,query=self.metaquery)
                #except:
                #    print("metacat dataset addition failed - does it already exist?")
        
    def makeSamDataset(self):
        # do some sam stuff
        defname=os.getenv("USER")+"_"+self.name
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
    # make metacat query
    creator.makequery() 
    # make up a name
    creator.make_name()
    print ("------------------------")
    print ("list from samweb")
    # make a sam query
    creator.make_sam_query()
    
    r = samweb.listFilesSummary(creator.samquery)
    print(r)
    print ("------------------------")
    print ("list from metacat")
    print("metacat query \"",creator.metaquery,"\"\n")
    query_files = list(mc_client.query(creator.metaquery))
    creator.printSummary(query_files)
    print (creator.meta)
    print(json.dumps({"dataset.meta":creator.meta},indent=4))

    # actually make the sam definition and metacat dataset
    print ("------------------------")
    if not creator.test:
        print ("Try to make a samweb definition")
        creator.makeSamDataset()
        print ("Try to make a metacat definition")
        creator.makeDataset()
    else:
        print ("this was just a test")
 
