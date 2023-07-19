#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os,time,sys,datetime, glob, fnmatch,string,subprocess, json, csv, jsonlines

if len(sys.argv)>1:
    dname = sys.argv[1]
else:
    dname = 'test.jsonl'

print (dname)
    
ignore = ["query","file_name","start_time","end_time", 'artdaq-core.timestamp', 'artdaq-core.version', 'artdaq.timestamp', 'artdaq.version', 'dune-artdaq.timestamp', 'dune-artdaq.version', 'dune-raw-data.timestamp','file_count','total_file_size_GB', 'total_event_count']

dname = 'newrequests.json'
dname = 'test.jsonl'

records = []

count = 0
if not "jsonl" in dname:
    f = open(dname,'r')
    j = json.load(f)
    for obj in j:
        records.append(j[obj])
else:
    f = jsonlines.open(dname,'r')
    
    for obj in f:
        count +=1
        if count < 10: print (count, obj)
        records.append(obj)

print (records[1:10])
        
        


# In[2]:


fields = []
unique = {}
for record in records:
    print (record)
    data = record
    for entry in data:
        if entry not in fields and entry != "query" and entry not in ignore:
            fields.append(entry)
            unique[entry] = []
            
print (fields)
            


# In[3]:


csvname = dname.replace("jsonl","csv")
csvname = csvname.replace("json","csv")

with open(csvname, 'w') as csvfile: 
    csvwriter = csv.writer(csvfile) 
        
    # writing the fields 
    csvwriter.writerow(fields) 

    for record in records:
        data = j[record]
        c = []
        #print (data)
        for field in fields:
            if field in data:
                c.append(data[field])
                if data[field] not in unique[field] and field not in ignore:
                    unique[field].append(data[field])
            else:
                c.append("")
        csvwriter.writerow(c)
        
sname = dname.replace('jsonl','txt')
sname = sname.replace('json','txt')
summary = open(sname,'w')

               
for x in unique:
    s =  "%s\n"%x
    summary.write(s)
    for y in unique[x]:
        s="\t%s\n"%y
        summary.write(s)
            
    
summary.close()
    
    
            


# In[ ]:




