import os,time,sys,datetime, glob, fnmatch,string,subprocess, json

import samweb_client
samweb = samweb_client.SAMWebClient(experiment='dune')

firstyear = 2018
lastyear = 2021
out = open("YearlySummary.csv",'w')
line = "val, type, expt, trigger, tier,"
for year in range(firstyear,lastyear+1):
  line = line + "%d"%(year)
  if year != lastyear:
    line = line + ","
  else:
    line = line + "\n"
out.write(line)
  
for type in ["mc","detector"]:
  for expt in ["protodune-sp","protodune-dp","neardet","fardet","fardet-sp","iceberg","test", "311","311_dp_light","physics","ALL"]:
    for stream in ["physics","cosmics","test","commissioning","ALL"]:
      #if type == "mc" and stream != "ALL":
      #  continue
      for tier in ["raw","full-reconstructed","pandora_info","hit-reconstructed","simulated","detector-simulated","ALL"]:
          if type == "detector" and tier in ("simulated","detector-simulated"):
            continue
          if type == "mc" and tier in "raw":
            continue
          lineevents = "events, %s, %s, %s, %s,"%(type,expt,stream,tier)
          linesize = "size (TB), %s,  %s, %s, %s,"%(type,expt,stream,tier)
          sumevents = 0
          otherevents = 0
          othersize = 0
          for year in range(firstyear,lastyear+1):
            if year != firstyear:
              lineevents = lineevents+ ","
              linesize = linesize + ","
            command = "file_type " + type
            command += " and data_tier "+tier
            command += " and data_stream " + stream
            command += " and run_type " + expt
            #if( type != "mc"):
            #  command += " and run_type " + expt
            command += " and create_date >= " +" %d-01-01"%(year)
            command += " and create_date <= " +" %d-12-31"%(year)
            command = command.replace("ALL","%")
          #  print (command)
            result = samweb.listFilesSummary(command)
            
            
            file_count = result["file_count"]
            if file_count == None:
              file_count = 0
            events = result["total_event_count"]
            if events == None:
              events = 0
            #print (" events is ",events)
            sumevents += events
            ssize = result["total_file_size"]
            if ssize == None:
              ssize = 0
            ssize = ssize/1000/1000/1000/1000.
            if events > 0:
              fsize = ssize/events*1000*1000
            else:
              fsize = 0.0
            
            lineevents = lineevents + "%d"%(events)
            linesize = linesize + "{:.1f}".format(ssize)
            
  #          else:
  #            lineevents = lineevents+ "\n"
  #            linesize = linesize + "\n"
  #          print (year, expt,tier,stream,file_count,events,"%s TB"%ssize,fsize," MB")
            linesize = linesize.replace("%","ALL")
            lineevents = lineevents.replace("%","ALL")
          lineevents = lineevents+ "\n"
          linesize = linesize + "\n"
          if sumevents == 0:
            continue
          out.write(lineevents)
          out.write(linesize)
          print (lineevents.replace(",","\t"))
          print (linesize.replace(",","\t"))


out.close()
    
