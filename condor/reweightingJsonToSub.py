import json
import os
from collections import OrderedDict
from optparse import OptionParser

parser = OptionParser(usage="%prog [options] jobs.json AFS_dir")
parser.add_option("--JobFlavour", dest="JobFlavour", default="espresso", help="Job flavour for condor submission")
(options, args) = parser.parse_args()

job_json = args[0]
afs_dir = args[1]

nanoAODTools_dir = os.getcwd()

with open(job_json, "r") as f:
  jobs = json.loads(f.read(), object_pairs_hook=OrderedDict)

#will need to dump all condor stuff to an AFS directory
os.system("mkdir -p %s"%afs_dir)
os.system("mkdir -p %s/log"%afs_dir) 
os.system("mkdir -p %s/output"%afs_dir) 
os.system("mkdir -p %s/error"%afs_dir) 

#transfer executable
os.system("cp condor/reweighting_executable.sh %s/"%afs_dir)

sub = ""

sub += "executable = %s/reweighting_executable.sh \n"%afs_dir
sub += "arguments = %s $(outDir) $(in_file) $(rw_path) $(start) $(entries) $(method) $(ClusterId) $(ProcId) \n"%nanoAODTools_dir
sub += "output = %s/output/rw.$(ClusterId).$(ProcId).out \n"%afs_dir
sub += "error = %s/error/rw.$(ClusterId).$(ProcId).err \n"%afs_dir
sub += "log = %s/log/rw.$(ClusterId).log \n\n"%afs_dir

sub += '+JobFlavour = "%s"\n'%(options.JobFlavour)

for job in jobs:
  sub += "outDir = %s \n"%job['outdir']
  sub += "rw_path = %s \n"%job['rw_path']
  sub += "in_file = %s \n"%job['infile']
  sub += "start = %s \n"%job['firstEntry']
  sub += "entries = %s \n"%job['maxEntries']
  sub += "method = %s \n"%job['method']
  sub += "queue \n\n"

with open("%s/submit.sub"%afs_dir, "w") as f:
  f.write(sub)

