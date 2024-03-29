"""metacat query_creator"""
##
# @mainpage queryCreator
#
# @section description_main  
#
##
# @file queryCreator.py

DEBUG = True

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

    for core in ["other"]:
         metafield[core] =  "other"

    if DEBUG: print(metafield)

    return metafield

def makequery(meta,inputdataset=None,ordered=None,skip=None,limit=None,min_time=None,max_time=None,timevar="created"):
    query = "files from " + inputdataset + " where"
    i  = 0
     
    for item in meta:
        if "_time" in item: 
             i+=1
             continue
        val = meta[item]
        if item == "other":
            query += " "+val[1:-1]
        else:
            query += " "+item+"="+val
        i += 1
        if i < len(meta): 
            query += " and"    
    

# do time range
    if min_time == None and max_time == None:
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
    else:
        print ("No time range set, use all files")

    if ordered: query += " ordered "

    if skip != None:
            query += " skip %d"%skip

    if limit != None:
            query += " limit %d"%limit
      
    #return "\"%s\""%query
    return query

def main():
        parser = ap()
        parser.add_argument('--namespace',type=str,default=os.getenv("USER"),help="metacat namespace for dataset")
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
        parser.add_argument('--inputdataset',default='dune:all',type=str,help='parent dataset, default=[\"dune:all\"]')
        parser.add_argument('--user', type=str, help='user name')
        parser.add_argument('--ordered',default=False,type=bool, help='return list ordered for reproducibility')
        parser.add_argument('--limit',type=int, help='limit on # to return')
        parser.add_argument('--skip',type=int, help='skip N files')
        parser.add_argument('--other',type=str,help='other selections, for example, --other=\"detector.hv_value=180 and beam.momentum=1\" ')
        
        
        args = parser.parse_args()

        if DEBUG: print (args)

        required = ["file_type","run_type"]

        metafield = makemetafields()
  
        if args.user == None and os.environ["USER"] != None:  args.user = os.environ["USER"]

        # load the valid arguements into query input form

        meta = {}
        check = 0


        # make a map of args and values for valid metacat fields
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

        query = makequery(meta,inputdataset=args.inputdataset,ordered=args.ordered,skip=args.skip,limit=args.limit,min_time=args.min_time,max_time=args.max_time,timevar=args.timevar)
        
        tags = {
        dataset
}
        
        return query

## command line, explains the variables.
if __name__ == "__main__":
    mc_client = MetaCatClient(os.getenv("METACAT_SERVER_URL"))
    thequery = main()
    print ("metacat query","\""+thequery+"\"")
    query_files = list(mc_client.query(thequery))
     
    for l in query_files:
         
         print("%s:%s"%(l["namespace"],l["name"]))
