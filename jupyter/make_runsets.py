import os,time,sys,datetime, glob, fnmatch,string,subprocess, json

import samweb_client
samweb = samweb_client.SAMWebClient(experiment='dune')


#############################################
## Main Function
#############################################


DEBUG = False
version = "v07_08_00_03"

def h_header():
    return "<table border=\"1\"><thead><tr><th bgcolor=\"7caed5\">SAM Dataset Name</th><th bgcolor=\"7caed5\">SAM Query Links</th><th bgcolor=\"7caed5\">Comment</th></tr></thead><tbody>"

def h_body(defname,num):
    return "<tr><td>%s </td><td>%d</td><td><a href=\"http://samweb.fnal.gov:8480/sam/dune/api/definitions/name/%s/describe\"> describe</a>,<a href=\"http://samweb.fnal.gov:8480/sam/dune/api/definitions/name/%s/files/summary\"> summary</a>,<a href=\"http://samweb.fnal.gov:8480/sam/dune/api/definitions/name/%s/files/list\"> files</a></td>\n</tr>"%(defname,num,defname,defnamedefname)

def h_ender():
    
    return "<td></td></tr><tr></tr></tbody></table>"

def allrunlist(min=400,max=600):


  for run in range(min,max+1):
    
    runno = run

    samgeneral  = "run_type protodune-sp and run_number %s"%runno
    
    raw_query = samgeneral + " and data_tier raw"
    reco_query = samgeneral + " and version %s"%version
    
    defname = "runset-%d-reco-%s-v0"%(runno,version)
    
    
    rdefname = "runset-%d-raw-v0"%(runno)
    
    events = samweb.listFilesSummary(raw_query)
    #print events["total_event_count"]
    if events["total_event_count"] < 100:
        continue
    try:
        samweb.listFilesSummary("defname:"+rdefname)
        print "#defname already exists", rdefname
    
    except:
        print "samweb create-definition ",rdefname,'"',raw_query,'"'
    events = samweb.listFilesSummary(reco_query)
    if events["total_event_count"] < 1:
        continue
    try:
        samweb.listFilesSummary("defname:"+defname)
        print "#defname already exists", defname

    except:
        print "samweb create-definition ",defname,'"', reco_query, '"'
allrunlist(400,600)
