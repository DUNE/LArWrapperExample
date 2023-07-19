import os,time,sys,datetime, glob, fnmatch,string,subprocess, json

import samweb_client
samweb = samweb_client.SAMWebClient(experiment='dune')


#############################################
## Main Function
#############################################


DEBUG = False
qversion = "(v08_27_%)"
version = "v08_27_XX"

def goodrunlist(goodruns="GoodBeamAug2019.csv"):
  thefile = open(goodruns,'r')
  thedata = thefile.readlines()
  for line in thedata[1:150]:
    fields = line.split(",")
    if len(fields[0])!=4:
      #print "#",fields
      continue
    runno = fields[0]
    hv = fields[3]
    beam = fields[4]
    samgeneral  = "run_type protodune-sp and run_number %s and file_type detector"%runno
    #print samgeneral
    hvcut = "" # and detector.hv_value %s"%hv
    #raw_query = samgeneral + hvcut + " and data_tier raw"
    reco_query = samgeneral + hvcut + " and data_tier full-reconstructed and version %s"%qversion
    #print samweb.listFilesSummary(raw_query)
    #print samweb.listFilesSummary(reco_query)
    defname = "runset-%s-reco-%s-hv-%skV-beam-%sGeV-v0"%(runno,version,hv,beam)
    
    print "samweb create-definition ",defname,'"', reco_query, '"'
    #rdefname = "runset-%s-raw-%skV-%sGeV-v0"%(runno,hv,beam)
    
#print "samweb create-definition ",rdefname,'"',raw_query,'"'

goodrunlist()
