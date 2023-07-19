import os,time,sys,datetime, glob, fnmatch,string,subprocess, json

import samweb_client
samweb = samweb_client.SAMWebClient(experiment='dune')


#############################################
## Main Function
#############################################


DEBUG = False
RAW = False
version = "v08_27_XX"
sversion = "v08_27_%"

def h_header():
    
    
    header = "<table border=\"1\"><thead><tr><th bgcolor=\"7caed5\">SAM Dataset Name</th><th bgcolor=\"7caed5\">Events</th><th bgcolor=\"7caed5\">SAM Query Links</th><th bgcolor=\"7caed5\">Comment</th></tr></thead><tbody>\n"
    return header

def h_body(defname,num):
    return "<tr><td>%s </td><td>%d</td><td><a href=\"http://samweb.fnal.gov:8480/sam/dune/api/definitions/name/%s/describe\"> describe</a>,<a href=\"http://samweb.fnal.gov:8480/sam/dune/api/definitions/name/%s/files/summary\"> summary</a>,<a href=\"http://samweb.fnal.gov:8480/sam/dune/api/definitions/name/%s/files/list\"> files</a></td>\n</tr>"%(defname,num,defname,defname,defname)

def h_ender():
    
    return "<td></td></tr><tr></tr></tbody></table>"

def allrunlist(min=5141,max=5841):

  raw = open("rawlist.html",'w')
  raw.write("<h2> Raw Data Samples for Each Run </h2>\n\r")
  raw.write("predefined definitions like <b>protodune-sp_runset_RUNNO_raw_v0</b>\n\r")
  reco = open("recolist%s.html"%version,'w')
  raw.write(h_header())
  
  for run in range(min,max+1):
    
    runno = run

    samgeneral  = "run_type protodune-sp and file_type detector and run_number %s and data_stream in ('physics')"%runno
    
    
    raw_query = samgeneral + " and data_tier raw"
    reco_query = samgeneral + " and data_tier full-reconstructed and version %s"%sversion
    
    defname = "protodune-sp_runset_%d_reco_%s_v0"%(runno,version)
    
    
    rdefname = "protodune-sp_runset_%d_raw_v0"%(runno)
    
    events = samweb.listFilesSummary(raw_query)['total_event_count']
    if events < 1:
      continue
    #print events
    if RAW:
      #print events["total_event_count"]
      if events["total_event_count"] < 1:
          continue
      raw.write(h_body(rdefname,events["total_event_count"]))
      try:
          samweb.listFilesSummary("defname:"+rdefname)
          print "#defname already exists", rdefname
      
      except:
          print "samweb create-definition ",rdefname,'"',raw_query,'"'

    events = samweb.listFilesSummary(reco_query)
      #if events["total_event_count"] < 1:
      # continue
    try:
        samweb.listFilesSummary("defname:"+defname)
        print "#defname already exists", defname

    except:
        print "samweb create-definition ",defname,'"', reco_query, '"'
  raw.write(h_ender())
allrunlist(5141,5841)
