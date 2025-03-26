from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

import standalone_reweight
import event as definitions
import numpy as np
import warnings

class ReweighterTemplate(Module):
  def __init__(self, rw_module_path, partsName, verb=False, no_match_behaviour='sm weights'):
    self.rw_module = standalone_reweight.StandaloneReweight(rw_module_path, no_match_behaviour)
    self.partsName = partsName
    self.verb = verb

  def beginJob(self):
    pass

  def endJob(self):
    pass

  def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    self.out = wrappedOutputTree
    self.out.branch("Reweights", "F", self.rw_module.N)

  def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    pass

  def getStatus(self, part, event, index):
    return part.status

  def getSpin(self, part, event, index):
    try:
      if abs(part.spin) <= 1:
        return part.spin
      else:
        return None
    except: #if no spin info
      return None

  def getpz(self, part, event, index):
    raise Exception("Particle with zero pt found. Must define a child class and specify how to find pz.")

  def getp4(self, part, event, index):
    """For a particle with non-zero pt, this is pretty simple. Just use the
    built in .p4() method to convert from eta,phi to px,py,pz,E.
    If a particle has zero pt, you can find pz through means that are specific
    to the collection used. Then, with pz and mass, you can find p4."""
    if part.pt>0:
      p4 = part.p4()
      return [p4[3], p4[0], p4[1], p4[2]]
    else:
      pz = self.getpz(part, event, index) #specific to collection used
      E = np.sqrt(part.mass**2 + pz**2)
      return [E, 0, 0, pz]

  def getnPart(self, event):
    return getattr(event, "n%s"%self.partsName)

  def getParticles(self, event):
    parts = Collection(event, self.partsName)
    rw_parts = []
    for index, p in enumerate(parts):
      if self.filterPart(p, event, index):
        p4 = self.getp4(p, event, index)
        status = self.getStatus(p, event, index)
        spin = self.getSpin(p, event, index)
        rw_parts.append(definitions.Particle(p4, p.pdgId, status, spin))
    return rw_parts

  def filterPart(self, part, event, index):
    """Return True if part should be included, False if not"""
    return True

  def acceptEvent(self, event):
    """Return True if event should be accepted, False if not"""
    return True

  def getAlphas(self, event):
    try:
      alphas = event.LHE_AlphaS
    except:
      #file doesn't have alphas info
      warnings.warn("Alpha_s not found")
      alphas = 0.137 #use as a default
    return alphas

  def analyze(self, event):
    """process event, return True (go to next module) or False (fail, go to next event)"""
    if self.acceptEvent(event):
      rw_event = definitions.Event(0, event.genWeight, self.getParticles(event), self.getAlphas(event))
      if self.verb: print(rw_event)

      reweights = rw_event.getReweights(self.rw_module, self.verb)
      if self.verb: print(str(reweights) + "\n")

      if reweights is False:
        return False
      else:
        self.out.fillBranch("Reweights", reweights) #just matrix elements
        #self.out.fillBranch("Reweights", [i * event.genWeight for i in reweights])
        return True
  
    else:
      return False

class LHEReweighter(ReweighterTemplate):
  def __init__(self, rw_module_path, verb=False, no_match_behaviour='sm weights'):
    ReweighterTemplate.__init__(self, rw_module_path, "LHEPart", verb, no_match_behaviour)
  
  def isIncomingParton(self, part, event, index):
    return part.status == -1

  def is2to1Process(self, part, event, index):
    return self.getnPart(event) == 3

  def getpz(self, part, event, index):
    if self.isIncomingParton(part, event, index):
      return part.incomingpz
    elif self.is2to1Process(part, event, index):
      #assuming the first two particles are the partons
      parts = Collection(event, self.partsName)
      return parts[0].incomingpz + parts[1].incomingpz
    else:
      raise Exception("Particle is not a parton, nor is this a 2->1 process. Uncertain how to proceed.")

