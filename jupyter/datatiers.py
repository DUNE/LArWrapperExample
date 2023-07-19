import os,time,sys,datetime, glob, fnmatch,string,subprocess, json

import samweb_client
samweb = samweb_client.SAMWebClient(experiment='dune')

# check to see significance of a parameter
def checkdimGB(parameter, value):
	command = "%s %s"%(parameter,value)
	result = samweb.listFilesSummary(command)
	if result == None:
		return -1
	if result["total_file_size"] == None:
		return -1
	return result["total_file_size"]/1000/1000/1000

# if there are less than cut GB of data for the parameter skip
def clean(parameter,list,cut=10000):
	skip = []
	sizes = {}
	for x in list:
		sizes[x] = checkdimGB(parameter,x)
		if sizes[x] == None or sizes[x] <cut:
			skip.append(x)
	for x in skip:
		if x == "ALL":
			continue
		list.remove(x)
		print ("remove item ", x, " from ", parameter, sizes[x])
	return list

data_tiers=["ALL",
"simulated",
"raw",
"hit-reconstructed",
"full-reconstructed",
#"generated",
"detector-simulated",
#"reconstructed-2d",
#"reconstructed-3d",
#"sliced",
#"dc1input",
#"dc1output",
"root-tuple",
#"root-hist",
#"dqm",
"decoded-raw",
#"sam-user",
"pandora_info",
"reco-recalibrated",
#"storage-testing",
#"root-tuple-virtual",
]

data_tiers = clean("data_tier",data_tiers,1000)

print ("data_tiers",data_tiers)

run_types = ["ALL",
#"calibration",
#"cosmic",
"physics",
#"special",
#"test",
"fardet",
"neardet",
#"protodune",
"protodune-sp",
"protodune-dp",
#"35ton",
#"311",
#"311_dp_light",
"iceberg",
"fardet-sp",
"fardet-dp",
"fardet-moo",
#"np04_vst",
"vd-coldbox-bottom",
"vd-coldbox-top",
"protodune-hd",
"hd-coldbox",
"vd-protodune-arapucas",
"protodune-vst",
"vd-protodune-pds",
"fardet-hd",
"fardet-vd",
"dc4-vd-coldbox-bottom",
"dc4-vd-coldbox-top",
"dc4-hd-protodune",
"hd-protodune"
]

run_types = clean("run_type",run_types,1000)
print ("run_types",run_types)

data_streams = ["ALL",
"out1",
"noise",
"test",
"cosmics",
"calibration",
"physics",
"commissioning",
"out2",
"pedestal",
"study"
]

data_streams = clean("data_stream",data_streams,1000)
# range
print ("data_streams",data_streams)
det_types = ["detector","mc"]
first = "2017-01-01"
last = "2025-01-01"
if len(sys.argv) > 1:
  first = sys.argv[1]
if len(sys.argv) > 2:
  last = sys.argv[2]

out = open("data_tier_%s_%s.txt"%(first,last),'w')

obsolete = {"raw":"(run_type protodune-sp and run_number<5141)"}


head =  "%s\t%10s\t%20s\t%20s\t%20s\t%s\t%s\t%s\tTB\t%s\tMB\n"%("year","det/mc","expt","stream","tier","files","events","size","size/event")
out.write(head)
print(head)
file_count = 0
for year in [2018,2019,2020,2021,2022,9999]:
    if year != "9999":
        first ="%d-01-01"%year
        last = "%d-12-31"%year
    else:
        first ="2018-01-01"
        last = "2022-12-31"
    for dtype in det_types:
        for tier in data_tiers:
            for rtype in run_types:
                for stream in data_streams:
                    command = ""
                    command += "data_tier "+tier
                    command += " and file_type " + dtype
                    command += " and run_type " + rtype
                    command += " and create_date >= " + first
                    command += " and create_date <= " + last
                    command += " and data_stream " + stream
                    command = command.replace("ALL","%")
                    print ("Command: ",command)
                    result = samweb.listFilesSummary(command)
                      #print (result)

                    file_count = result["file_count"]
                    if stream == "ALL" and file_count == 0:
                        sresult = "%d\t%10s\t%20s\t%20s\t%20s\t%d\t%d\t%6.3f\tTB\t%6.3f\tMB\n"%(year,dtype,rtype,stream,tier,0,0,0,0)
                        out.write(sresult)
                        print (sresult)
                        print ("giving up as no files",dtype,tier,rtype,stream,file_count)
                        break
                    if file_count == 0:
                        sresult = "%d\t%10s\t%20s\t%20s\t%20s\t%d\t%d\t%6.3f\tTB\t%6.3f\tMB\n"%(year,dtype,rtype,stream,tier,0,0,0,0)
                        out.write(sresult)
                        print (sresult)
                        continue
                    events = result["total_event_count"]
                    ssize = result["total_file_size"]/1000/1000/1000/1000.
                    if events != None:
                        fsize = result["total_file_size"]/1000/1000/events
                    else:
                        events = 0
                        fsize = -1
                    sresult = "%d\t%10s\t%20s\t%20s\t%20s\t%d\t%d\t%6.3f\tTB\t%6.3f\tMB\n"%(year,dtype,rtype,stream,tier,file_count,events,ssize,fsize)
                    out.write(sresult)
                    print (sresult)
                if rtype == "ALL" and stream == "ALL" and file_count == 0:
                    print ("giving up as no files",dtype,tier,rtype,stream,file_count)
                    break
            if tier == "ALL" and rtype == "ALL" and stream == "ALL" and file_count == 0:
                print ("giving up as no files",dtype,tier,rtype,stream,file_count)
                break

out.close()
#  out.write(divide)
