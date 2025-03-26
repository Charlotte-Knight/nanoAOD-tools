import numpy as np

class Particle:
  def __init__(self, p, pdg_id, status, helicity=None):
    self.p = p
    self.pdg_id = pdg_id
    self.status = status
    self.helicity = helicity

  def getP(self):
    return self.p

  def getPT(self):
    return np.sqrt(self.p[1]**2 + self.p[2]**2) 

  def getPdg_id(self):
    return self.pdg_id

  def getStatus(self):
    return self.status

  def getHelicity(self):
    return self.helicity

  def isJet(self):
    if self.status==1:
      if (abs(self.pdg_id)<=9) or (self.pdg_id==21):
        return True
    return False

  def __str__(self):
    p_strs = [("%.1f"%p_i).rjust(10, ' ') for p_i in self.p]

    string = str(pdg_dict[self.pdg_id]).rjust(10, ' ') + str(self.status).rjust(10, ' ') + str(self.helicity).rjust(10, ' ') + " "*5 + ''.join(p_strs)

    return string

class Event:
  def __init__(self, event_id, weight, gen_particles, alphas=0.137, scale2=0.0):
    self.event_id = event_id
    self.gen_particles = gen_particles
    self.alphas = alphas
    self.weight = weight
    self.scale2 = scale2

  def getWeight(self):
    return self.weight

  def getParticles(self):
    return self.gen_particles

  def getReweightInfo(self):
    parts = []
    pdgs = []
    helicities = []
    status = []
    for particle in self.gen_particles:
      parts.append(particle.getP())
      pdgs.append(particle.getPdg_id())
      helicities.append(particle.getHelicity())
      status.append(particle.getStatus())

    return parts, pdgs, helicities, status

  def useHelicity(self, helicities):
    """
    If all gen_particles have helicity information return True.
    Else, return False.
    """
    for h in helicities:
      if h==None:
        return False
    return True

  def getReweights(self, rw, verb=False):
    parts, pdgs, helicities, status = self.getReweightInfo()

    use_helicity = self.useHelicity(helicities)
    reweights = rw.ComputeWeights(parts, pdgs, helicities, status, self.alphas, use_helicity, verb)
    return reweights

  def __str__(self):
    strings = []
    strings.append("-"*75)
    strings.append(" Particle | status  | helicity |   | E       | P_x     | P_y     | P_z      ")
    strings.append("-"*75)
    for particle in self.gen_particles:
      strings.append(str(particle))
    return "\n".join(strings)

"""
Credit to https://github.com/scikit-hep/particle for the csv file
https://doi.org/10.5281/zenodo.2552429
"""
"""
import csv
pdg_dict = {}
with open("pdgid_to_evtgenname.csv", "r") as f:
  line_no = 0
  for row in csv.reader(f):
    if line_no>1:
      pdg_dict[int(row[0])] = row[1]
    line_no += 1
"""

