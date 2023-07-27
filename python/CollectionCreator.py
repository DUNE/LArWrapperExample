"""metacat query_creator"""
##
# @mainpage queryCreator
#
# @section description_main  
#
#  You can invoke this with python CollectionCreator --json=<json with list of required field values>
# optional arguments are --min_time (earliest date)  --max_time (latest date)
##
# @file queryCreator.py

import samweb_client
samweb = samweb_client.SAMWebClient(experiment='dune')

 
DEBUG = False

from argparse import ArgumentParser as ap
import sys
import os
import subprocess
import json
from  collectionTags import *



#rom datetime import date,timezone,datetime
#from dateutil import parser as dp
from metacat.webapi import MetaCatClient 



def jsonwrite(path,j):
      g = open(path,'w')
      s = json.dumps(j,indent=2)
      g.write(s)
    
def make_name(tags):
    order=["core.run_type","dune.campaign","core.file_type","core.data_tier","core.data_stream","dune_mc.gen_fcl_filename","core.application.version","min_time","max_time","skip","limit"]
    name = ""
    for i in order:
         if i in tags and tags[i]!= None:
            new = tags[i]
            if i == "skip":
                new="skip%d"%tags[i]
            if i == "limit":
                new="limit%d"%tags[i]
            
            if i == "max_time":
                new ="le"+tags[i]
            if i == "min_time":
                new ="ge"+tags[i]
            name += new
            name += "_"
    name = name[:-1]
    print ("name might be",name)
    return name


def makequery(meta):
    
    query = "files where"
    
     
    for item in meta.keys():
        if item == "Comment": continue
        if (DEBUG): print (item)
        if meta[item] == None:
            continue
        if "." not in item:
            continue
        val = meta[item]
        if type(val) == str and "-" in val and not "'" in val: val = "\'%s\'"%val
        
        query += " "+item+"="+str(val)
        query += " and"
        if (DEBUG): print(query)
    query = query[:-4]
    if (DEBUG): print (query)
    

# do time range - takes some work as there are two possibilities
    if meta["min_time"] != None or meta["max_time"] != None:
        min = None
        max = None
        if meta["min_time"] != None:
            min = meta["min_time"]
            
        if meta["max_time"] != None:
            max = meta["max_time"]
        
        if "created" in meta["time_var"]:
             var = "created_timestamp"
        elif "raw" in meta["time_var"]:
             var = "core.start_time"
        else:
             print (" undercognized time_var")
             sys.exit(1)

        timequery = "" 
        if var != "created_timestamp":
            if min != None: timequery += " and %s >= datetime('%s')"%(var,min)
            if max != None: timequery += " and %s <= datetime('%s')"%(var,max)
        else:
            if min != None: timequery += " and %s >= '%s'"%(var,min)
            if max != None: timequery += " and %s <= '%s'"%(var,max)
        query += timequery
    else:
        print ("No time range set, use all files")

    if meta["ordered"]: query += " ordered "

    

    if meta["limit"] != None:
            query += " limit %s"%meta["limit"]
    
    if meta["skip"] != None:
            query += " skip %s"%meta["skip"]
      
    return query
    
def make_sam_query(query):
    s = query.split("where")
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
    
    return r

def setup():
        parser = ap()
         
        parser.add_argument('--namespace',type=str,default=os.getenv("USER"),help="metacat namespace for dataset")
        parser.add_argument('--time_var',type=str,default="created",help="creation time to select ['created'] or 'raw']")
        parser.add_argument('--min_time',type=str,help='min time range (inclusive) YYYY-MM-DD UTC')
        parser.add_argument('--max_time',type=str,help='end time range (inclusive) YYYY-MM-DD UTC')
        parser.add_argument('--file_type',type=str, help='["detector","mc"]')
        parser.add_argument('--run_type',type=str, help='run_type, example="prododune-sp"')
        parser.add_argument('--campaign',type=str, help='DUNE Campaign')
        parser.add_argument('--family',type=str, help='Application Family')
        parser.add_argument('--name', type=str, help='Application Name')
        parser.add_argument('--version', type=str, help='Application Version')
        parser.add_argument('--data_tier', type=str, help='data tier')
        parser.add_argument('--data_stream', type=str, help='data stream for output file if only one')
        #parser.add_argument('--input_dataset',default='dune:all',type=str,help='parent dataset, default=[\"dune:all\"]')
        parser.add_argument('--user', type=str, help='user name')
        parser.add_argument('--ordered',default=True,const=True,nargs="?", help='return list ordered for reproducibility')
        parser.add_argument('--limit',type=int, help='limit on # to return')
        parser.add_argument('--skip',type=int, help='skip N files')
        #parser.add_argument('--other',type=str,help='other selections, for example, --other=\"detector.hv_value=180 and beam.momentum=1 ')
        parser.add_argument('--json',type=str, help='filename for a json list of parameters to and')
        #parser.add_argument('--summary',default=False,const=True,nargs="?", help='print a summary')
        parser.add_argument('--test',type=bool,default=False,const=True,nargs="?",help='do in test mode')
        XtraTags = ["min_time","max_time","ordered","limit","skip","time_var"]
        args = parser.parse_args()
        
        
    

        if DEBUG: print (args)

        required1 = ["file_type","run_type"]
        required2 = ["json"]

        ok = False
        if "file_type" in args and "run_type" in args:
             ok = True
        elif "json" in args:
             ok = True
        if not ok:  
             print ("must have either json or both file_type and run_type arguments")
             sys.exit(1)

        #metafield = makemetafields()
  
        if args.user == None and os.environ["USER"] != None:  args.user = os.environ["USER"]

        
        if args.json == None:
            Tags = DefineCollectionTags()
            map = CollectionArgMap(Tags)
            for tag in Tags:
                argis=map[tag]
                val = getattr(args,argis)
                if DEBUG: print (tag,argis,val)
                Tags[tag] = val
                if DEBUG: print (tag,argis,val,type(val))
                #if type(val) == 'str' and "-" in val:
                #Tags[tag] = "\'%s\'"%(val)
        else:
        # read the data description tags from json file
            if not os.path.exists(args.json):
                print (args.json," does not exist, quitting")
                sys.exit(0)
            f = open(args.json,'r')
            
            if f:
                Tags = json.load(f)
            # protect special characters
