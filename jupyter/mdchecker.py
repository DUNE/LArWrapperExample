# script to check metadata based on an json file.

#file_name is the file name - this needs to be unique within DUNE
#file_size is the file size in bytes
#user is the fnal unix user name of the person who is storing the file (need to generalize)
#content_status can be used to flag bad files/data - not used unless it is REALLY bad
#file_type is "detector" for data or "mc" for mc. "photon_detector" recently defined for np02
#file_format describes the format, can be root, artroot, binary ...
#data_tier is the stage in processing - raw, decoded, reconstructed, ... (should be lower case)
#application is a 3-form with top level (art), specific application (reco, filter, sim...) and version
#event_count number of events in the file
#data_stream allows separation of different raw data types - map to different tape families for better access.  test, cosmics, physics ....
#start_time UTC time that file writing started (required for raw, optional for reconstruction)
#end_time UTC time that file writing ended
#runs list of 3-forms of [run, subrun, detector type] detector type tells 35T from far detector 1, from protodune sp ...
#parents list of files that were processed to produce this file.  Can be many->one


import os,time,sys,datetime, glob, fnmatch,string,subprocess, json

import samweb_client
samweb = samweb_client.SAMWebClient(experiment='dune')

filename = sys.argv[1]
f = open(filename,'r')

md = json.load(f)

required = ["file_name","file_type","data_tier","application","event_count","data_stream","runs"]
preferred = ["start_time","end_time","parents","file_format","DUNE.campaign"]



missing  = []
maybe = []
for key in required:
  if not md.has_key(key):
    missing.append(key)

if len(missing) > 0:
  print "mdchecker ERROR: required fields that are missing:", missing

for key in preferred:
  if not md.has_key(key):
    maybe.append(key)

if len(maybe) > 0:
  print "mdchecker WARNING: preferred fields that are missing:", maybe

if md.has_key("application"):
  nover =  md["application"]["version"] == "null"
else:
  nover = True

if nover:
  print "mdchecker ERROR: no application version given, this is bad"



bad = len(missing) > 0 or nover

if bad:
  print "mdchecker ERROR: This metadata is not good, please fix"
  sys.exit(1)

print "mdchecker: metadata is probably ok but check that any missing preferred fields are reasonable"

sys.exit(0)



