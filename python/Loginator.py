""" Art logfile parser
H. Schellman - 2022

"""
##
# @mainpage Loginator.py
#
# @section description_main Description
# A program for parsing art logs to put information into DUNE job monitoring.
#
#
##
# @file Loginator.py

import string,time,datetime,json,os,sys

import dbparse

## try to set up samweb if available
if "SAM_EXPERIMENT" in os.environ:
    import samweb_client


from metacat.webapi import MetaCatClient
import string,datetime
from datetime import date,timezone,datetime





##  Loginator class should not care what access method you are using

class Loginator:
    """
    Art Logfile parser that assembles a file by file json record for use with elasticsearch
    """
## initialization, requires an Art logfile to parse and creates a template json file

    def __init__(self,logname=None,fcl=None,debug=False):
        """
        :param logname: name of the art logfile to read
        :type logname: str
        :param debug: turn on debug printout
        :type debug: bool
        """

        if not os.path.exists(logname):
            print ("no such file exists, quitting",logname)
            sys.exit(1)
        self.logname = logname
        self.debug = debug
        print ("Loginator debug:",self.debug)
        self.logfile = open(logname,'r')
        if fcl != None: 
            self.fclname = os.path.basename(fcl).replace(".fcl","")
        else: 
            self.fclname = "nofcl"
        self.errfile = open(logname.replace('.out','.err'),'r')
        self.outobject ={}
        self.info = self.getsysinfo()
        self.tags = ["%MSG-i MF_INIT_OK:  Early ","Opened input file", "Closed input file","MemReport  VmPeak","CPU","Events total","Initiating request to open input file"]
        self.template = {
             # job attributes
            "user":None,  # (who's request is this)
            "job_id":None, # (jobsubXXX03@fnal.gov)
            "job_node":None,  # (name within the site)
            "job_site":None,  # (name of the site)
            "country":None,  # (nationality of the site)
            "art_real_memory":None,
            "timestamp_for_job_start":"",
            "timestamp_for_art_start":"",
            "startup_time":0.0,
            "art_wall_time":None,
            "art_cpu_time":None,
            "art_total_events":None,
            "art_cpu_time_per_event":-1.,
            "art_wall_time_per_event":-1.,
            "art_cpu_efficiency":-1.,
            "project_id":0,
            "delivery_method":None, #(samweb/dd/wfs)
            "workflow_method":None,
            "access_method":None, #(stream/copy)
            "timestamp_for_request":None,
            "timestamp_for_start":None,  #
            "timestamp_for_end":None,  #
            "application_family":None,  #
            "application_name":None,  #
            "application_version":None, 
            "fcl":self.fclname, #
            "final_state":None,  # (what happened?)
            "project_name":None, #(wkf request_id?)"
            "duration":None,  # (difference between end and start)
            "path":None,
            "rse":None,
            "preference":None,
            # file attributes from metacat
            "file_size":None,  #
            "file_type":None,  #
            "file_name":None,  # (not including the metacat namespace)
            "fid":None, # metacat fid
            "data_tier":None,  # (from metacat)
            "data_stream":None,
            "run_type":None,
            "file_format":None,
            "file_campaign":None,  # (DUNE campaign)
            "namespace":None,
            "event_count":None,
            "mips":None,
            "vendor":None
        }



    def setDebug(self,debug=False):
        self.debug = debug

    ## utility to print the environment
    def envPrinter(self):
        env = os.environ
        for k in env:
            print ("env ",k,"=",env[k])


## look at a line of text and find the first tag from self.tags in the line
    def findme(self,line):
        """
        Check to see if one of the tags is in a given line of the log
        """
        for tag in self.tags:
            if tag in line:
                if self.debug: print (tag,line)
                return tag
        return None

