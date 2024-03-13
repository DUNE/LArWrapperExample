
from argparse import ArgumentParser as ap
import sys
import os
import subprocess
import json
import zlib

MAX = 5  # max # to run over


from metacat.webapi import MetaCatClient 


def jsondump(adict):
    return json.dumps(adict,indent=4)                   

def adler32(data_file):
    checksum = zlib.adler32(b"")
    size = 0
    block = data_file.read(16*1024)
    while block:
        size += len(block)
        checksum = zlib.adler32(block, checksum)
        block = data_file.read(16*1024)

    checksum = "%08x" % (checksum,)
    return checksum


def getTemplate():
    return {
    "checksums": {
    "adler32": None,
    },
    "created_timestamp": None,
    "creator": None,
    "metadata":{
        "beam.polarity": 1,
        "core.application": "g4beamline",
        "core.application.family": "g4beamline",
        "core.application.name": "g4beamline",
        "core.application.version": "v34b",  # from parsing filename
        "core.data_stream": "beam",
        "core.data_tier": "g4-beam",
        "core.config_file_name": "????",
        "core.end_time": None,
        "core.event_count": 0, # from reading the root file
        "core.file_content_status": "good",
        "core.file_format": "root",
        "core.file_type": "mc",
        "core.first_event_number": 0,
        "core.group": "dune",
        "core.last_event_number": 0,
        "core.run_type": "pdsp-beam",
        "core.runs": [
            -1
            ],
        "core.runs_subruns": [
            -1
            ],
        "core.start_time": None,
        "dune.campaign": "PDSPProd4a",
        "dune.requestid": None,
        "dune_mc.generators": "g4beamline",
        "retention.class": "simulation",
        "retention.status": "active"
    },
    "name": None,
    "namespace": "pdsp_mc_reco",
    "retired": False,
    "retired_by": None,
    "retired_timestamp": None,
    "size": None,
    "updated_by": None,
    "updated_timestamp": None
}



f = open("List.txt",'r')

lines = f.readlines()

count = 0
directory = ""
for line in lines:
    #print ("new line",line,directory)
    fields = line.split(" ")
    l = len(fields)
    momentum = 0
    num = 0
    if "GeV/c" in line:
        momentum = fields[0]
    if "/pnfs/" in line or "/Users/" in line:
        
        directory = line.strip()
        print("set new directory",directory)
    
    if "Input files" in line:
        print (line,fields[2])
        num = int(fields[2][1:])
    if "H4" in line:
        newdata = getTemplate()
        name = fields[0]
        entries = int(fields[1])
        namemeta = name.split("_")
        version = namemeta[1]
        p = float(namemeta[2].replace("GeV",""))
        run = int(p*100000)
        if "negative" not in name:
            run += 1
        subrun = int(namemeta[5].replace(".root","")) + run*10000
        newmeta = newdata["metadata"]
        thefile = os.path.join(directory,name)
        
        #print ("thefile",directory,thefile)
        if os.path.exists(thefile):
            #print ("file exists")
            newdata["size"] = os.path.getsize(thefile)
            h = open(thefile, "rb")
            newdata["checksums"]["adler32"]=adler32(h)
            h.close()
        else:
            print ("file does not exist", thefile)
            newdata["size"] = None
            newdata["checksum"] = None
        newmeta["core.runs"] = [run]
        newmeta["core.runs_subruns"] = [subrun]
        newmeta["core.event_count"] = entries
        newmeta["first_event_number"] = 0
        newmeta["core.last_event_number"] = entries - 1
        newmeta["beam.momentum"] = p
        newdata["metadata"] = newmeta
        #print (version,run,subrun,p)
        newdata["name"] = name
        newdata["creator"] = os.getenv("USER")
        if count < MAX: 
            print (jsondump(newdata))  
        else:
            sys.exit(1)
        g = open(name+".json",'w')
        s = jsondump(newdata)
        g.write(s)
        g.close()
        count += 1
    else:
        print ("status", momentum, directory, num)