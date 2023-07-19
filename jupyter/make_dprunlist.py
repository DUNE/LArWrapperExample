import os,time,sys,datetime, glob, fnmatch,string,subprocess, json

import samweb_client
samweb = samweb_client.SAMWebClient(experiment='dune')


#############################################
## Main Function
#############################################


DEBUG = False
RAW = True
campaign = "NP02_run2019"
scampaign = "NP02_run2019"

def h_header():
    
    
    header = "<table border=\"1\"><thead><tr><th bgcolor=\"7caed5\">SAM Dataset Name</th><th bgcolor=\"7caed5\">Events</th><th bgcolor=\"7caed5\">SAM Query Links</th><th bgcolor=\"7caed5\">Comment</th></tr></thead><tbody>\n"
    return header

def h_body(defname,num):
    return "<tr><td>%s </td><td>%d</td><td><a href=\"http://samweb.fnal.gov:8480/sam/dune/api/definitions/name/%s/describe\"> describe</a>,<a href=\"http://samweb.fnal.gov:8480/sam/dune/api/definitions/name/%s/files/summary\"> summary</a>,<a href=\"http://samweb.fnal.gov:8480/sam/dune/api/definitions/name/%s/files/list\"> files</a></td>\n</tr>"%(defname,num,defname,defname,defname)

def h_ender():
    
    return "<td></td></tr><tr></tr></tbody></table>"

def allrunlist(min=1000,max=1500):

  raw = open("dprawlist.html",'w')
  raw.write("<h2> Raw Data Samples for Each Run </h2>\n\r")
  raw.write("predefined definitions like <b>protodune-dp_runset_RUNNO_cosmics_raw_v0</b>\n\r")
  reco = open("hit-recolist%s.html"%campaign,'w')
  reco.write("<h2> Reconstructed Data Samples for Each Run </h2>\n\r")
  reco.write("predefined definitions like <b>protodune-dp_runset_RUNNO_cosmics_hit-reco_CAMPAIGN_v0</b>\n\r")
  raw.write(h_header())
  reco.write(h_header())
  
  for run in range(min,max+1):
    
    runno = run

    samgeneral  = "run_type protodune-dp and file_type detector and run_number %s and data_stream in ('cosmics')"%runno
    
    
    raw_query = samgeneral + " and data_tier raw"
    reco_query = samgeneral + " and data_tier hit-reconstructed and DUNE.campaign %s"%scampaign
    
    defname = "protodune-dp_runset_%d_cosmics_hit-reco_%s_v0"%(runno,campaign)
    
    
    rdefname = "protodune-dp_runset_%d_cosmics_raw_v0"%(runno)
    #print "#",reco_query
    events = samweb.listFilesSummary(raw_query)['total_event_count']
    if events < 1:
       print "#no raw events for run ",runno
       continue
    
    # raw data
    if RAW:
      #print events["total_event_count"]
      if events < 1:
          continue
      raw.write(h_body(rdefname,events))
      try:
          samweb.listFilesSummary("defname:"+rdefname)
          print "#defname already exists", rdefname
      
      except:
          print "samweb create-definition ",rdefname,'"',raw_query,'"'
  # reconstructed files
    #print reco_query
    revents = samweb.listFilesSummary(reco_query)
    rn = revents["total_event_count"]
    
    if revents["total_event_count"] < 1:
       print "#no reco events for ",runno
       continue
    try:
        samweb.listFilesSummary("defname:"+defname)
        print "#defname already exists", defname
        reco.write(h_body(defname,rn))
    except:

        print "samweb create-definition ",defname,'"', reco_query, '"'
        reco.write(h_body(defname,rn))
  raw.write(h_ender())
  reco.write(h_ender())
allrunlist(1100,1800)
