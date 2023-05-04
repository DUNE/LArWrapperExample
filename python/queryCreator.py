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

#rom datetime import date,timezone,datetime
#from dateutil import parser as dp
from metacat.webapi import MetaCatClient 

# # convert a date into a timestamp
# def human2number(stamp):
#   parsed = dp.isoparse(stamp)
#   print ( parsed.timestamp())
#   return parsed.timestamp()
  
## translate arguemnts into metacat fields
def makemetafields():
    metafield = {}

    for core in ["file_type","run_type","data_tier","data_stream"]:
            metafield[core] = "core."+core
        
    for core in ["campaign"]:
            metafield[core] = "DUNE.campaign"

    for core in ["family","name","version"]:
            metafield[core] = "core.application."+core
    return metafield

def makequery(meta,dataset=None,ordered=None,skip=None,limit=None,min_time=None,max_time=None,timevar="file"):
    query = "files from " + dataset + " where"
    i  = 0
     
    for item in meta:
        if "_time" in item: 
             i+=1
             continue
        operator = "="
        val = meta[item]
         
        
        query += " "+item+operator+val
        i += 1
        if i < len(meta): 
            query += " and"    
    

# do time range

    min = '2018-01-01'
    max = '2100-01-01'
    if min_time != None:
        min = min_time
        
    if max_time != None:
        max = max_time
    
    if timevar == "created":
         var = "created_timestamp"
    elif timevar == "raw":
         var = "core.start_time"
    else:
         print (" undercognized timevar")
         sys.exit(1)

    if min_time != None or max_time != None:
        if var != "created_timestamp":
            timequery = " and %s >= datetime('%s')"%(var,min)
            timequery += " and %s <= datetime('%s')"%(var,max)
        else:
            timequery = " and %s >= '%s'"%(var,min)
            timequery += " and %s <= '%s'"%(var,max)
        query += timequery

    if ordered: query += " ordered "

    if skip != None:
            query += " skip %d"%skip

    if limit != None:
            query += " limit %d"%limit
      
    #return "\"%s\""%query
    return query

def main():
        parser = ap()
        parser.add_argument('--timevar',type=str,default="created",help="creation time to select ['created'] or 'raw']")
        parser.add_argument('--min_time',type=str,help='min time range (inclusive) YYYY-MM-DD UTC')
        parser.add_argument('--max_time',type=str,help='end time range (inclusive) YYYY-MM-DD UTC')
        parser.add_argument('--file_type',required=True,type=str, help='["detector","mc"]')
        parser.add_argument('--run_type',required=True,type=str, help='run_type, example="prododune-sp"')
        parser.add_argument('--campaign',type=str, help='DUNE Campaign')
        parser.add_argument('--family',type=str, help='Application Family')
        parser.add_argument('--name', type=str, help='Application Name')
        parser.add_argument('--version', type=str, help='Application Version')
        parser.add_argument('--data_tier', type=str, help='data tier')
        parser.add_argument('--data_stream', type=str, help='data stream for output file if only one')
        parser.add_argument("--dataset",default="dune:all",type=str,help="parent dataset, default=[DUNE:ALL]")
        parser.add_argument('--user', type=str, help='user name')
        parser.add_argument('--ordered',default=False,type=bool, help='return list ordered for reproducibility')
        parser.add_argument('--limit',type=int, help='limit on # to return')
        parser.add_argument('--skip',type=int, help='skip N files')
        
        
        args = parser.parse_args()

        if DEBUG: print (args)

        required = ["file_type","run_type"]

        metafield = makemetafields()
  
        if args.user == None and os.environ["USER"] != None:  args.user = os.environ["USER"]

        # load the valid arguements into query input form

        meta = {}
        check = 0

        for arg in metafield:
                val = getattr(args,arg)
                if val == None: 
                    continue
                if arg in required:
                    check+=1
                            
                meta[metafield[arg]] = "\'%s\'"%(val)

        # check that enough required items are present
        if check < len(required):
              print ("a required field is missing - I must have ",required)
              sys.exit(1)

        query = makequery(meta,dataset=args.dataset,ordered=args.ordered,skip=args.skip,limit=args.limit,min_time=args.min_time,max_time=args.max_time,timevar=args.timevar)
        
        return query

## command line, explains the variables.
if __name__ == "__main__":
    mc_client = MetaCatClient('https://metacat.fnal.gov:9443/dune_meta_demo/app')
    thequery = main()
    print ("metacat query",thequery)
    query_files = list(mc_client.query(thequery))
    for l in query_files:
         print(l["name"])
