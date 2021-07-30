#!/usr/bin/env python
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from importlib import import_module
import os
import sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import awkward as ak
import numpy as np

from Utilities.General.cmssw_das_client import get_data as das_query
import pickle
import pandas as pd
import json

class ExampleAnalysis(Module):
  def __init__(self, df, keepNoTag=False, NoTagIndex=0, extraBranches=[]):
    self.df = df
    self.keepNoTag = keepNoTag
    self.NoTagIndex = NoTagIndex
    self.notFound = 0
    self.extraBranches = extraBranches

  def beginJob(self):
    pass

  def endJob(self):
    print("No. failed matches: %d"%self.notFound)
    pass

  def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    self.out = wrappedOutputTree
    self.out.branch("category", "I")
    if len(self.extraBranches) > 0:
      print("> Adding extra branches from csv file")
      for branch in self.extraBranches:
        print(" %s"%branch)
        self.out.branch(branch, "F")

  def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    pass

  def beginJob(self, histFile=None, histDirName=None):
    pass

  def fillBranches(self, entry):
    self.out.fillBranch("category", entry["category"])
    if self.extraBranches != None:
      for branch in self.extraBranches:
        self.out.fillBranch(branch, entry[branch])    

  def analyze(self, event):
    eventID = int(event.event)
    try:
      entry = self.df.loc[eventID]
      self.fillBranches(entry)

      if self.keepNoTag:
        return True
      elif entry.category != self.NoTagIndex:
        return True
      else:
        return False
    except:
      self.notFound += 1
      return False

def findFiles(dataset):
  print(">> Finding files for %s"%dataset)
  query = das_query("file dataset=%s"%dataset)
  files = [each['file'][0] for each in query['data']]

  totalN = sum([f['nevents'] for f in files])
  print(">> Found %d events across %d files"%(totalN, len(files)))

  files_dir = ["root://xrootd-cms.infn.it/%s"%f['name'] for f in files]
  return files_dir


def addKeep(txt, collection):
  return txt + "\nkeep %s*"%collection

def makeInputOutputTxt(options):
  baseCollections = ["event", "category", "LHEPart", "GenPart", "Generator",
                     "genWeight", "LHE_AlphaS", "HTXS_stage1_2_cat_pTjet30GeV"]
  txt = "drop *"
  for collection in baseCollections:
    txt = addKeep(txt, collection)
  for collection in options.extraCollections:
    txt = addKeep(txt, collection)
  for collection in options.extraBranches:
    txt = addKeep(txt, collection)
  with open("%s/keep_and_drop.txt"%os.environ.get("TMPDIR"), "w") as f:
    f.write(txt)

def run(df, files, options):
  if options.test:
    files = [files[0]]
    maxEntries = 10000
  else:
    maxEntries = None

  print(">> Starting skim")
  postfix = "_temp"
  p = PostProcessor(".", files, branchsel="%s/keep_and_drop.txt"%os.environ.get("TMPDIR"), modules=[ExampleAnalysis(df, extraBranches=options.extraBranches)], postfix=postfix, prefetch=True, maxEntries=maxEntries)
  p.run()
  print(">> Skim complete")

  #collect all root files into one
  prescripts = [f.split("/")[-1].split(".")[0] for f in files]
  
  #merge root files
  print(">> Merging root files")
  new_file_names = ["%s%s.root"%(pre, postfix) for pre in prescripts]
  os.system("hadd -f %s %s"%(options.output_root, " ".join(new_file_names))) 
  
  #remove remaining root files after merge
  command = "rm %s"%" ".join(new_file_names)
  os.system(command)

def processExtraBranches(options, df):
  if options.extraBranches != None:
    if options.extraBranches == "auto":
      extraBranches = df.columns
      extraBranches = filter(lambda x: x not in ["category", "Unnamed: 0"], extraBranches)
      extraBranches = filter(lambda x: pd.api.types.is_numeric_dtype(df[x]), extraBranches)
    else:
      extraBranches = options.extraBranches.split(",")
  else:
      extraBranches = []
  options.extraBranches = extraBranches

def processExtraCollections(options):
  if options.extraCollections is not None:
    options.extraCollections = options.extraCollections.split(",")
  else:
    options.extraCollections = []

if __name__=="__main__":
  from optparse import OptionParser
  parser = OptionParser(usage="%prog dataset df_csv")
  parser.add_option("--test", dest="test", default=False, action="store_true",
                    help="Skim only one file from the dataset, upto 10,000 events")
  parser.add_option('--extraBranches', dest='extraBranches', default=None, 
                    help="Comma separated list of branches/columns from the csv file that should be added to the output tree. auto = add all branches from csv file.")
  parser.add_option('--extraCollections', dest='extraCollections', default=None,
                    help="Comma separated list of variables/collections from the nanoAOD to include. All collections needed for reweighting are included by default, this option is for additional collections.")
  parser.add_option('--output', '-o', dest='output_root', default=None,
                    help="Path to output root file, e.g. path/to/myroot.root")
  parser.add_option('--datasetJson', dest='datasetJson', default="eventIDSkimming/datasetKeys.json",
                    help="Path to json dict that stores dataset shortcuts")
  

  (options, args) = parser.parse_args()
  
  if len(args) < 2:
    parser.print_help()
    sys.exit(1)
  dataset = args[0]
  df_csv = args[1]

  try:
    with open(options.datasetJson, "r") as f:
      dataset_dict = json.loads(f.read())
  except:
    dataset_dict = {}

  if dataset in dataset_dict.keys():
    dataset = dataset_dict[dataset]

  files = findFiles(dataset)
  
  df = pd.read_csv(df_csv)
  df.set_index("event", inplace=True)

  processExtraBranches(options, df)
  processExtraCollections(options)

  makeInputOutputTxt(options)

  if options.output_root is None:
    options.output_root = dataset.split("/")[1] + ".root"
  
  run(df, files, options)
