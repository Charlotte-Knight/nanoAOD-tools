import uproot
import numpy as np
import json
from collections import OrderedDict
import os
import sys

def tqdm(iterable):
  for i, item in enumerate(iterable):
    j = i + 1
    sys.stdout.write('\r'+"%d/%d"%(j, len(iterable)))
    sys.stdout.flush()
    if j == len(iterable): print("")
    yield item

#def getTerms(sm, rw1, rw2, x):
#  """
#  Derive A and B coefficients for scaling equation.
#  sm: array of event weights at SM benchmark
#  rw1: array of event reweights at C=x/2
#  rw2: array of event reweights at C=x
#  """
#  mu1 = sum(rw1)/sum(sm)
#  mu2 = sum(rw2)/sum(sm)
#  A = (4*mu1 - mu2 -3)/x
#  B = (mu2 - 1 - A*x)/x**2
#
#  return A, B
#
#def getCrossTerm(sm, rw, A1, B1, A2, B2, x): 
#  """
#  Derive B_ij cross term for scaling equation.
#  sm: array of event weights at SM benchmark
#  rw: array of event reweights at C1=x C2=x
#  A1, B1, A2, B2: linear and quad scaling eqn coefficients for C1 and C2
#  """
#  mu = sum(rw)/sum(sm)
#  B12 = (mu - 1 - A1*x - B1*x**2 - A2*x - B2*x**2) / x**2
#  return B12

def getTerms(mu1, mu2, x):
  """
  Derive A and B coefficients for scaling equation.
  sm: array of event weights at SM benchmark
  rw1: array of event reweights at C=x/2
  rw2: array of event reweights at C=x
  """
  A = (4*mu1 - mu2 -3)/x
  B = (mu2 - 1 - A*x)/x**2

  return A, B

def getCrossTerm(mu, A1, B1, A2, B2, x):
  """
  Derive B_ij cross term for scaling equation.
  sm: array of event weights at SM benchmark
  rw: array of event reweights at C1=x C2=x
  A1, B1, A2, B2: linear and quad scaling eqn coefficients for C1 and C2
  """
  B12 = (mu - 1 - A1*x - B1*x**2 - A2*x - B2*x**2) / x**2
  return B12


def processConfig(config_path):
  with open(config_path, "r") as f:
    config_dict = json.load(f)

  def_val = config_dict['parameter_defaults']['val']
  params = [param['name'] for param in config_dict['parameters']]
  return def_val, params

#helper function for reading json and converting keys to integers
def keysToInt(x):
  od = OrderedDict()
  for k, v in x:
    od[int(k)] = v
  return od

def getKeys(options):
  key, key2 = None, None

  if options.key != None:
    with open(options.key, "r") as f:
      key = json.load(f, object_pairs_hook=keysToInt)
  if options.key2 != None:
    with open(options.key2, "r") as f:
      key2 = json.load(f, object_pairs_hook=keysToInt)

  return key, key2

def readNanoFile(nano_file, options, key, key2):
  f = uproot.open(nano_file)["Events"]

  reweights = f["Reweights"].array()
  if options.weight_branch != None:
    original_weights = f[options.weight_branch].array()
    sf = reweights / reweights[:,0,np.newaxis]
    reweights = sf * original_weights[...,np.newaxis]

  if options.inclusive:
    return reweights, np.ones(len(reweights)), {1.0: "inclusive"}

  tag_branch = f[options.tag_branch].array()
  if key == None:
    key = {}
    for i in np.unique(tag_branch):
      key[i] = str(i)

  if options.stage0 != None:
    #rebin to stage0
    tags = [k for k in key.keys() if ((options.stage0 in key[k]) and ("FWDH" not in key[k]))] #all keys corresponding to stage0 process which are not FWDH
    selection = np.isin(tag_branch, tags)
    return reweights[selection], np.ones(len(reweights[selection])), {1.0: options.stage0}

  if options.tag_branch2 == None:
    return reweights, tag_branch, key
  else:
    tag_branch2 = f[options.tag_branch2].array()
    if key2 == None:
      key2 = {}
      for i in np.unique(tag_branch2):
        key2[i] = str(i)

    max_tag_2 = max(tag_branch2)
    min_tag_2 = min(tag_branch2)
    spacing = max_tag_2 - min_tag_2 + 1

    new_tag_branch = tag_branch*spacing + (tag_branch2-min_tag_2)
    new_key = OrderedDict()
    for i in np.unique(tag_branch):
      for j in np.unique(tag_branch2):
        new_key[(i*spacing) + (j-min_tag_2)] = "%s__%s"%(key[i], key2[j])

    return reweights, new_tag_branch, new_key  

