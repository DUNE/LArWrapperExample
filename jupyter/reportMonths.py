import os,time,sys,datetime, glob, fnmatch,string,subprocess, json

import samweb_client
samweb = samweb_client.SAMWebClient(experiment='dune')
campaigns = ["PDSPProd4","PDSPProd2","MC_Summer2020","keepup_v08_55_01","keepup_v08_27_01",
"PDSPProd3","diffusion_RITM0986948","mcc11","NP02_run2020","MC_Winter2021","RITM1103733","PDSPProd4a","diffusion_RITM1131173"]
#from datetime import date,datetime
from dateutil import parser, relativedelta
#import dateutil
first = "2020-07-01"
last = "2021-08-01"

start_date = parser.isoparse(first)
end_date = parser.isoparse(last)

dates = []
nextdates = []
m = start_date
while m < end_date:
  d = m.strftime('%Y-%m-%d')
  dates.append(d)
  m = m + relativedelta.relativedelta(months=1)
  d = m.strftime('%Y-%m-%d')
  nextdates.append(d)
  
#firstyear = 2020
#lastyear = 2020
#firstmonth = 10
#lastmonth = 12
#dates = []
#nextdates = []
#for year in range(firstyear,lastyear+1):
#  for month in range( firstmonth, lastmonth+1):
#    dates.append("%4d-%02d"%(year,(month-1)%12+1))
#    nextmonth = (month)%12+1
#    nextyear = year
#    if nextmonth == 1:
#      nextyear = year+1
#    nextdates.append("%4d-%02d"%(nextyear,nextmonth))
print (dates)
out = open("%s-%s-months.csv"%(dates[0],dates[-1]),'w')
line = "val, type, expt, trigger, tier,,"
for date in dates:
  line = line + "%s"%(date)
  line = line + ","
line = line + "\n"
out.write(line)

expts = ["ALL","protodune-sp","protodune-dp","neardet","fardet","fardet-sp","physics","iceberg"] #,"iceberg","test", "311","311_dp_light","physics"]
streams = ["ALL","physics","cosmics","test","commissioning"]
  
tiers = ["ALL","raw","full-reconstructed","pandora_info","hit-reconstructed","simulated","detector-simulated","unknown","sam-user","reco-recalibrated","generated","sam-user"]
types =  ["mc","detector"]
for type in types:
  for expt in expts:
    if type == "detector" and expt  not in ["ALL","protodune-sp","protodune-dp","iceberg"]:
      continue
    for stream in streams:
      #if type == "mc" and stream != "ALL":
      #  continue
      for tier in tiers:
          if type == "detector" and tier in ("simulated","detector-simulated"):
            continue
          if type == "mc" and tier in "raw":
            continue
          lineevents = "events, %s, %s, %s, %s,"%(type,expt,stream,tier)
          linesize = "size (TB), %s, %s, %s, %s,"%(type,expt,stream,tier)
          sumevents = 0
          otherevents = 0
          othersize = 0
          for i in range(0,len(dates)):
            
            lineevents = lineevents+ ","
            linesize = linesize + ","
            command = "file_type " + type
            command += " and data_tier "+tier
            command += " and data_stream " + stream
            command += " and run_type " + expt
            #if( type != "mc"):
            #  command += " and run_type " + expt
            command += " and create_date >= " +" %s"%(dates[i])
            command += " and create_date < " +" %s"%(nextdates[i])
            command = command.replace("ALL","%")
            print (command)
            result = samweb.listFilesSummary(command)
            print (expt,stream,tier,type,result)
            
            file_count = result["file_count"]
            if file_count == None or file_count ==0:
              file_count = 0
            #if stream == "ALL" or tier == "ALL" or expt == "ALL" or type == "ALL":
#                print " got zero for ALL so break",type,stream,tier,expt
#                break

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
    
