#fill in yoda histogram with nanoAOD
import uproot
import yoda
import sys
import numpy as np
import awkward as ak
import json
from collections import OrderedDict

#helper function for reading json and converting keys to integers
def keysToInt(x):
  od = OrderedDict()
  for k, v in x:
    od[int(k)] = v
  return od

from optparse import OptionParser
parser = OptionParser(usage="%prog input.root output.yoda")
parser.add_option("--tag-branch", dest="tag_branch", default="HTXS_stage1_2_cat_pTjet30GeV",
                  help="Specify the branch used to tag the events, e.g. HTXS_stage1_2_cat_pTjet30GeV")
parser.add_option("--inclusive", dest="inclusive", default=False, action="store_true",
                  help="Dump all events into a single bin. Do no splitting by e.g. STXS bin.")
parser.add_option("--tag-branch2", dest="tag_branch2", default=None,
                  help="Specify a second tag branch so the events will be binned by branch1 x branch2")
parser.add_option("--weight-branch", dest="weight_branch", default=None,
                  help="By default, standalone reweighting using the 'genWeight' branch as the original weights to scale. Use this option to specify a different branch to act as the original weight.")
parser.add_option("--keys", dest="keys", default=None,
                   help="Comma seperated tagKey.json files for tag-branch and tag-branch2. Used to make a new key file for tag-branch * tag-branch2.")
parser.add_option("--key-output", dest="key_output", default=None, 
                   help="Output for new key file from combination of tag-branch and tag-branch2, e.g. new_key.json")

(options, args) = parser.parse_args()

if len(args) < 2:
  parser.print_help()
  sys.exit(1)
filename = args[0]
outname = args[1]

if options.keys is not None:
  options.keys = options.keys.split(",")
  if len(options.keys) != 2:
    print("Must have two key files (one for each tag branch)")
    parser.print_help()
    sys.exit(1)
  else:
    #try reading in keys
    try:
      with open(options.keys[0], "r") as f:
        t1_key = json.loads(f.read(), object_pairs_hook=keysToInt)
      with open(options.keys[1], "r") as f:
        t2_key = json.loads(f.read(), object_pairs_hook=keysToInt)
      options.keys = [t1_key, t2_key]
    except:
      print("Failed to read in the tagKey.json files. Will not output a new_key.json file.")
      options.key_output = None

#open nanoAOD 
f = uproot.open(filename)
print("Reading in reweights")
reweights=f["Events"]["Reweights"].array(library='np')

#if using different original weight, find scaling and apply to new original weights
if options.weight_branch is not None:
  original_weights = f["Events"][options.weight_branch].array(library='np')
  sf = reweights / reweights[:,0,np.newaxis]
  reweights = sf * original_weights[...,np.newaxis]

#if using a single bin, tag every event with 0
if options.inclusive:
  tag = np.zeros(len(reweights))
else:
  print("Reading in tag")
  tag=f["Events"][options.tag_branch].array()

  #if using >1 tag, create new tag from combination of tag1 and tag2
  if options.tag_branch2 is not None:
    print("Reading in tag2")
    tag2 = f["Events"][options.tag_branch2].array(library='np')
    
    #if don't have keys, find range of tag2 from nanoAOD, then calculate new tag
    if len(options.keys) != 2:
      n_tags2 = max(tag2) - min(tag2) + 1
      new_tag = (tag * n_tags2) + tag2

    else:
      t1_key = options.keys[0]
      t2_key = options.keys[1]
      
      #find range from key dictionaries (may be bigger than in nanoAOD)
      n_tags2 = max(t2_key.keys()) - min(t2_key.keys()) + 1
      new_tag = (tag * n_tags2) + tag2

      assert max(tag) <= max(t1_key.keys())
      assert min(tag) >= min(t1_key.keys())
      assert max(tag2) <= max(t2_key.keys())
      assert min(tag2) >= min(t2_key.keys())

      #create a new key for new tag
      print("Creating new key")
      if options.key_output is not None:
        new_key = OrderedDict()
        for t1 in t1_key.keys():
          for t2 in t2_key.keys():
            new_name = t1_key[t1] + "__" + t2_key[t2]
            new_key[(t1*n_tags2) + t2] = new_name

        print("Writing new key")
        with open(options.key_output, "w") as f:
          f.write(json.dumps(new_key, indent=4))

    tag = new_tag 

n_events = len(reweights)
n_rw = len(reweights[0])
n_pars = int((-3 + np.sqrt(9+8*(n_rw-1)))/2)

hists = []
max_i = max(tag)
min_i = min(tag)
#min_i = 1
#max_i = 79
for i in range(n_rw):
  hists.append(yoda.Histo1D(max_i-min_i+1, min_i, max_i+1, "/MyHist[rw%.4i]"%i))

for i in range(n_events):
  if (i%10000 == 0):
    print("Processed %d/%d events"%(i, n_events))
  inw = reweights[i]
  out = inw.copy()
  for ip in range(n_pars):
    s0 = inw[0]
    s1 = inw[ip*2 + 1]
    s2 = inw[ip*2 + 2]
    s1 -= s0
    s2 -= s0
    Ai = 4. * s1 - s2
    Bii = s2 - Ai

    out[ip*2 + 1] = Ai
    out[ip*2 + 2] = Bii
 
  crossed_offset = 1 + 2*n_pars
  c_counter = 0
  for ix in range(n_pars):
    for iy in range(ix+1, n_pars):
      s = inw[crossed_offset + c_counter]
      sm = inw[0]
      sx = out[ix*2 + 1]
      sy = out[iy*2 + 1]
      sxx = out[ix*2 + 2]
      syy = out[iy*2 + 2]
      s -= (sm + sx + sy + sxx + syy)
      out[crossed_offset + c_counter] = s
      c_counter += 1

  for j in range(n_rw):
    hists[j].fill(tag[i], out[j])  
print("Processed all events")
yoda.write(hists, outname)