## safe access for a dictionary element, returns None rather than failing
    def getSafe(self,dict,envname):
        if envname in dict:
            if self.debug: print ("found ",envname)
            return dict[envname]
        else:
            return None



    def getsysinfo(self):
        """ get system info for the running process, shared with all files processed """
        info = {}
        # get a bunch of system thingies.
        if os.getenv("GRID_USER") != None:
            info["user"]=os.getenv("GRID_USER")
        else:
            info["user"]=os.getenv("USER")
        
        if os.getenv("poms_data") != None:
            poms_data = os.getenv("poms_data")
            if poms_data != None:
                poms_dict=json.loads(poms_data)
                if "bogomips" in poms_dict:
                    info["mips"] = poms_dict["bogomips"]
                if "vendor_id" in poms_dict:
                    info["vendor"] = poms_dict["vendor_id"]
        info["job_id"] = self.getSafe(os.environ,"JOBSUBJOBID")
        info["job_node"] = self.getSafe(os.environ,"NODE_NAME")
        #info["job_node"] = os.getenv("HOST")
        if "GLIDEIN_DUNESite" in os.environ:
            info["job_site"] = os.getenv("GLIDEIN_DUNESite")
        elif "GLIDEIN_Entry_Name" in os.environ:
            info["job_site"]=os.getenv("GLIDEIN_Entry_Name")
        else:
            info["job_site"]=self.getSafe(os.environ,"NODE_NAME")
        return info

    def addsysinfo(self):
        """## add system info to the record"""
        self.addinfo(self.getsysinfo())

    def readme(self):
        """ read in the log file and parse it
            lines with specific tags get processes while others are skipped
        """
        object = {}
        memdata = None
        cpudata = None
        walldata = None
        totalevents = None
        larstart = None
        for line in *self.logfile,*self.errfile:
            tag = self.findme(line)
            if self.debug and tag != None: print (tag,line)

            # not relevant, skip
            if tag == None:
                continue

            # find the job start
            if "Early" in tag:
                part = line.split(tag)[1]
                part = part.split(" JobSetup")[0]
                larstart = part
            # memory from end of job
            if "MemReport  VmPeak" == tag:
                memdata = float(line.split("VmHWM = ")[1].strip())

            # cpu/walltime from end of job
            if "CPU" == tag:
                timeline = line.strip().split(" ")
                if len(timeline) < 7:
                    continue
                cpudata = float(timeline[3])
                walldata = float(timeline[6])

            # total events processedf from end of job
            if "Events total" in tag:
                eventline  = line.strip().split(" ")
                if len(eventline) < 11:
                    continue
                totalevents = int(eventline[4])

            # file request/open/close activities
            if "file" in tag:
                data = line.split(tag)
                filefull = data[1].strip().replace('"','')
                timestamp = data[0].strip()
                filename = os.path.basename(filefull).strip()
                filepath = os.path.dirname(filefull).strip()

                dups = 0

                # start - ask for file
                if "Initiating" in tag:
                    localobject = self.template.copy()
                    localobject["final_state"] = "Started"
                    localobject["timestamp_for_request"] = timestamp
                    localobject["final_state"] = "Requested"
                    localobject["path"]=filepath
                    localobject["file_name"] = filename
                    localobject["url"] = filefull
                    if larstart == None:  # somehow we didn't start quite right
                    	larstart = timestamp
                    if "BEGIN_TIME" in os.environ:
                        localobject["timestamp_for_job_start"]=os.getenv("BEGIN_TIME")
                    else:
                        localobject["timestamp_for_job_start"] = larstart
                    localobject["timestamp_for_art_start"]=larstart
                    localobject["startup_time"]=self.duration(localobject["timestamp_for_job_start"],larstart)
                    if "root" in filepath[0:10]:
                        if self.debug: print ("I am root")
                        tmp = filepath.split("//")
                        localobject["rse"] = tmp[1]
                        localobject["access_method"] = "xroot"
                    for thing in self.info:
                        localobject[thing] = self.info[thing]
                    if self.debug: print ("localobject",localobject)
                # open the file
                if "Opened" in tag:


                    if self.debug: print ("filename was",filename,line)
                    localobject["timestamp_for_start"] = timestamp
                    start = timestamp
                    localobject["path"]=filepath
                    localobject["file_name"] = filename
                    if self.debug: print ("filepath",filepath)
                    if "root" in filepath[0:10]:
                        if self.debug: print ("I am root")
                        tmp = filepath.split("//")
                        localobject["rse"] = tmp[1]
                        localobject["access_method"] = "xroot"
                    for thing in self.info:
                        localobject[thing] = self.info[thing]
                    localobject["final_state"] = "Opened"

                # Close the file
                if "Closed" in tag:
                    localobject["timestamp_for_end"] = timestamp
                    localobject["duration"]=self.duration(localobject["timestamp_for_request"],timestamp)
                    localobject["final_state"] = "Closed"

                object[filename] = localobject
                continue


        # add the job info to all file records if available
        localinfo = self.dbread()
        for thing in object:
            
            if memdata != None: object[thing]["art_real_memory"]=memdata
            if "memory" in localinfo: object[thing]["db_real_memory"]=localinfo["memory"]
            if "n_events" in localinfo: object[thing]["db_total_events"]=localinfo["n_events"]
            if walldata != None: object[thing]["art_wall_time"]=walldata
            if "wall_time" in localinfo: object[thing]["db_wall_time"]=localinfo["wall_time"]
            if cpudata != None: object[thing]["art_cpu_time"]=cpudata
            if totalevents != None:
                object[thing]["art_total_events"]=totalevents
                if totalevents > 0:
                    object[thing]["art_cpu_time_per_event"] = cpudata/totalevents
                    object[thing]["art_wall_time_per_event"] = walldata/totalevents
            if walldata  != None and walldata > 0:
                object[thing]["art_cpu_efficiency"] = cpudata/walldata

            #print ("mem",object[thing]["real_memory"])
        self.outobject=object

    def addinfo(self,info):
        """  add information from a dictionary to the record"
        :param info: Dictionary with list of items to add the the output record
        :type info: {}
        """

        for s in info:
            if s in self.outobject:
                print ("Loginator.addinfo replacing",s, self.outobject[s],self.info[s])
            else:
                for f in self.outobject:
                    self.outobject[f][s] = info[s]
                    if self.debug: print ("adding",s,info[s])


    def addsaminfo(self):
        ''' add input file information from sam to the record
            need to check that sam is actually available
        '''
        if "SAM_EXPERIMENT" in os.environ:
            import samweb_client
        else:
            print ("You need to set up samweb to get sam info")
            sys.exit(0)
        samweb = samweb_client.SAMWebClient(experiment='dune')
        for f in self.outobject:
            if self.debug: print ("f ",f)
            meta = samweb.getMetadata(f)
            self.outobject[f]["namespace"]="samweb"
            self.outobject[f]["delivery_method"]="samweb"
            for item in ["event_count","data_tier","file_type","data_stream","file_size","file_format"]:
                self.outobject[f][item]=meta[item]
            if "DUNE.campaign" in meta:
                self.outobject[f]["file_campaign"] = meta["DUNE.campaign"]
            for run in meta["runs"]:
                self.outobject[f]["run_type"] = run[2]
                break


    def addmetacatinfo(self,defaultNamespace=None):
        """add file information from metacat to the record
        the defaultNamespace argument is just there for testing
        """
        if self.debug:print ("add metacat info")
        #os.environ["METACAT_SERVER_URL"]="https://metacat.fnal.gov:9443/dune_meta_demo/app"
        mc_client = MetaCatClient(os.getenv("METACAT_SERVER_URL"))
        
        for f in self.outobject:
            if "namespace" in self.outobject[f] and self.outobject[f]["namespace"] != None:
                namespace = self.outobject[f]["namespace"]
            else:
                print ("set default namespace for file",f,defaultNamespace)
                namespace = defaultNamespace
                if namespace == None:
                    print (" could not set namespace for",f)
                    continue
            if self.debug: print ("get metadata for ", f,namespace)
            try:
                meta = mc_client.get_file(name=f,namespace=namespace)
                print ("got metadata",f, namespace, meta)
                
            except:
                print ("metacat access failure for file",f)
                self.outobject[f]["metacat_status"]="failed"
                meta = None
            if self.debug: print ("metacat answer",f,namespace,meta)
            if meta == None:
                print ("no metadata for",f)
                continue
            self.outobject[f]["metacat_status"]="success"
            self.outobject[f]["delivery_method"]="dd"
            for item in ["data_tier","file_type","data_stream","run_type","event_count","file_format"]:
                if "core."+item in meta["metadata"].keys():
                    self.outobject[f][item]=meta["metadata"]["core."+item]
                else:
                    print ("addmetacatinfo: no", item, "in ",list(meta["metadata"].keys()))
            self.outobject[f]["file_size"]=meta["size"]
            if "DUNE.campaign" in meta["metadata"]:
                self.outobject[f]["file_campaign"]=meta["metadata"]["DUNE.campaign"]
            self.outobject[f]["fid"]=meta["fid"]
            self.outobject[f]["namespace"]=namespace


    def addreplicainfo(self,replicas=None,flist=[],test=False):
        """
        get some details from the data dispatcher on file locations
        :param replicas: dictionary with lists of replicas for each file from the dd
        :type replicas: {}
        :return: list of file did's that were in the replicas list but not found in the parsed logs
        :rtype: [str]
        """
        if self.debug:  print (" add replica info")
        notfound = []
        for f in self.outobject:
            self.outobject[f]["rse"] = None

        # do this if just a file list
        
        print ("outobject", self.outobject)
        if replicas == None:
            # this is a file list
            filelist = flist.split(" ")
            print ("flist",filelist)
            fullpath=""
            for files in filelist:
                r = os.path.basename(files)
                found = False
                for f in self.outobject:
                    print ('outfile',f)
                    fpath = os.path.join(self.outobject[f]["path"],f)
                    if self.debug: print ("RSECHECK1",fullpath,"\nRSECHECK2",fpath)
                    if r in fpath:
                        if self.debug: print ("replica match",r)
                        if self.outobject[f]["final_state"] in ["Closed"]:
                            found = True
                        else:
                            print ("File found but not closed, flag as failed",f)
                        if "rse" in r:
                            self.outobject[f]["rse"] = r["rse"]
                        if "namespace" in r:
                            self.outobject[f]["namespace"] = r["namespace"]
                        if "preference" in r:
                            self.outobject[f]["preference"] = r["preference"]
                    if self.debug: print (self.outobject[f])
                if not found:
                    print (r,"appears in replicas but not in Lar Log, need to mark as unused")
                    notfound.append(r)
            return notfound


        # do this for rucio replica list
        for r in replicas:
            found = False
            fullpath = r["url"]
            for f in self.outobject:
                fpath = os.path.join(self.outobject[f]["path"],f)
                if self.debug: print ("RSECHECK1",fullpath,"\nRSECHECK2",fpath)
                if fullpath == fpath:
                    if self.debug: print ("replica match",r)
                    if self.outobject[f]["final_state"] in ["Closed"]:
                        found = True
                    else:
                        print ("File found but not closed, flag as failed",f)
                    if "rse" in r:
                        self.outobject[f]["rse"] = r["rse"]
                    if "namespace" in r:
                        self.outobject[f]["namespace"] = r["namespace"]
                    if "preference" in r:
                        self.outobject[f]["preference"] = r["preference"]
                if self.debug: print (self.outobject[f])
            if not found:
                print (r,"appears in replicas but not in Lar Log, need to mark as unused")
                notfound.append(r)

        return notfound

    def writeme(self):
        """ dump info to json file """
        result = []
        for thing in self.outobject:
            if self.debug: print ("writeme", thing,self.outobject[thing])
            outname = "%s_%s_%d_process.json" %(thing,self.fclname,self.outobject[thing]["project_id"])
            outfile = open(outname,'w')
            json.dump(self.outobject[thing],outfile,indent=4)

            outfile.close()
            result.append(outname)
        return result