#            for tag in Tags.keys():
#                if "-" in Tags[tag]:
#                    Tags[tag] = "\'%s\'"%(Tags[tag])
#
            if DEBUG: print (Tags)
            # add the extra tags
            for tag in XtraTags:
                argis=tag
                val = getattr(args,argis)
                if DEBUG: print (tag,argis,val)
                Tags[tag] = val
                if DEBUG: print (tag,argis,val,type(val))
                if type(val) == 'str' and "-" in val:
                    Tags[tag] = "\'%s\'"%(val)
                    
        return Tags,args.test

def writequery(q,fname):
    g = open(fname+".txt",'w')
    g.write(q)
    g.close()
    
def printSummary(results):
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
    
def makeDataset(query,name,meta):
    cleanmeta = meta["dataset.meta"].copy()
    for x in meta["dataset.meta"].keys():
        print (x,meta["dataset.meta"][x])
        
        if meta["dataset.meta"][x] == None:
            print ("remove null key",x,meta["dataset.meta"][x])
            cleanmeta.pop(x)
    print (cleanmeta)
    did = "%s:%s"%(os.getenv("USER"),name)
    test= mc_client.get_dataset(did)
    print ("look for a dataset",did)
    if test == None:
        print ("make a new dataset",did)
        try:
            mc_client.create_dataset(did,files_query=query,description=query,metadata={"dataset.meta":cleanmeta})
            return 1
        except:
            print("metacat dataset creation failed - does it already exist?")
    else:
        print ("add files to dataset",did)
        try:
            mc_client.add_files(did,query=query)
        except:
            print("metacat dataset addition failed - does it already exist?")
    
def makeSamDataset(query,thename):
    # do some sam stuff
    defname=os.getenv("USER")+"_"+thename
    print ("Try to make a sam definition:",defname)
    #x = samweb.listFilesSummary(samquery)
    #print (x)
    if samquery != None :
        try:
            samweb.createDefinition(defname,dims=samquery,description=samquery)
        except:
            print ("failed to make sam definition")
    
    


## command line, explains the variables.
if __name__ == "__main__":
    mc_client = MetaCatClient('https://metacat.fnal.gov:9443/dune_meta_prod/app')
    Tags,test = setup()
    thequery = makequery(Tags)
    
    
    
    thename = make_name(Tags)
    print ("------------------------")
    print ("list from samweb")
    samquery = make_sam_query(thequery)
    r = samweb.listFilesSummary(samquery)
    print(r)
    print ("------------------------")
    print ("list from metacat")
    print("metacat query \"",thequery,"\"\n")
    query_files = list(mc_client.query(thequery))
    printSummary(query_files)
    print(json.dumps({"dataset.meta":Tags},indent=4))
    print ("------------------------")
    if not test:
        print ("Try to make a samweb definition")
        makeSamDataset(samquery,thename)
        print ("Try to make a metacat definition")
        makeDataset(thequery,thename,{"dataset.meta":Tags})
    else:
        print ("this was just a test")
    
#    # do some sam stuff
#    defname=os.getenv("USER")+"_"+thename
#    print ("Try to make a sam definition:",defname)
#    x = samweb.listFilesSummary(samquery)
#    print (x)
#    if samquery != None :
#        try:
#            samweb.createDefinition(defname,dims=samquery,description=samquery)
#        except:
#            print ("failed to make sam definition")
            
   
    
    query_files = list(mc_client.query(thequery))
    summary = True
    if summary: 
         printSummary(query_files)
    else:
        for l in query_files:
         
            print("%s:%s"%(l["namespace"],l["name"]))
