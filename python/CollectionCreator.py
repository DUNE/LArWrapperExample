"""metacat query_creator"""
##
# @mainpage queryCreator
#
# @section description_main  
#
##
# @file queryCreator.py



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
    

def makequery(meta):
    query = "files from " + meta["inputdataset"] + " where"
    
     
    for item in meta:
        if (DEBUG): print (item)
        if meta[item] == None:
            continue
        if "." not in item:
            continue
        val = meta[item]
        if item == "other":
            query += " "+val[1:-1]
        else:
            query += " "+item+"="+val
        query += " and"
        if (DEBUG): print(query)
    query = query[:-4]
    if (DEBUG): print (query)
    

# do time range - takes some work as there are two possibilities
    if meta["min_time"] != None or meta["max_time"] != None:
        min = '2018-01-01'
        max = '2100-01-01'
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

        
        if var != "created_timestamp":
            timequery = " and %s >= datetime('%s')"%(var,min)
            timequery += " and %s <= datetime('%s')"%(var,max)
        else:
            timequery = " and %s >= '%s'"%(var,min)
            timequery += " and %s <= '%s'"%(var,max)
        query += timequery
    else:
        print ("No time range set, use all files")

    if meta["ordered"]: query += " ordered "

    if meta["skip"] != None:
            query += " skip %s"%meta["skip"]

    if meta["limit"] != None:
            query += " limit %s"%meta["limit"]
      
    #return "\"%s\""%query
    return query

def main():
        parser = ap()
        parser.add_argument('--namespace',type=str,default=os.getenv("USER"),help="metacat namespace for dataset")
        parser.add_argument('--time_var',type=str,default="created",help="creation time to select ['created'] or 'raw']")
        parser.add_argument('--min_time',type=str,help='min time range (inclusive) YYYY-MM-DD UTC')
        parser.add_argument('--max_time',type=str,help='end time range (inclusive) YYYY-MM-DD UTC')
        parser.add_argument('--file_type',dest='file_type',required=True,type=str, help='["detector","mc"]')
        parser.add_argument('--run_type',required=True,type=str, help='run_type, example="prododune-sp"')
        parser.add_argument('--campaign',type=str, help='DUNE Campaign')
        parser.add_argument('--family',type=str, help='Application Family')
        parser.add_argument('--name', type=str, help='Application Name')
        parser.add_argument('--version', type=str, help='Application Version')
        parser.add_argument('--data_tier', type=str, help='data tier')
        parser.add_argument('--data_stream', type=str, help='data stream for output file if only one')
        parser.add_argument('--inputdataset',default='dune:all',type=str,help='parent dataset, default=[\"dune:all\"]')
        parser.add_argument('--user', type=str, help='user name')
        parser.add_argument('--ordered',default=False,const=True,nargs="?", help='return list ordered for reproducibility')
        parser.add_argument('--limit',type=int, help='limit on # to return')
        parser.add_argument('--skip',type=int, help='skip N files')
        parser.add_argument('--other',type=str,help='other selections, for example, --other=\"detector.hv_value=180 and beam.momentum=1\" ')
        
        
        args = parser.parse_args()

        if DEBUG: print (args)

        required = ["file_type","run_type"]

        #metafield = makemetafields()
  
        if args.user == None and os.environ["USER"] != None:  args.user = os.environ["USER"]

        # load the valid arguements into query input form
#
#        meta = {}
#        check = 0
#
#
#        # make a map of args and values for valid metacat fields
#        for field in metafield:
#
#                val = getattr(args,arg)
#                if val == None:
#                    continue
#                if arg in required:
#                    check+=1
#
#                meta[metafield[arg]] = "\'%s\'"%(val)
        Tags = DefineCollectionTags()
        map = CollectionArgMap(Tags)
        for tag in Tags:
            argis=map[tag]
            val = getattr(args,argis)
            if DEBUG: print (tag,argis,val)
            Tags[tag] = val
            if DEBUG: print (tag,argis,val,type(val))
            if type(val) == 'str' and "-" in val:
                Tags[tag] = "\'%s\'"%(val)
            
            
        
            
        if (DEBUG): print (Tags)
#        # check that enough required items are present
#        if check < len(required):
#              print ("a required field is missing - I must have ",required)
#              sys.exit(1)

        
        fname = "test.json"
        jsonwrite(fname,Tags)
        query = makequery(Tags)
        
        
        
        
        return query

## command line, explains the variables.
if __name__ == "__main__":
    mc_client = MetaCatClient('https://metacat.fnal.gov:9443/dune_meta_prod/app')
    thequery = main()
    print ("metacat query","\""+thequery+"\"")
    query_files = list(mc_client.query(thequery))
     
    for l in query_files:
         
         print("%s:%s"%(l["namespace"],l["name"]))
