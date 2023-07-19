import os,time,sys,datetime, glob, fnmatch,string,subprocess, json

import samweb_client
DEBUG=False
samweb = samweb_client.SAMWebClient(experiment='dune')
#print (samweb.listDataDisks())
recodata = "run_type 'protodune-sp' and file_type detector  and data_stream in physics and data_tier 'reco-recalibrated' and version v09_30_00"
rawphysics = "run_type 'protodune-sp' and file_type detector  and data_stream in physics and data_tier raw"

ignore = ["lbnedata","dcache","dunedata","ph.liv.ac.uk"]
defs = open("definitions.txt",'r')
definitions = defs.readlines()
#print (definitions)
print (definitions)
#print (definitions)
f = open("disk_content.csv",'w')
#f.write("\documentclass[10pt]{article}\n"+
#"\setlength{\textwidth}{6.5in}\n"+ "\setlength{\oddsidemargin}{0.00in}\n"+ "\begin{document}\n"+"\begin{table}\n"+"\begin{tabular}{rrrr}")
count = 0
thedisks = []
for d in samweb.listDataDisks():
    disk = d["node"]
    if disk in ignore:
        continue
    if disk not in thedisks:
        thedisks.append(disk)
thedisks.append("/pnfs/")
print (thedisks)
f.write("RSE, dataset, size(PB), events\n")
for disk in thedisks:
  print ("disk",disk)
  if disk=="dcache":
     continue
  if disk in ignore:
    print ("ignoring", disk)
    continue
  checkdim1 = "full_path '"+disk+"%'"
  
  result = samweb.listFilesSummary(checkdim1)
  if result["file_count"]<100:
    print ("site", disk," has < 100 files")
    continue
  count = 0
  for thedataset in definitions:
    dataset = thedataset.strip()
   
    dims = "full_path '"+disk+"%'"
    dims += " and defname:"+dataset
    print (dims)
    result = samweb.listFilesSummary(dims)
    print (result)
    if (result["file_count"]<100):
        continue
    count +=1
    if count > 3 and DEBUG:
        continue
    size = float(result["total_file_size"])/1.0E15
    if result["total_event_count"] != None:
        events = result["total_event_count"]
    else:
        events = 0
    if "pnfs" in disk:
        disk = "/pnfs/"
    else:
        disk = disk
    s = "%s, %s, %7.3f, %d\n" %(disk,dataset,size,events)
    
    stex = "%20s & %60s & %7.3f & %d\\\\\n" %(disk,dataset,size,events)
    stex = stex.replace("_","\_")
    print (s)
    f.write(s)
f.close()
#f.write("\end{table}\n\end{tabular\n\end{document}")
