import uproot
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import json
from collections import OrderedDict

#helper function for reading json and converting keys to integers
def keysToInt(x):
  od = OrderedDict()
  for k, v in x:
    od[int(k)] = v
  return od

def replaceNan(arr, num):
  for i in range(len(arr)):
    if np.isnan(arr[i]) or np.isinf(arr[i]):
      arr[i] = num
  return arr

def hist(shape, reweights, i, options, density=False):
  n_sm, edges = np.histogram(shape, options.bin_number, options.bin_range, weights = reweights[:,0], density=density)
  n_eft, edges = np.histogram(shape, options.bin_number, options.bin_range, weights = reweights[:,(2+i*2)], density=density)
  return n_sm, n_eft, edges

def getRatioAndUncert(shape, reweights, i, options):
  #get ratio using all events
  n_sm, n_eft, edges = hist(shape, reweights, i, options)
  ratio = n_eft/n_sm -1

  overall_scaling = sum(n_eft) / sum(n_sm) - 1

  ratio = replaceNan(ratio, overall_scaling)

  #separate events into 3 and calculate ratios
  ratios = []
  nsplits = 10
  indicies = np.arange(0, len(shape), 1)
  np.random.shuffle(indicies)
  splits = np.array_split(indicies, nsplits)

  bin_with_zero_events = np.zeros(options.bin_number) #use to keep track of when a bin had no events

  for j in range(nsplits):
    n_sm, n_eft, edges = hist(shape[splits[j]], reweights[splits[j]], i, options)
    bin_with_zero_events[np.where(n_sm==0)] = 1
    ratios.append(replaceNan(n_eft/n_sm -1, overall_scaling))
  ratios = np.array(ratios)

  uncert = np.std(ratios, axis=0) / np.sqrt(nsplits)

  #where there were no events in a bin, artifically set the uncertainty high
  uncert[np.where(bin_with_zero_events==1)] = ratio[np.where(bin_with_zero_events==1)] * 10

  return ratio, uncert, overall_scaling

def plot(shape, reweights, i, options, params, defval, bin_name=""):
  n_sm_normed, n_eft_normed, edges = hist(shape, reweights, i, options, density=True)
  ratio, uncert, overall_scaling = getRatioAndUncert(shape, reweights, i, options)

  if not options.plotAll:
    if (ratio != 0).sum() == 0:
      return None #don't do plot if parameter has no influence

  f, axs = plt.subplots(2, sharex=True, gridspec_kw={'height_ratios': [3, 1]})

  #print(len(edges))
  #print(edges)
  #print(n_sm_normed)
  #print(n_eft_normed)

  axs[0].hist(edges[:-1], edges, weights=n_sm_normed, histtype="step", label="SM")
  axs[0].hist(edges[:-1], edges, weights=n_eft_normed, histtype="step", label="%s = %.2f"%(params[i], defval))
  axs[0].set_ylabel("No. Events (normalised)")

  axs[0].text(0.05, 0.9, "%d events"%len(shape), transform=axs[0].transAxes)
  
  std_down = ratio-uncert
  std_up = ratio+uncert

  axs[1].hist(edges[:-1], edges, weights=ratio, histtype="step", color="tab:orange")
  axs[1].fill_between(edges, list(std_down)+[std_down[-1]], list(std_up)+[std_up[-1]], alpha=0.3, step="post", color="grey", lw=1)
  line = axs[1].plot([edges[0], edges[-1]], [overall_scaling, overall_scaling], 'g--', label="overall scaling")
  axs[1].set_xlabel(options.xlabel)
  axs[1].set_ylabel("Ratio to SM -1")
  #axs[1].set_ylim(min(ratio-uncert)-max(uncert)*0.2, max(ratio+uncert)+max(uncert)*0.2)
  height = max(ratio) - min(ratio)
  axs[1].set_ylim(min(ratio)-height*0.1, max(ratio)+height*0.1)
  
  """
  deviation = ratio-overall_scaling
  nsigma_deviation = np.zeros(len(deviation))
  nsigma_deviation[np.where(deviation!=0)] = deviation[np.where(deviation!=0)] / uncert[np.where(deviation!=0)]
  bin_centers = (edges[:-1]+edges[1:])/2
  axs[1].scatter(bin_centers, nsigma_deviation)
  """

  handles, labels = axs[0].get_legend_handles_labels()
  handles.append(line[0])
  axs[0].legend(handles=handles)

  f.savefig("%s/%s_%s.png"%(options.savepath, bin_name, params[i]))
  #f.savefig("%s/%s_%s.pdf"%(options.savepath, bin_name, params[i]))
  plt.close()


