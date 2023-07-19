# adapted from MINERvA sam audit script

# arguments are

# python AuditProduction.py <data/mc> <runmin-runmax> [version]

import os,time,sys,datetime, glob, fnmatch,string,subprocess, json

import samweb_client
samweb = samweb_client.SAMWebClient(experiment='dune')


#############################################
## Main Function
#############################################


DEBUG = False

# this can be extended for MC production by adding "mc" in types and putting in the right stuff
types = {}
types["data"] = ["raw","full"]
tiers = {}

# these give shorter names for the tables

tiers["data"]= {"raw":"raw","full":"hit-reconstructed"}
#{"decoded":"decoded-raw","hits":"hit-reconstructed","raw":"raw","full":"full-reconstructed"}

# you can specify a code version

version = "%"

if len(sys.argv) < 2:
    print " need to provide <mc/data> <run-range=a-b> [version] "
    sys.exit(1)

datatype = sys.argv[1]
if datatype not in ["data","mc"]:
  print " need data or mc "
  sys.exit(1)

# runrange can actually be a single number

outname = "audit_%s_%s.txt"%(sys.argv[1],sys.argv[2])
outfile = open(outname,'w')
runrange = sys.argv[2]
runs = runrange.split("-")
runmin = 0
runmax = 0
if len(runs)==1:
  runmin = int(runs)
  runmax = int(runs)
else:
  runmin = int(runs[0])
  runmax = int(runs[1])


    
if len(sys.argv) > 3:
    version = sys.argv[3]

# holdover from minerva - sorry

runsets=[[runmin,runmax]]
count = 0
print "Running over these sets", runsets
tots = {}
tots["raw"] = 0.0
tots["full"] = 0.0

for sets in runsets:
  for runs in range(sets[0],sets[1]+1):
    sizeper = {}
    answer = {}
    tapeanswer = {}
    sum = {}
    if count%10 == 0:
        out =  "-------------------------------------------------"
        print out
        outfile.write(out+"\n")
    count +=1
    for type in types[datatype]:
        myrun = runs
        myversion = version
        quality = " "
        # make a sam query - can add quality cuts later
        tapequery =  " run_number %d and run_type protodune-dp and data_tier %s and data_stream in (physics,cosmics,test) "%(myrun,tiers[datatype][type])
        #tapequery =  " run_number %d and run_type protodune-sp and data_tier %s and data_quality.online_good_run_list 1 "%(myrun,tiers[datatype][type])
        if tiers[datatype][type] != "raw":
          tapequery += "and version "+version
        
        # this checks to see if the file has a location or not
        
        query = tapequery+" and availability:anylocation "

        if runmin == runmax:
          print query
        # just count the files...
        fileinfo = len(samweb.listFiles(query))
        tapeinfo = len(samweb.listFiles(tapequery))
       
        summary = samweb.listFilesSummary(query)
          #print summary
        nevents = summary["total_event_count"]
        size = summary["total_file_size"]
    
        sizeper[type] = 0
        if nevents > 0:
          sizeper[type] = size/nevents/1000000.
        answer[type] = nevents
        tapeanswer[type] = tapeinfo
  
    status = ""
    tapestatus = []
    for key in types[datatype]:
        if tapeanswer[key] != answer[key]:
            tapestatus.append(key)
    answerline = ""
    for key in types[datatype]:
      
        answerline += "%s %s\t" % (key,answer[key])
    if answer["full"] == None:
       answer["full"] = 0
    if answer["raw"] != None and answer["raw"] > 0:
    
      percent = float(answer["full"])/float(answer["raw"]/100.)
      formatted = "%% %5.2f\t size per event %5.2fM"%(percent,sizeper["raw"])
      out = "%d\t%s\t%s"% (runs,answerline, formatted)
      print out
      outfile.write(out+"\n")
      tots["raw"]=tots["raw"]+float(answer["raw"])
      tots["full"]+=float(answer["full"])
out =  "%d\t%d\t%f" %(tots["raw"], tots["full"], tots["full"]/tots["raw"])
print out
outfile.write(out+"\n")