class GenReweighter(ReweighterTemplate):
  def __init__(self, rw_module_path, pdgs=None, verb=False, no_match_behaviour='sm weights'):
    ReweighterTemplate.__init__(self, rw_module_path, "GenPart", verb, no_match_behaviour)
    self.wanted_pdgs = pdgs

  def getStatus(self, part, event, index):
    """Just a guess for now"""
    if part.status == 21:
      return -1
    else:
      return 1

  def isIncomingParton(self, part, event, index):
    return (index==0 or index==1)

  def is2to1Process(self, part, event, index):
    parts = Collection(event, self.partsName)
    no_from_partons = 0
    for part in parts:
      if part.genPartIdxMother==0:
        no_from_partons+=1
    return no_from_partons == 1

  def getpz(self, part, event, index):
    if self.isIncomingParton(part, event, index):
      if index==0:
        return event.Generator_x1*6500
      elif index==1:
        return -event.Generator_x2*6500
      else:
        raise Exception("If incoming parton, index should be 0 or 1. This was not the case.")
      
    elif self.is2to1Process(part, event, index):
      return (event.Generator_x1-event.Generator_x2)*6500
    else:
      raise Exception("Particle is not a parton, nor is this a 2->1 process. Uncertain how to proceed.")

  def getFlags(self, part):
    flag_dict = {0b1 : "isPrompt", 0b10 : "isDecayedLeptonHadron", 0b100 : "isTauDecayProduct", 
                0b1000 : "isPromptTauDecayProduct", 0b10000 : "isDirectTauDecayProduct", 
                0b100000 : "isDirectPromptTauDecayProduct", 0b1000000 : "isDirectHadronDecayProduct", 
                0b10000000 : "isHardProcess", 0b100000000 : "fromHardProcess", 
                0b1000000000 : "isHardProcessTauDecayProduct", 0b10000000000 : "isDirectHardProcessTauDecayProduct", 
                0b100000000000 : "fromHardProcessBeforeFSR", 0b1000000000000 : "isFirstCopy", 
                0b10000000000000 : "isLastCopy", 0b100000000000000 : "isLastCopyBeforeFSR"}
    flags = []
    for each in flag_dict.items():
      if (part.statusFlags & each[0])>0:
        flags.append(each[1])
    return flags

  def isHardProcess(self, part):
    flags = self.getFlags(part)
    return "isHardProcess" in flags

  def filterPart(self, part, event, index):
    if self.isHardProcess(part):
      if self.wanted_pdgs != None:
        return (part.pdgId in self.wanted_pdgs)
      else:
        return True
    else:
      return False

class HiggsDecayReweighter(GenReweighter):
  def isDaughterOfHiggs(self, part, event, index):
    """Includes non-direct daughters"""
    parts = Collection(event, self.partsName)
    mother_index = part.genPartIdxMother
    if mother_index >= 0:
      mother = parts[mother_index]
      if mother.pdgId == 25:
        return True
      else:
        return self.isDaughterOfHiggs(mother, event, mother_index)
    else:
      return False
  
  def filterPart(self, part, event, index):
    """If Higgs or decay product then accept"""
    if self.isHardProcess(part):
      if part.pdgId == 25:
        return True
      elif self.isDaughterOfHiggs(part, event, index):
        return True
      else:
        return False

  def getStatus(self, part, event, index):
    if self.isDaughterOfHiggs(part, event, index):
      return 1
    else:
      return -1

class H4LReweighter(HiggsDecayReweighter):
  def filterPart(self, part, event, index):
    """Accept Higgs and decay products but not intermediate Z"""
    if HiggsDecayReweighter.filterPart(self, part, event, index):
      if part.pdgId == 23:
        return False  
      return True
  
  def getParticles(self, event):
    """Grab particles and then reorder them so they line up with what rw module expects"""
    rw_parts = HiggsDecayReweighter.getParticles(self, event)
    #positive lepton in pair goes first
    if rw_parts[1].getPdg_id()>0:
      rw_parts[1], rw_parts[2] = rw_parts[2], rw_parts[1]
    if rw_parts[3].getPdg_id()>0:
      rw_parts[3], rw_parts[4] = rw_parts[4], rw_parts[3]
    #need to make sure the electrons are first in queue
    if rw_parts[1].getPdg_id()<rw_parts[3].getPdg_id():
      rw_parts[1], rw_parts[3] = rw_parts[3], rw_parts[1]
      rw_parts[2], rw_parts[4] = rw_parts[4], rw_parts[2]    
    return rw_parts

class ggFReweighter(LHEReweighter):
  def acceptEvent(self, event):
    """
    Keep number of jets below a specified number.
    Do not accept events with b jets.
    Only accept g g > ... events.
    """
    parts = Collection(event, self.partsName)
    #check that the first two parts (incoming partons) are gluons
    if (parts[0].pdgId!=21) or (parts[1].pdgId!=21):
      return False
    #count jets
    nJets = len(parts)-3 #2 partons and a higgs, everything else are jets
    if nJets > 0:
      return False
    #look for b's
    for part in parts:
      if abs(part.pdgId)==5:
        return False
    return True

class ttHReweighter(GenReweighter):
  def filterPart(self, part, event, index):
    if GenReweighter.filterPart(self, part, event, index):
      if self.isIncomingParton(part, event, index):
        return True
      #elif part.pdgId in [25, 6, -6]:
      #  return True
      elif part.genPartIdxMother==0:
        return True
      else:
        return False

class H4LProdReweighter(GenReweighter):
  def isDaughterOfHiggs(self, part, event, index):
    """Includes non-direct daughters"""
    parts = Collection(event, self.partsName)
    mother_index = part.genPartIdxMother
    if mother_index >= 0:
      mother = parts[mother_index]
      if mother.pdgId == 25:
        return True
      else:
        return self.isDaughterOfHiggs(mother, event, mother_index)
    else:
      return False

  def filterPart(self, part, event, index):
    isHard = (self.isHardProcess(part) or index==2) 
    isDaughter = self.isDaughterOfHiggs(part, event, index)
    isIntermediateV = (abs(part.pdgId) == 24) or (part.pdgId == 23)
    return (isHard and not isDaughter) and not isIntermediateV
    

"""
# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
LHEReweighterConstr = lambda: LHEReweighter(rw_module_path)
GenReweighterConstr = lambda: GenReweighter(rw_module_path)
"""