from optparse import OptionParser
parser = OptionParser(usage="%prog reweightedNanoAOD branch")

parser.add_option("--weight-branch", dest="weight_branch", default=None,
                  help="By default, standalone reweighting using the 'genWeight' branch as the original weights to scale. Use this option to specify a different branch to act as the original weight.")
parser.add_option("--config", "-c", dest="config", default=None,
                  help="The json config used to generate the reweighting module. If included, parameter names will be shown in plots.")
parser.add_option("--range", "-r", dest="bin_range", default="0,200",
                  help="Bin range for the histogram.")
parser.add_option("--binNumber", "-n", dest="bin_number", default=50, type="int",
                  help="Number of bins.")
parser.add_option("--xlabel", "-x", dest="xlabel", default=None,
                  help="Label for the x axis. Default will be the name of the branch")                 
parser.add_option("--save-path", "-s", dest="savepath", default="./",
                  help="Directory to save the plots to.")
parser.add_option("--tag-branch", dest="tag_branch", default="HTXS_stage1_2_cat_pTjet30GeV",
                  help="Specify the branch used to tag the events, e.g. HTXS_stage1_2_cat_pTjet30GeV")
parser.add_option("--inclusive", dest="inclusive", default=False, action="store_true",
                  help="Dump all events into a single bin. Do no splitting by e.g. STXS bin.")
parser.add_option("--key", dest="key", default=None,
  help="tagKey.json file for tag-branch.")
parser.add_option("--removeBigWeights", dest="removeBigWeights", default=False, action="store_true",
                  help="Remove events with a weight that is >10^3 times larger than the average")
parser.add_option("--plotAll", dest="plotAll", default=False, action="store_true",
                  help="By default, plots are only saved if the parameter changes overall scaling. Use this option all parameters for all bins.")


(options, args) = parser.parse_args()

if len(args) < 2:
  parser.print_help()
  sys.exit(1)
filename = args[0]
branch = args[1]

f = uproot.open(filename)["Events"]

reweights = f['Reweights'].array(library='np')

#if option is chosen, remove events which have large weights relative to the average
if options.removeBigWeights:
  avg_weight = abs(reweights.mean(axis=0))
  any_rw_gt = abs(reweights) > avg_weight*100
  remove_event = any_rw_gt.sum(axis=1).astype(bool)
  selection = ~remove_event
  print("Fraction of events kept: %f"%(float(sum(selection))/len(selection)))
else:
  selection = np.ones(len(reweights)).astype(bool)

reweights = reweights[selection]
shape = f[branch].array(library='np')[selection]

#if using a single bin, tag every event with 0
if options.inclusive:
  tag = np.zeros(len(reweights))
else:
  tag = f[options.tag_branch].array()[selection]

if options.key is not None:
  with open(options.key, "r") as key_f:
    key = json.loads(key_f.read(), object_pairs_hook=keysToInt)

#if using different original weight, find scaling and apply to new original weights
if options.weight_branch is not None:
  original_weights = f[options.weight_branch].array(library='np')[selection]
  sf = reweights / reweights[:,0,np.newaxis]
  reweights = sf * original_weights[...,np.newaxis]

n_rw = len(reweights[0])
n_pars = int((-3 + np.sqrt(9+8*(n_rw-1)))/2)

if options.config is not None:
  with open(options.config, "r") as f:
    options.config = json.loads(f.read(), object_pairs_hook=OrderedDict)
  params = [entry['name'] for entry in options.config['parameters']]
  defval = options.config['parameter_defaults']['val']
else:
  params = [i for i in range(n_pars)]
  defval = 0.01

options.bin_range = [float(x) for x in options.bin_range.split(",")]

if options.xlabel is None:
  options.xlabel = branch

unique_tags = np.unique(tag)
for unique_tag in unique_tags:
  s = tag==unique_tag
  for i in range(n_pars):
    if options.key is not None:
      bin_name = key[unique_tag]
    else:
      bin_name = unique_tag
    plot(shape[s], reweights[s], i, options, params, defval, bin_name)
