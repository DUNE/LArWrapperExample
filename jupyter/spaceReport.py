import os,time,sys,datetime, glob, fnmatch,string,subprocess, json

import samweb_client
samweb = samweb_client.SAMWebClient(experiment='dune')

# report on disk space cataloged in sam

disks = samweb.listDataDisks()
#print disks[1]
top = "%10s  \t %10s \t%s"%("size","files","site")
print top
disks.append({"mount_point":"/pnfs/dune/tape_backed"})
for disk in disks:
  name = disk["mount_point"]
  path = disk["mount_point"]+"%"
  #print path
  defname = "full_path ='"+path+"'"
  #print defname
  result = samweb.listFilesSummary(defname)
  if result["total_file_size"] == None:
    continue
  events = result["total_event_count"]
  files = result["file_count"]
  ssize = result["total_file_size"]/1000/1000/1000/1000.

  out = "%10.0f TB\t %10s \t%s"%(ssize,files,name)
  print out