pdg_dict = {480000000: 'geantino', 1: 'd', 2: 'u', 3: 's', 4: 'c', 5: 'b', 6: 't', 7: "b'", 8: "t'", 11: 'e-', 12: 'nu_e', 13: 'mu-', 14: 'nu_mu', 15: 'tau-', 16: 'nu_tau', 17: 'L-', 18: 'nu_L', 21: 'g', 22: 'gamma', 23: 'Z0', 24: 'W+', 25: 'Higgs0', 4122: 'Lambda_c+', -10213: 'b_1-', -10211: 'a_0(1450)-', 4101: 'cd_0', 32: "Z'0", 33: "Z''0", 34: "W'+", 35: "Higgs'0", 36: 'A0', 37: 'Higgs+', 38: 'Higgs++', -100313: "anti-K'*0", 40: 'a0', 41: 'R0', 43: 'Xu0', 44: 'Xu+', -20433: 'D_s1-', 2101: 'ud_0', 2103: 'ud_1', -20423: "anti-D'_10", 100411: 'D(2S)+', 100413: 'D*(2S)+', -12226: 'anti-Delta(1930)--', 20543: "B'_c1+", 2112: 'n0', 10325: 'K_2(1770)+', 2114: 'Delta0', -20413: "D'_1-", 2116: 'N(1675)0', 100421: 'D(2S)0', 2118: 'Delta(1950)0', 10311: 'K_0*0', -12216: 'anti-N(1680)-', 10313: 'K_10', 2122: 'Delta(1620)+', 10315: 'K_2(1770)0', 2124: 'N(1520)+', 2126: 'Delta(1905)+', 2128: 'N(2190)+', 81: 'specflav', 82: 'rndmflav', 83: 'phasespa', 84: 'c-hadron', 85: 'b-hadron', 86: 't-hadron', 87: "b'-hadron", 88: 'junction', 100441: 'eta_c(2S)', 90: 'system', 91: 'cluster', 92: 'string', 93: 'indep', 94: 'CMshower', 95: 'SPHEaxis', 96: 'THRUaxis', 97: 'CLUSjet', 98: 'CELLjet', 4201: 'cu_0', 4203: 'cu_1', 4114: 'Sigma_c*0', 111: 'pi0', 113: 'rho0', 43122: 'Lambda(1800)0', 115: 'a_20', 4212: 'Sigma_c+', 117: 'rho_3(1690)0', 4214: 'Sigma_c*+', 119: 'a_4(1970)0', -104324: 'anti-Xi_c(2790)-', 4222: 'Sigma_c++', 4224: 'Sigma_c*++', 130: 'K_L0', -104314: 'anti-Xi_c(2790)0', 4232: 'Xi_c+', -100213: 'rho(2S)-', -100211: 'pi(2S)-', 150: 'B0L', -10215: 'pi_2(1670)-', 22212: 'N(1535)+', 2203: 'uu_1', -20323: "K'_1-", -12126: 'anti-Delta(1930)-', 2212: 'p+', -20315: 'anti-K_2(1820)0', 2214: 'Delta+', -20313: "anti-K'_10", 2216: 'N(1675)+', 2218: 'Delta(1950)+', 10411: 'D_0*+', -12116: 'anti-N(1680)0', 10413: 'D_1+', 2222: 'Delta(1620)++', -100323: "K'*-", 2224: 'Delta++', 103112: 'Sigma(2250)-', 2226: 'Delta(1905)++', 2228: 'Delta(1950)++', 10421: 'D_0*0', 110551: 'chi_b0(2P)', 10423: 'D_10', -100321: 'K(1460)-', 20533: "B'_s10", 10431: 'D_s0*+', 10433: "D'_s1+", 20513: "B'_10", 10441: 'chi_c0', 10443: 'h_c', 4301: 'cs_0', 4303: 'cs_1', 211: 'pi+', 213: 'rho+', -14122: 'anti-Lambda_c(2593)-', 215: 'a_2+', 4312: "Xi'_c0", 217: 'rho_3(1690)+', 4314: 'Xi_c*0', 219: 'a_4(1970)+', 221: 'eta', 223: 'omega', 225: 'f_2', 4322: "Xi'_c+", 227: 'omega_3(1670)', 4324: 'Xi_c*+', 229: 'f_4(2050)', 4332: 'Omega_c0', 4334: 'Omega_c*0', -13222: 'anti-Sigma(1660)-', -100311: 'anti-K(1460)0', 41214: 'N(1900)0', 20523: "B'_1+", 104122: 'Lambda_c(2625)+', -20213: 'a_1-', 10511: 'B_0*0', 10513: 'B_10', 10521: 'B_0*+', 10523: 'B_1+', 10531: 'B_s0*0', 1000010020: 'deuteron', 10533: 'B_s10', 21212: 'Delta(1910)0', 10541: 'B_c0*+', 110555: 'eta_b2(2D)', 10543: 'B_c1+', -22224: 'anti-Delta(1920)--', -21112: 'anti-Delta(1910)+', -22222: 'anti-Delta(1910)--', 4403: 'cc_1', 310: 'K_S0', 311: 'K0', 1000020040: 'alpha', 313: 'K*0', -22214: 'anti-Delta(1920)-', 315: 'K_2*0', 4412: 'Xi_cc+', 317: 'K_3*0', 4414: 'Xi_cc*+', 319: 'K_4*0', 321: 'K+', 323: 'K*+', 325: 'K_2*+', 4422: 'Xi_cc++', 327: 'K_3*+', 4424: 'Xi_cc*++', 329: 'K_4*+', 331: "eta'", 333: 'phi', 335: "f'_2", 4432: 'Omega_cc+', 337: 'phi_3(1850)', 4434: 'Omega_cc*+', 4103: 'cd_1', 4444: 'Omega_ccc*++', 350: 'B_s0L', 33122: 'Lambda(1670)0', -30363: 'anti-Xss', -30353: 'anti-Xsu', 1000020030: 'He3', -30343: 'anti-Xsd', -12224: 'anti-Delta(1700)--', 120555: 'Upsilon_2(2D)', 31114: 'Delta(1600)-', -12222: 'anti-Delta(1900)--', -22124: 'anti-N(1700)-', -22122: 'anti-Delta(1910)-', -30313: "anti-K''*0", 411: 'D+', 413: 'D*+', -22114: 'anti-Delta(1920)0', 415: 'D_2*+', -22112: 'anti-N(1535)0', 421: 'D0', 423: 'D*0', 425: 'D_2*0', 100423: 'D*(2S)0', 431: 'D_s+', 433: 'D_s*+', 435: 'D_s2*+', 20553: 'chi_b1', 441: 'eta_c', 443: 'J/psi', 445: 'chi_c2', 20555: 'Upsilon_2(1D)', 9080225: 'f_2(2300)', -12212: 'anti-N(1440)-', -104322: 'anti-Xi_c(2815)-', 13314: 'Xi(1820)-', 10321: 'K_0*+', 9042413: 'Z(4430)+', 31214: 'N(1720)0', 10323: 'K_1+', -30213: 'rho(3S)-', 510: 'B0H', 511: 'B0', 513: 'B*0', 515: 'B_2*0', 521: 'B+', 523: 'B*+', 525: 'B_2*+', -13224: 'anti-Sigma(1670)-', 530: 'B_s0H', 531: 'B_s0', 533: 'B_s*0', 535: 'B_s2*0', 541: 'B_c+', 543: 'B_c*+', -32224: 'anti-Delta(1600)--', 545: 'B_c2*+', 10331: 'f_0(1710)', 551: 'eta_b', 553: 'Upsilon', -32214: 'anti-Delta(1600)-', 555: 'chi_b2', -32212: 'anti-N(1650)-', 557: 'Upsilon_3(1D)', 10333: "h'_1", 203312: 'Xi(1690)-', 203316: 'Xi(2030)-', 5214: 'Sigma_b*0', 203322: 'Xi(1690)0', 10335: 'eta_2(1870)', 203326: 'Xi(2030)0', -203338: 'anti-Omega(2250)+', 23112: 'Sigma(1750)-', 23114: 'Sigma(1940)-', -103326: 'anti-Xi(1950)0', -5554: 'anti-Omega_bbb+', 23122: 'Lambda(1600)0', 23124: 'Lambda(1890)0', 23126: 'Lambda(2110)0', -5544: 'anti-Omega_bbc*0', -5542: 'anti-Omega_bbc0', -5534: 'anti-Omega_bb*+', -5532: 'anti-Omega_bb+', 4112: 'Sigma_c0', -5524: 'anti-Xi_bb*0', -5522: 'anti-Xi_bb0', -5514: 'anti-Xi_bb*+', -5512: 'anti-Xi_bb+', 21114: 'Delta(1920)-', -5503: 'anti-bb_1', -32124: 'anti-N(1720)-', -32114: 'anti-Delta(1600)0', -32112: 'anti-N(1650)0', -204126: 'anti-Lambda_c(2880)-', 9050225: 'f_2(1950)', 23212: 'Sigma(1750)0', 23214: 'Sigma(1940)0', 23222: 'Sigma(1750)+', 23224: 'Sigma(1940)+', -5444: 'anti-Omega_bcc*-', -5442: 'anti-Omega_bcc-', -5434: 'anti-Omega_bc*0', -5432: "anti-Omega'_bc0", -5424: 'anti-Xi_bc*-', -5422: "anti-Xi'_bc-", -30323: "K''*-", -5414: 'anti-Xi_bc*0', -5412: "anti-Xi'_bc0", 21214: 'N(1700)0', -5403: 'anti-bc_1', -5401: 'anti-bc_0', -9000215: 'a_2(1700)-', -9000213: 'pi_1(1400)-', -9000211: 'a_0-', -53122: 'anti-Lambda(1810)0', -3334: 'anti-Omega+', -3324: 'anti-Xi*0', -3322: 'anti-Xi0', 9000553: 'Upsilon(5S)', 20323: "K'_1+", 103212: 'Sigma(2250)0', -3314: 'anti-Xi*+', -3312: 'anti-Xi+', 15122: 'Lambda_b(5912)0', -103222: 'anti-Sigma(2250)-', -3303: 'anti-ss_1', -42212: 'anti-N(1710)-', 1000223: 'omega(2S)', -5342: 'anti-Omega_bc0', -5334: 'anti-Omega_b*+', -5332: 'anti-Omega_b+', -104312: 'anti-Xi_c(2815)0', -5324: 'anti-Xi_b*0', -5322: "anti-Xi'_b0", 13112: 'Sigma(1660)-', 13114: 'Sigma(1670)-', 13116: 'Sigma(1915)-', 9020221: 'eta(1405)', -1218: 'anti-N(2190)0', -1216: 'anti-Delta(1905)0', -1214: 'anti-N(1520)0', -1212: 'anti-Delta(1620)0', 103222: 'Sigma(2250)+', 13126: 'Lambda(1830)0', -5303: 'anti-bs_1', -5301: 'anti-bs_0', 11212: 'Delta(1900)0', -1000020040: 'anti-alpha', -3228: 'anti-Sigma(2030)-', -3226: 'anti-Sigma(1775)-', -3224: 'anti-Sigma*-', -3222: 'anti-Sigma-', -9010325: 'K_2*(1980)-', 11116: 'Delta(1930)-', -3218: 'anti-Sigma(2030)0', -3216: 'anti-Sigma(1775)0', -100423: 'anti-D*(2S)0', -3214: 'anti-Sigma*0', -3212: 'anti-Sigma0', -5314: 'anti-Xi_b*+', -3203: 'anti-su_1', -3201: 'anti-su_0', -42112: 'anti-N(1710)0', -5312: "anti-Xi'_b+", -11114: 'anti-Delta(1700)+', -5242: 'anti-Xi_bc-', 13122: 'Lambda(1405)0', -5232: 'anti-Xi_b0', -11112: 'anti-Delta(1900)+', 52114: 'N(2090)0', 103316: 'Xi(1950)-', -5224: 'anti-Sigma_b*-', 13124: 'Lambda(1690)0', -5222: 'anti-Sigma_b-', 13212: 'Sigma(1660)0', 13214: 'Sigma(1670)0', 13216: 'Sigma(1915)0', -1118: 'anti-Delta(1950)+', -20325: 'K_2(1820)-', -1116: 'anti-Delta(1905)+', -1114: 'anti-Delta+', -1112: 'anti-Delta(1620)+', 13226: 'Sigma(1915)+', -5203: 'anti-bu_1', -5201: 'anti-bu_0', -1103: 'anti-dd_1', 9010111: 'pi(1800)0', 9010113: 'pi_1(1600)0', -3128: 'anti-Lambda(2100)0', -3126: 'anti-Lambda(1820)0', -3124: 'anti-Lambda(1520)0', -3122: 'anti-Lambda0', 11216: 'Delta(1930)0', -3118: 'anti-Sigma(2030)+', -3116: 'anti-Sigma(1775)+', -3114: 'anti-Sigma*+', -9010315: 'anti-K_2*(1980)0', -3112: 'anti-Sigma+', 100553: 'Upsilon(2S)', -9010213: 'pi_1(1600)-', -9010211: 'pi(1800)-', -3103: 'anti-sd_1', -3101: 'anti-sd_0', -12122: 'anti-Delta(1900)-', -5142: 'anti-Xi_bc0', 5101: 'bd_0', 5103: 'bd_1', -10413: 'D_1-', -5132: 'anti-Xi_b+', 52214: 'N(2090)+', 5112: 'Sigma_b-', 5114: 'Sigma_b*-', -5124: 'anti-Lambda_b(5920)0', -12118: 'anti-N(1990)0', -5122: 'anti-Lambda_b0', -7: "anti-b'", 5122: 'Lambda_b0', 5124: 'Lambda_b(5920)0', 12118: 'N(1990)0', -5114: 'anti-Sigma_b*+', -5112: 'anti-Sigma_b+', -52214: 'anti-N(2090)-', 5132: 'Xi_b-', 9910445: 'X_2(3872)', -5103: 'anti-bd_1', -5101: 'anti-bd_0', -12114: 'anti-Delta(1700)0', 5142: 'Xi_bc0', 30553: 'Upsilon_1(1D)', 9020443: 'psi(4415)', 3101: 'sd_0', 3103: 'sd_1', -12112: 'anti-N(1440)0', 9010211: 'pi(1800)+', 9010213: 'pi_1(1600)+', 9090225: 'f_2(2340)', 3112: 'Sigma-', 3114: 'Sigma*-', 3116: 'Sigma(1775)-', 9010221: 'f_0', 3118: 'Sigma(2030)-', -11216: 'anti-Delta(1930)0', 3122: 'Lambda0', 3124: 'Lambda(1520)0', 3126: 'Lambda(1820)0', 3128: 'Lambda(2100)0', 1103: 'dd_1', 5201: 'bu_0', 5203: 'bu_1', -13226: 'anti-Sigma(1915)-', 1112: 'Delta(1620)-', 1114: 'Delta-', 30223: 'omega(1650)', 1116: 'Delta(1905)-', 1118: 'Delta(1950)-', 20325: 'K_2(1820)+', -13216: 'anti-Sigma(1915)0', -13214: 'anti-Sigma(1670)0', -13212: 'anti-Sigma(1660)0', 5222: 'Sigma_b+', 5224: 'Sigma_b*+', -13124: 'anti-Lambda(1690)0', 200551: 'eta_b(3S)', -103316: 'anti-Xi(1950)+', -52114: 'anti-N(2090)0', 42124: 'N(1900)+', 5232: 'Xi_b0', 11112: 'Delta(1900)-', -20533: "anti-B'_s10", -13122: 'anti-Lambda(1405)0', 200553: 'Upsilon(3S)', 9920443: 'X_1(3872)', 5242: 'Xi_bc+', 11114: 'Delta(1700)-', 42112: 'N(1710)0', 3201: 'su_0', 3203: 'su_1', 9010315: 'K_2*(1980)0', 3212: 'Sigma0', 5314: 'Xi_b*-', 3214: 'Sigma*0', 3216: 'Sigma(1775)0', 3218: 'Sigma(2030)0', -11116: 'anti-Delta(1930)+', 9010325: 'K_2*(1980)+', 3222: 'Sigma+', 3224: 'Sigma*+', 3226: 'Sigma(1775)+', 3228: 'Sigma(2030)+', 13324: 'Xi(1820)0', 21112: 'Delta(1910)-', 100551: 'eta_b(2S)', 9000111: 'a_00', 9000113: 'pi_1(1400)0', 9000115: 'a_2(1700)0', 5301: 'bs_0', 5303: 'bs_1', -42124: 'anti-N(1900)-', -13126: 'anti-Lambda(1830)0', 1212: 'Delta(1620)0', 100323: "K'*+", 1214: 'N(1520)0', 4132: 'Xi_c0', 1216: 'Delta(1905)0', 1218: 'N(2190)0', 100555: 'chi_b2(2P)', -13116: 'anti-Sigma(1915)+', -13114: 'anti-Sigma(1670)+', -13112: 'anti-Sigma(1660)+', 5322: "Xi'_b0", 5324: 'Xi_b*0', 100557: 'Upsilon_3(2D)', 104312: 'Xi_c(2815)0', 5332: 'Omega_b-', 5334: 'Omega_b*-', 5342: 'Omega_bc0', 12112: 'N(1440)0', 42212: 'N(1710)+', 3303: 'ss_1', -15122: 'anti-Lambda_b(5912)0', 3312: 'Xi-', 3314: 'Xi*-', -103212: 'anti-Sigma(2250)0', 3322: 'Xi0', 3324: 'Xi*0', -13324: 'anti-Xi(1820)0', 3334: 'Omega-', 9060225: 'f_2(2010)', 9010443: 'psi(4160)', 53122: 'Lambda(1810)0', 9000211: 'a_0+', 9000213: 'pi_1(1400)+', 9000215: 'a_2(1700)+', 5401: 'bc_0', 5403: 'bc_1', 12114: 'Delta(1700)0', 9000221: 'sigma_0', -21214: 'anti-N(1700)0', 5412: "Xi'_bc0", 5414: 'Xi_bc*0', 5422: "Xi'_bc+", 5424: 'Xi_bc*+', 5432: "Omega'_bc0", 5434: 'Omega_bc*0', 5442: 'Omega_bcc+', 5444: 'Omega_bcc*+', -23224: 'anti-Sigma(1940)-', -23222: 'anti-Sigma(1750)-', -23214: 'anti-Sigma(1940)0', -23212: 'anti-Sigma(1750)0', 204126: 'Lambda_c(2880)+', 32112: 'N(1650)0', 32114: 'Delta(1600)0', 9010553: 'Upsilon(11020)', 32124: 'N(1720)+', 5503: 'bb_1', -21114: 'anti-Delta(1920)+', 5512: 'Xi_bb-', 220553: 'chi_b1(3P)', 5514: 'Xi_bb*-', -18: 'anti-nu_L', 5522: 'Xi_bb0', 5524: 'Xi_bb*0', 5532: 'Omega_bb-', 5534: 'Omega_bb*-', 30113: 'rho(3S)0', 5542: 'Omega_bbc0', 5544: 'Omega_bbc*0', -23126: 'anti-Lambda(2110)0', -23124: 'anti-Lambda(1890)0', -23122: 'anti-Lambda(1600)0', 5554: 'Omega_bbb-', 103326: 'Xi(1950)0', -23114: 'anti-Sigma(1940)+', -23112: 'anti-Sigma(1750)+', 203338: 'Omega(2250)-', 10551: 'chi_b0', -203326: 'anti-Xi(2030)0', -203322: 'anti-Xi(1690)0', -203316: 'anti-Xi(2030)+', -5214: 'anti-Sigma_b*0', 9030221: 'f_0(1500)', -203312: 'anti-Xi(1690)+', 32212: 'N(1650)+', 32214: 'Delta(1600)+', -5212: 'anti-Sigma_b0', -545: 'B_c2*-', 32224: 'Delta(1600)++', -543: 'B_c*-', -541: 'B_c-', 13222: 'Sigma(1660)+', -535: 'anti-B_s2*0', -533: 'anti-B_s*0', -531: 'anti-B_s0', 13224: 'Sigma(1670)+', -525: 'B_2*-', -523: 'B*-', -521: 'B-', 130553: 'Upsilon_1(2D)', 9000443: 'psi(4040)', -515: 'anti-B_2*0', 104322: 'Xi_c(2815)+', -513: 'anti-B*0', -511: 'anti-B0', -10325: 'K_2(1770)-', 30213: 'rho(3S)+', 300553: 'Upsilon(4S)', 12122: 'Delta(1900)+', 5212: 'Sigma_b0', -31214: 'anti-N(1720)0', -9042413: 'Z(4430)-', -13314: 'anti-Xi(1820)+', 20022: 'Cerenkov', 12212: 'N(1440)+', 12214: 'Delta(1700)+', -435: 'D_s2*-', -433: 'D_s*-', -431: 'D_s-', -425: 'anti-D_2*0', -423: 'anti-D*0', -421: 'anti-D0', 12218: 'N(1990)+', 22112: 'N(1535)0', -415: 'D_2*-', 22114: 'Delta(1920)0', -413: 'D*-', -411: 'D-', 30313: "K''*0", 22122: 'Delta(1910)+', 22124: 'N(1700)+', 30323: "K''*+", 12222: 'Delta(1900)++', -31114: 'anti-Delta(1600)+', 210551: 'chi_b0(3P)', 210553: 'h_b(3P)', 12224: 'Delta(1700)++', 30343: 'Xsd', -1000020030: 'anti-He3', 20113: 'a_10', 30363: 'Xss', -33122: 'anti-Lambda(1670)0', -4444: 'anti-Omega_ccc*--', -4434: 'anti-Omega_cc*-', -4432: 'anti-Omega_cc-', -329: 'K_4*-', -4424: 'anti-Xi_cc*--', -327: 'K_3*-', -4422: 'anti-Xi_cc--', -325: 'K_2*-', -12218: 'anti-N(1990)-', -323: 'K*-', -321: 'K-', -319: 'anti-K_4*0', -4414: 'anti-Xi_cc*-', -317: 'anti-K_3*0', -4412: 'anti-Xi_cc-', -315: 'anti-K_2*0', 22214: 'Delta(1920)+', -313: 'anti-K*0', -311: 'anti-K0', -4403: 'anti-cc_1', 22222: 'Delta(1910)++', 22224: 'Delta(1920)++', -10543: 'B_c1-', -1000010030: 'anti-triton', -10541: 'B_c0*-', -21212: 'anti-Delta(1910)0', -10533: 'anti-B_s10', -1000010020: 'anti-deuteron', -10531: 'anti-B_s0*0', -10523: 'B_1-', -10521: 'B_0*-', 120553: 'chi_b1(2P)', 30443: 'psi(3770)', -2: 'anti-u', -10513: 'anti-B_10', -10511: 'anti-B_0*0', 100443: 'psi(2S)', 20213: 'a_1+', 20223: 'f_1', -41214: 'anti-N(1900)0', 100311: 'K(1460)0', 100111: 'pi(2S)0', 100113: 'rho(2S)0', -4334: 'anti-Omega_c*0', -4332: 'anti-Omega_c0', 1000010030: 'triton', 110553: 'h_b(2P)', -4324: 'anti-Xi_c*-', -4322: "anti-Xi'_c-", 20443: 'chi_c1', -219: 'a_4(1970)-', -4314: 'anti-Xi_c*0', -217: 'rho_3(1690)-', -4312: "anti-Xi'_c0", -215: 'a_2-', 14122: 'Lambda_c(2593)+', -213: 'rho-', 5312: "Xi'_b-", -211: 'pi-', 100445: 'chi_c2(2P)', -4303: 'anti-cs_1', -4301: 'anti-cs_0', -12214: 'anti-Delta(1700)-', -10433: "D'_s1-", -10431: 'D_s0*-', -10423: 'anti-D_10', -10421: 'anti-D_0*0', -2228: 'anti-Delta(1950)--', -2226: 'anti-Delta(1905)--', -2224: 'anti-Delta--', -103112: 'anti-Sigma(2250)+', -2222: 'anti-Delta(1620)--', 10211: 'a_0(1450)+', 12116: 'N(1680)0', -10411: 'D_0*-', -2218: 'anti-Delta(1950)-', 10553: 'h_b', -2216: 'anti-N(1675)-', 20313: "K'_10", -2214: 'anti-Delta-', 20315: 'K_2(1820)0', -2212: 'anti-p-', 12126: 'Delta(1930)+', 10555: 'eta_b2(1D)', -2203: 'anti-uu_1', 30353: 'Xsu', -22212: 'anti-N(1535)-', 200555: 'chi_b2(3P)', 20333: "f'_1", 100211: 'pi(2S)+', 100213: 'rho(2S)+', -4232: 'anti-Xi_c-', 104314: 'Xi_c(2790)0', 100221: 'eta(2S)', 10111: 'a_0(1450)0', -4224: 'anti-Sigma_c*--', 10113: 'b_10', -4222: 'anti-Sigma_c--', 10115: 'pi_2(1670)0', 104324: 'Xi_c(2790)+', -4214: 'anti-Sigma_c*-', -4212: 'anti-Sigma_c-', -43122: 'anti-Lambda(1800)0', 100333: 'phi(1680)', -4203: 'anti-cu_1', -4201: 'anti-cu_0', 10223: 'h_1', -16: 'anti-nu_tau', -104122: 'anti-Lambda_c(2625)-', 10225: 'eta_2(1645)', -87: "anti-b'-hadron", -86: 'anti-t-hadron', -85: 'anti-b-hadron', -84: 'anti-c-hadron', -10323: 'K_1-', -82: 'anti-rndmflav', -10321: 'K_0*-', -2128: 'anti-N(2190)-', -11212: 'anti-Delta(1900)0', -2126: 'anti-Delta(1905)-', 10022: 'vpho', -2124: 'anti-N(1520)-', -10315: 'anti-K_2(1770)0', -2122: 'anti-Delta(1620)-', -10313: 'anti-K_10', 12216: 'N(1680)+', -10311: 'anti-K_0*0', -2118: 'anti-Delta(1950)0', -100421: 'anti-D(2S)0', -2116: 'anti-N(1675)0', 20413: "D'_1+", -2114: 'anti-Delta0', -2112: 'anti-n0', -20543: "B'_c1-", 12226: 'Delta(1930)++', -100413: 'D*(2S)-', -100411: 'D(2S)-', 20423: "D'_10", -2103: 'anti-ud_1', -2101: 'anti-ud_0', 20433: 'D_s1+', -44: 'Xu-', -20523: "B'_1-", -41: 'anti-R0', 100313: "K'*0", -38: 'Higgs--', -37: 'Higgs-', -4132: 'anti-Xi_c0', -34: "W'-", -20513: "anti-B'_10", 100321: 'K(1460)+', -5: 'anti-b', 10213: 'b_1+', -4122: 'anti-Lambda_c-', 10215: 'pi_2(1670)+', -24: 'W-', 100331: 'eta(1475)', 10221: "f'_0", -4114: 'anti-Sigma_c*0', -17: 'L+', -4112: 'anti-Sigma_c0', -15: 'tau+', -14: 'anti-nu_mu', -13: 'mu+', -12: 'anti-nu_e', -11: 'e+', -8: "anti-t'", -4103: 'anti-cd_1', -6: 'anti-t', -4101: 'anti-cd_0', -4: 'anti-c', -3: 'anti-s', -1: 'anti-d'}


