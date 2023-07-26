import sys,os,json,datetime

if len(sys.argv) <2:
    print ("need name of json file to convert to dataset template")
    sys.exit(1)
inputname = sys.argv[1]
f = open(inputname,'r')
m = json.load(f)
require = [
  "user",
  "dune.campaign",
  "dune.requestid",
  "core.run_type",
  "core.data_tier",
  "core.file_type",
  "dune_mc.beam_flux_ID",
  "dune_mc.beam_polarity",
  "dune_mc.electron_lifetime",
  "dune_mc.gen_fcl_filename",
  "dune_mc.mixerconfig"]

result = m.copy()
for r in m.keys():
    if r not in require:
        result.pop(r)
now = datetime.datetime.now()
date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
result["Comment"]="Created by DatasetJsonMaker by %s on %s"%(os.getenv("USER"),date_time)
print(result)
dname = result["dune_mc.gen_fcl_filename"].replace(".fcl",".dataset.json")
g = open(dname,'w')
json.dump(result,g,indent=4)