def deriveEqns(reweights, tag_branch, key, params, def_val):
  eqns = OrderedDict()
  
  rws = {}
  for i in np.unique(tag_branch):
    rws[i] = reweights[tag_branch==i]
  
  for i in tqdm(np.unique(tag_branch)):
    new_eqn = OrderedDict()

    rw = rws[i]
    n_events = len(rw)
    
    new_eqn["N_Events"] = n_events

    sm = rw[:,0].sum()
    for j in range(len(params)):
      mu1 = rw[:,j*2+1].sum() / sm
      mu2 = rw[:,j*2+2].sum() / sm
      A, B = getTerms(mu1, mu2, def_val)
      
      new_eqn["A_%s"%params[j]] = float(A)
      new_eqn["B_%s_2"%params[j]] = float(B)

    ic = 0
    for j in range(len(params)):
      for k in range(j+1, len(params)):
        A1, B1, A2, B2 = new_eqn["A_%s"%params[j]], new_eqn["B_%s_2"%params[j]], new_eqn["A_%s"%params[k]], new_eqn["B_%s_2"%params[k]], 
        mu = rw[:,1+(len(params)*2) + ic].sum() / sm
        B = getCrossTerm(mu, A1, B1, A2, B2, def_val)
        new_eqn["B_%s_%s"%(params[j], params[k])] = B
        ic += 1

    eqns[key[i]] = new_eqn
  return eqns  

def cleanUp(eqns, options):
  for tag in eqns.keys():
    params = eqns[tag].keys()
    params = filter(lambda x: x[0] != "u", params)
    
    for param in params:
      if abs(eqns[tag][param]) < options.absolute_threshold:
        del eqns[tag][param]
        del eqns[tag]["u_"+param]
  return eqns

def getOptions():
  from optparse import OptionParser
  parser = OptionParser(usage="%prog EFT2Obs_config.json inputFile1 inputFile2... [options] ")
  parser.add_option("--tag-branch", dest="tag_branch", default="HTXS_stage1_2_cat_pTjet30GeV",
                    help="Specify the branch used to tag the events, e.g. HTXS_stage1_2_cat_pTjet30GeV")
  parser.add_option("--tag-branch2", dest="tag_branch2", default=None,
                    help="Specify a second tag branch so the events will be binned by branch1 x branch2")
  parser.add_option("--inclusive", dest="inclusive", default=False, action="store_true",
                    help="Dump all events into a single bin. Do no splitting by e.g. STXS bin.")
  
  parser.add_option("--weight-branch", dest="weight_branch", default=None,
                    help="By default, standalone reweighting using the 'genWeight' branch as the original weights to scale. Use this option to specify a different branch to act as the original weight.")
  
  parser.add_option("--key", dest="key", default=None,
                    help="tagKey.json file that provides names for each bin in tag_branch.")  
  parser.add_option("--key2", dest="key2", default=None,
                    help="tagKey.json file that provides names for each bin in tag_branch2.") 

  parser.add_option("--outputDir", dest="outputDir", default="",
                    help="Specify the directory to save the output json files.")

  parser.add_option("--absoluteThreshold", dest="absolute_threshold", type=float, default=0,
                    help="Remove terms that are smaller than this number")

  parser.add_option("--stage0", dest="stage0", default=None)

  parser.add_option("--nBootstrap", dest="n_bootstrap", type="int", default=5, 
                    help="The number of resamples used in the boostrapping")

  (options, args) = parser.parse_args()

  if len(args) < 2:
    parser.print_help()
    sys.exit(1)
  EFT2Obs_config = args[0]
  nano_files = args[1:]

  return EFT2Obs_config, nano_files, options

def addBootstrapErrors(eqns, eqn_collection):
  for bin_name in eqns.keys():
    for term in eqns[bin_name].keys():
      values = [eqn[bin_name][term] if bin_name in eqn.keys() else 0. for eqn in eqn_collection]
      eqns[bin_name]["u_"+term] = np.std(values)
  return eqns

def main(EFT2Obs_config, nano_files, options):
  def_val, params = processConfig(EFT2Obs_config)
  key, key2 = getKeys(options)

  for nano_file in nano_files:
    nano_name = nano_file.split("/")[-1].split(".")[-2]
    json_path = os.path.join(options.outputDir, nano_name+".json")

    print(">> Reading %s and outputting %s"%(nano_file, json_path))
    reweights, tag_branch, key = readNanoFile(nano_file, options, key, key2)
    print(">> Finished reading")

    eqns = deriveEqns(reweights, tag_branch, key, params, def_val)

    if options.n_bootstrap > 1:
      n_events = len(reweights)
      resamples = np.random.randint(0, len(reweights), size=(options.n_bootstrap, n_events))

      eqn_collection = [deriveEqns(reweights[s], tag_branch[s], key, params, def_val) for s in resamples]
      #print(eqn_collection)
      eqns = addBootstrapErrors(eqns, eqn_collection)
    
    eqns = cleanUp(eqns, options)

    with open(json_path, "w") as f:
      json.dump(eqns, f, indent=4)

  return eqns

if __name__=="__main__":
  EFT2Obs_config, nano_files, options = getOptions()
  main(EFT2Obs_config, nano_files, options)