## utility to parse timestamps
    def human2number(self,stamp):
        #15-Nov-2022 17:24:41 CST https://docs.python.org/3/library/time.html#time.strftime
        format = "%d-%b-%Y %H:%M:%S"
        # python no longer accepts time zones.  We only want the different but need to correct for DT
        #print ("human2number converting",stamp)
        if self.debug: print ("raw time", stamp, stamp[0:20], datetime.strptime(stamp[0:20],format))
        thetime  = datetime.strptime(stamp[0:20],format)
        epoch = datetime.utcfromtimestamp(0)
        delta = 0
        if "DT" in stamp:
            delta = 3600
        return (thetime-epoch).total_seconds() + delta

## utility to change timestamps into time delta
    def duration(self,start,end):
        t0 = self.human2number(start)
        t1 = self.human2number(end)
        if self.debug: print("duration", start, end, t0, t1, t1-t0)
        return t1-t0
        
    def dbread(self):
        if self.debug: print("try to access the time and memory databases")
        localinfo = {}
        try:
            mem = dbparse.getme("mem.db", "peak-summary.sql")
            time = dbparse.getme("time.db", "event-summary.sql")
            localinfo["memory"]=int(mem['Peak resident set size (MB)'])
            localinfo["wall_time"] = int(time['Full Event'][1]*time['Full Event'][3])
            localinfo["n_events"] = time['Full Event'][3]
            if self.debug: print ("db info",localinfo)
        except:
            print ("Can't get mem/time info from db")
        return localinfo



def test():
    """ test the Loginator """

    parse = Loginator(logname=sys.argv[1],debug=True)
    if len(sys.argv)>2:
        namespace = sys.argv[2]
    else:
        namespace = None
    #print ("looking at",sys.argv[1])
    print ("namespace",namespace)
    parse.readme()
    parse.addsysinfo()
    parse.addreplicainfo(replicas=[])
    if "SAM_EXPERIMENT" in os.environ and namespace==None:
        parse.addsaminfo()
    else:
        parse.addmetacatinfo(namespace)
            #parse.addmetacatinfo("dc4-hd-protodune") # argument is there for testing when you don't have replica list.
    parse.writeme()


if __name__ == '__main__':
    print (" Loginator needs to know the namespace for the input files as arg 2")
    test()
