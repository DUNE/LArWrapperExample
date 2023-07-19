import os,time,sys,datetime, glob, fnmatch,string,subprocess, json

import samweb_client
samweb = samweb_client.SAMWebClient(experiment='dune')

f = open("disks.tex",'w')
for d in samweb.listDataDisks():
    print ("disk",d["node"])
    dims = "full_path "+d["node"]+"%%"
    dims += " and data_tier full-reconstructed and DUNE.campaign PDSPProd4a%%"
    print (dims)
    result = samweb.listFilesSummary(dims)
    print (result)
    if (result["file_count"]<1000):
        continue
    size = float(result["total_file_size"])/1.0E15

    s = "%20s %5.1f" %(d["node"],size)
    stex = "%20s&%5.1f\\\\\n" %(d["node"],size)
    print (s)
    f.write(stex)
