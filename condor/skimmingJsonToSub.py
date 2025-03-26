import json
import os
from collections import OrderedDict
from optparse import OptionParser

parser = OptionParser(usage="%prog [options] jobs.json AFS_dir")
parser.add_option("--JobFlavour", dest="JobFlavour", default="espresso", help="Job flavour for condor submission")
(options, args) = parser.parse_args()

job_json = args[0]
afs_dir = args[1]
proxy_path = os.path.abspath(args[2])

nanoAODTools_dir = os.getcwd()

with open(job_json, "r") as f:
  jobs = json.loads(f.read(), object_pairs_hook=OrderedDict)

#will need to dump all condor stuff to an AFS directory
os.system("mkdir -p %s"%afs_dir)
os.system("mkdir -p %s/log"%afs_dir) 
os.system("mkdir -p %s/output"%afs_dir) 
os.system("mkdir -p %s/error"%afs_dir) 

#transfer executable
os.system("cp condor/skimming_executable.sh %s/"%afs_dir)

sub = ""

sub += "executable = %s/skimming_executable.sh \n"%afs_dir
sub += "arguments = %s $(dataset) $(csv) $(output_root) $(extraBranches) $(extraCollections) $(doTest) $(keepNoTag) $(NoTagIndex) $(inclusiveSample) %s $(ClusterId) $(ProcId) \n"%(nanoAODTools_dir, proxy_path)
sub += "output = %s/output/rw.$(ClusterId).$(ProcId).out \n"%afs_dir
sub += "error = %s/error/rw.$(ClusterId).$(ProcId).err \n"%afs_dir
sub += "log = %s/log/rw.$(ClusterId).log \n\n"%afs_dir

sub += '+JobFlavour = "%s"\n'%(options.JobFlavour)

for job in jobs:
  sub += "dataset = %s \n"%job['dataset']
  sub += "csv = %s \n"%job['csv']
  sub += "output_root = %s \n"%job['output']
  sub += "extraBranches = %s \n"%job['extraBranches']
  sub += "extraCollections = %s \n"%job['extraCollections']
  sub += "doTest = %s \n"%job['test']
  sub += "keepNoTag = %s \n"%job['keepNoTag']
  sub += "NoTagIndex = %s \n"%job['NoTagIndex']
  sub += "inclusiveSample = %s \n"%job['inclusiveSample']
  
  sub += "queue \n\n"

with open("%s/submit.sub"%afs_dir, "w") as f:
  f.write(sub)

