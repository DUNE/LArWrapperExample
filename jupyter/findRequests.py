#!/usr/bin/env python
# coding: utf-8

# In[1]:


# brute force loop over files in samweb and create a list of requestids with characteristics

# HMS 6-17-2023


import os,time,sys,datetime, glob, fnmatch,string,subprocess, json, jsonlines

import samweb_client
samweb = samweb_client.SAMWebClient(experiment='dune')
DEBUG = False
if len(sys.argv)>1:
    year = sys.argv[1]
else:
    year = "2021"

fname = "%srequests.jsonl"%year
if DEBUG: fname = "%stest.jsonl"%year
writer = jsonlines.open(fname, mode='w') 
      
#mode = "data"

max = 100
# list of things that are particular to that file, not the request
reject = ["start_time","end_time", 'file_name','process_id','event_count','DUNE_data.detector_config','parents','runs', 'file_id', 'create_date','update_date', 'update_user', 'file_size', 'checksum', 'content_status',  'group',  'first_event', 'last_event', 'art.file_format_era', 'art.file_format_version', 'art.first_event', 'art.last_event', 'art.process_name', 'art.run_type']


# In[2]:


def safeget(md,key):
    r = None
    if key in md:
        if type(md[key]) == 'int':
            r = str(md[key])
        else:
            r = md[key]
    return r


# In[3]:


# get a list of first files in runs for mc

# if mode == "mc":
#     query = "user dunepro and file_type mc and data_tier full-reconstructed and first_event 1 and create_date > 2022-01-01 and user dunepro"
# else:
#     query = "user dunepro and file_type detector and first_event 1 and create_date > 2022-01-01 minus data_tier root-tuple"

query = "user dunepro and first_event 1 and create_date > %s-01-01 and create_date <= %s-12-31 minus data_tier root-tuple"%(year,year)
filelist = samweb.listFiles(dimensions=query)


# In[ ]:





descrip=""
descriplist = {}
count = 0
for file in filelist:

    count +=1
    if DEBUG and count > max:
        print ("quitting after", count, "files")
        break
    md = samweb.getMetadata(file)
    k = {}
    
    # define a list of valid parameter names
    k["file_type"] = safeget(md,"file_type")
    
    runs = safeget(md,"runs")
    if runs != None:
        k["run_type"] = runs[0][2]
    else:
        k["run_type"] = None
    md["run_type"] = k["run_type"]
    k["DUNE.requestid"] = safeget(md,"DUNE.requestid")
    k["DUNE.campaign"] = safeget(md,"DUNE.campaign")
    if safeget(md,"application") != None:
        k["version"] = safeget(md,"application")["version"]
    k["data_tier"] = safeget(md,"data_tier")
    k["data_stream"] = safeget(md,"data_stream")
    k["detector.hv_value"] = safeget(md,"detector.hv_value")
    k["beam.momentum"] = safeget(md,"beam.momentum")
    k["DUNE_MC.beam_energy"] = safeget(md,"DUNE_MC.beam_energy")
    k["DUNE_MC.electron_lifetime"] = safeget(md,"DUNE_MC.electron_lifetime")
    k["DUNE_MC.generators"] = safeget(md,"DUNE_MC.generators")
    
    # deal with pathological generator names. 
    if k["DUNE_MC.generators"] != None:
        if "poms_recover" in k["DUNE_MC.generators"]:
            print ("skip poms_recover")
            k["DUNE_MC.generators"] =  None
        elif "scalar" in k["DUNE_MC.generators"] :
            print ("skip scalar")
            k["DUNE_MC.generators"] =  None
     
    k["DUNE_MC.liquid_flow"] = safeget(md,"DUNE_MC.liquid_flow")
    k["DUNE_MC.space_charge"] = safeget(md,"DUNE_MC.space_charge")
    k["DUNE_MC.with_cosmics"] = safeget(md,"DUNE_MC.with_cosmics")
                                             

    tag = "TAG_"
    mquery = ""
    for x in k:
        if k[x] != None:
            tag += str(k[x])
            mquery += x + " " + str(k[x]) + " and "
        else:
            tag += "X"
        tag += "___"

    request = tag[:-3]
    mquery = mquery[:-4]


    if request in descriplist: continue

    #if DEBUG: print (request)
    #if DEBUG: print (mquery) 

    print ("new requestid",request)
    # get rid of a lot of extra metadata

    newreject = []
    for y in md.keys():
        if "DUNE_data" in y:
            newreject.append(y)

    for x in reject:
        if x in md:
            md.pop(x)
    for x in newreject:
        if x in md:
            md.pop(x)

    descriplist[request]=md

    summary = samweb.listFilesSummary(mquery)
    #print (mquery, summary)
    descriplist[request]["query"] = mquery
    descriplist[request]["file_count"] = summary["file_count"]
    if summary["total_file_size"] != None:
        descriplist[request]['total_file_size_GB'] = int(summary["total_file_size"]/1000000000)
    else:
        descriplist[request]['total_file_size_GB'] = None
    descriplist[request]["total_event_count"] = summary["total_event_count"]
    if (DEBUG): print (descriplist[request])
    
    writer.write(descriplist[request])


# In[ ]:


print ("processed", count, "records")
#print (descriplist)
fname = "newrequests.jsonl"
if DEBUG: fname = "test.jsonl"
#f = open(fname,'w')
#json.dump(descriplist,f,indent = 4)
#f.close()

for x in descriplist:
    print (x, "\t events = ", descriplist[x]["total_event_count"], " \t size = ", descriplist[x]["total_file_size_GB"],"GB")


# In[ ]:


writer.close()

# for a in descriplist:
#     query =  "DUNE.requestid %s"%a
#     summary = samweb.listFilesSummary(query)
#     print (query, summary)


# In[ ]:





# In[ ]:




