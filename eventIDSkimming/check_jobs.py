"""Recursively searches directory for root files and checks they are not empty"""

import os
import sys
import uproot

input_dir = sys.argv[1]

os.system('find %s -name "*.root" > ${TMPDIR}/root_file_search.txt'%input_dir)
with open(os.path.join(os.getenv("TMPDIR"), "root_file_search.txt"), "r") as f:
  root_files = f.read().split("\n")

for root_file in root_files:
  if root_file == "": continue
  f=uproot.open(root_file)
  okay = f.keys() != []

  if okay:
    print("%s: \033[92m okay \033[0m"%root_file)
    print(" %.3fk events"%(float(len(f["Events"]))/1000))
  else:
    print("%s: \033[91m fail \033[0m"%root_file)
