# Example walk through - Going from a MadGraph process line to reweighted NanoAOD

The following will assume that you have already familiar with MadGraph and already know how to use it to generate MC for the process you are interested in. If you are not already familiar, the most important thing is that you know is how to write a proc_card.dat. I suggest first reading through the instructions for [EFT2Obs](https://github.com/ajgilbert/EFT2Obs). If you find that you need a bit more explanation then I suggest reading this [twiki tutorial](https://twiki.cern.ch/twiki/bin/view/CMSPublic/MadgraphTutorial) and/or looking at this more detailed [indico tutorial](https://indico.cern.ch/event/962610/?showDate=all&showSession=19).

In this example, we are interested in the SMEFT model and intend to reweight ggF Higgs boson events for different values of the Wilson coefficient $c_{HG}$. 

There are two steps to take. First, we will need to make the reweighting module for the SMEFT ggF process using [EFT2Obs](https://github.com/ajgilbert/EFT2Obs). Second, this nanoAOD tool will take that reweighting module and apply it to the inputted nanoAOD file to make a new nanoAOD file with the desired reweights.

Before following these instructions, make sure you have done the [initial setup](initial_setup.md).

## Step 1: Make reweighting module

Start from the EFT2Obs directory and make sure CMSSW is **not** set. Source the EFT2Obs environment script.

```
source env.sh
```

Make a new directory to hold the cards for our SMEFT ggF process. 

```
mkdir cards/ggF-SMEFTsim
```

Create the proc_card.dat in this new directory.

```
import model SMEFTsim_U35_MwScheme_UFO

generate g g > h QED=1 NP<=1
add process g g > h j QED=1 NP<=1

output ggF-SMEFTsim
```

Setup the process.

```
./scripts/setup_process.sh ggF-SMEFTsim
```

Create the config file, param card and reweight card.

```
python scripts/make_config.py -p ggF-SMEFTsim -o config_SMEFT_STXS.json \ 
--pars SMEFT:6 --def-val 0.01 --def-sm 0.0 --def-gen 0.0
python scripts/make_param_card.py -p ggF-SMEFTsim -c config_SMEFT_STXS.json \ 
-o cards/ggF-SMEFTsim/param_card.dat
python scripts/make_reweight_card.py config_SMEFT_STXS.json \ 
cards/ggF-SMEFTsim/reweight_card.dat
```

Create the standalone reweighting module
```
./scripts/setup_process_standalone.sh ggF-SMEFTsim
python scripts/make_standalone.py -p ggF-SMEFTsim -o rw_ggF-SMEFTsim \ 
-c config_SMEFT_STXS.json --rw-dir MG5_aMC_v2_6_7/ggF-SMEFTsim-standalone
```

## Step 2: Apply the reweighting to the nanoAOD

Here, we will apply the reweighting to this dataset:

```
/GluGluHToGG_M125_TuneCP5_13TeV-amcatnloFXFX-pythia8_storeWeights/RunIISummer19UL18NanoAODv2-106X_upgrade2018_realistic_v15_L1v1-v1/NANOAODSIM
```
and to this file particular:
```
/store/mc/RunIISummer19UL18NanoAODv2/GluGluHToGG_M125_TuneCP5_13TeV-amcatnloFXFX-pythia8_storeWeights/NANOAODSIM/106X_upgrade2018_realistic_v15_L1v1-v1/40000/9646BBBF-8A18-F345-9E84-A15B6BA628A8.root
```

To perform the reweighting, first move to the nanoAOD-tools directory and call `cmsenv`. Then we will use [run_reweighting.py](../scripts/run_reweighting.py). This script will take a nanoAOD file and a reweighting module and return a new nanoAOD file with the reweights in the new 'Reweights' branch. It is used in the following way:
```
python scripts/run_reweighting.py path/to/output path/to/NanoAOD_input.root path/to/rw_module
```
There are a number of further options/arguments that could be useful:
- `-N` specifies the number of entries to run over
- `-m` specifies the particular reweighting method to use. The default value is `LHE` which tells the script to use the LHEPart branches. To use the default GenPart method, use `-m GEN`. You can design your own methods which is described further [here](making_adjustments.md).
- `-v` tells the script to run in verbose mode.
- `--drop` tells the script to remove events which are not compatible with the reweighting module. For example, when an event contains a final state the module was not expecting. By default, in situations like this, the reweighting module will just return the SM weight for all reweights.
  
There are more (probably less useful) options that are inherited (and can be found) from [scripts/nano_postproc.py](../scripts/nano_postproc.py).

Before following these next instructions make sure to have a grid proxy: 
```
voms-proxy-init --voms cms
```
As this is the first time performing the reweighting we will begin by reweighting only 10 events and running in verbose mode:
```
python scripts/run_reweighting.py path/to/output \
 root://xrootd-cms.infn.it//store/mc/RunIISummer19UL18NanoAODv2/GluGluHToGG_M125_TuneCP5_13TeV-amcatnloFXFX-pythia8_storeWeights/NANOAODSIM/106X_upgrade2018_realistic_v15_L1v1-v1/40000/9646BBBF-8A18-F345-9E84-A15B6BA628A8.root \
 path/to/rw_module -N 10 -v
```

<details>
<summary>Click here to see the output of this command.</summary>
<p>

```
[mknight@lxplus740 NanoAODTools]$ python scripts/run_reweighting.py . root://xrootd-cms.infn.it//store/mc/RunIISummer19UL18NanoAODv2/GluGluHToGG_M125_TuneCP5_13TeV-amcatnloFXFX-pythia8_storeWeights/NANOAODSIM/106X_upgrade2018_realistic_v15_L1v1-v1/40000/9646BBBF-8A18-F345-9E84-A15B6BA628A8.root  ../../../../EFT2Obs/rw_ggF-SMEFTsim/ -N 10 -v
>> 1 parameters, 3 reweight points
>> LO Reweighting
>> Initialising modules...
>> Reusing working directory /eos/home-m/mknight/Standalone/tidying/EFT2Obs/rw_ggF-SMEFTsim
>> StandaloneReweight class initialized
>> Accepted PDG lists:
   - [21, 21, 25, 21]
   - [21, 21, 25]
Will write selected trees to .
Pre-select 10 entries out of 10 (100.00%)
>> Event with PDGs [21, 21, 25, 21, 21] does not match any known process
---------------------------------------------------------------------------
 Particle | status  | helicity |   | E       | P_x     | P_y     | P_z      
---------------------------------------------------------------------------
         g        -1      None         1277.6       0.0       0.0    1277.6
         g        -1      None           76.5       0.0       0.0     -76.5
    Higgs0         1      None         1191.8     -33.0      11.3    1184.8
         g         1      None           85.4       2.8       2.3      85.4
         g         1      None           76.7      30.1     -13.6     -69.2
[1.0, 1.0, 1.0]
 
>> Event with PDGs [21, 2, 25, 2, 21] does not match any known process
---------------------------------------------------------------------------
 Particle | status  | helicity |   | E       | P_x     | P_y     | P_z      
---------------------------------------------------------------------------
         g        -1      None          214.4       0.0       0.0     214.4
         u        -1      None         2250.2       0.0       0.0   -2250.2
    Higgs0         1      None         1207.8     -11.3      29.6   -1200.9
         u         1      None         1045.0      41.0     -16.0   -1044.1
         g         1      None          211.7     -29.7     -13.6     209.2
[1.0, 1.0, 1.0]
 
---------------------------------------------------------------------------
 Particle | status  | helicity |   | E       | P_x     | P_y     | P_z      
---------------------------------------------------------------------------
         g        -1      None          124.4       0.0       0.0     124.4
         g        -1      None          357.9       0.0       0.0    -357.9
    Higgs0         1      None          361.4     -31.4     -62.9    -331.7
         g         1      None          120.9      31.4      62.9      98.3
[1.0, 1.2051066150355456, 1.4293332410707515]
 
---------------------------------------------------------------------------
 Particle | status  | helicity |   | E       | P_x     | P_y     | P_z      
---------------------------------------------------------------------------
         g        -1      None          211.2       0.0       0.0     211.2
         g        -1      None           18.5       0.0       0.0     -18.5
    Higgs0         1      None          229.7       0.0       0.0     192.7
[1.0, 1.2066145544144442, 1.4326178848018922]
 
>> Event with PDGs [2, 2, 25, 2, 2] does not match any known process
---------------------------------------------------------------------------
 Particle | status  | helicity |   | E       | P_x     | P_y     | P_z      
---------------------------------------------------------------------------
         u        -1      None         2497.9       0.0       0.0    2497.9
         u        -1      None          205.0       0.0       0.0    -205.0
    Higgs0         1      None          770.0      -4.7      -5.5     759.7
         u         1      None         1732.4       8.3      29.2    1732.2
         u         1      None          200.5      -3.7     -23.6    -199.1
[1.0, 1.0, 1.0]
 
>> Event with PDGs [21, 21, 25, 21, 21, 21] does not match any known process
---------------------------------------------------------------------------
 Particle | status  | helicity |   | E       | P_x     | P_y     | P_z      
---------------------------------------------------------------------------
         g        -1      None         2121.6       0.0       0.0    2121.6
         g        -1      None          628.7       0.0       0.0    -628.7
    Higgs0         1      None         2023.4      69.8      18.5    2018.2
         g         1      None           99.4      18.6      27.4      93.8
         g         1      None          447.1     -71.5     -37.3    -439.7
         g         1      None          180.4     -16.8      -8.5    -179.4
[1.0, 1.0, 1.0]
 
>> Event with PDGs [2, 21, 25, 2, 21] does not match any known process
---------------------------------------------------------------------------
 Particle | status  | helicity |   | E       | P_x     | P_y     | P_z      
---------------------------------------------------------------------------
         u        -1      None         2157.5       0.0       0.0    2157.5
         g        -1      None          424.9       0.0       0.0    -424.9
    Higgs0         1      None          232.4       8.9      -8.8     195.5
         u         1      None         1943.6       1.6      18.8    1943.5
         g         1      None          406.5     -10.5     -10.1    -406.2
[1.0, 1.0, 1.0]
 
---------------------------------------------------------------------------
 Particle | status  | helicity |   | E       | P_x     | P_y     | P_z      
---------------------------------------------------------------------------
         g        -1      None          504.0       0.0       0.0     504.0
         g        -1      None            7.8       0.0       0.0      -7.8
    Higgs0         1      None          511.8       0.0       0.0     496.3
[1.0, 1.2065789469173653, 1.4325402869550874]
 
---------------------------------------------------------------------------
 Particle | status  | helicity |   | E       | P_x     | P_y     | P_z      
---------------------------------------------------------------------------
         g        -1      None           11.9       0.0       0.0      11.9
         g        -1      None          586.4       0.0       0.0    -586.4
    Higgs0         1      None          516.2     -25.9      21.5    -499.7
         g         1      None           82.0      25.9     -21.5     -74.8
[1.0, 1.1878151942955253, 1.391783429098858]
 
---------------------------------------------------------------------------
 Particle | status  | helicity |   | E       | P_x     | P_y     | P_z      
---------------------------------------------------------------------------
         g        -1      None          301.6       0.0       0.0     301.6
         g        -1      None           13.0       0.0       0.0     -13.0
    Higgs0         1      None          314.6       0.0       0.0     288.7
[1.0, 1.2132839950433434, 1.4471691259297452]
 
Processed 10 preselected entries from root://xrootd-cms.infn.it//store/mc/RunIISummer19UL18NanoAODv2/GluGluHToGG_M125_TuneCP5_13TeV-amcatnloFXFX-pythia8_storeWeights/NANOAODSIM/106X_upgrade2018_realistic_v15_L1v1-v1/40000/9646BBBF-8A18-F345-9E84-A15B6BA628A8.root (10 entries). Finally selected 10 entries
Done ./9646BBBF-8A18-F345-9E84-A15B6BA628A8_Skim.root
Total time 16.3 sec. to process 10 events. Rate = 0.6 Hz.
```

</p>
</details> 

The verbose mode provides a summary of each event and the calculated reweights are printed below it. In this example, a simple process line has been used that includes only the 0j and 1j ggF processes. However, you can see that there exist events with >1 jets which the reweighting module cannot reweight. In such situations, the nominal weight will be given for each reweighting point. If you wanted to reweight these ggF events properly I would suggest having a proc_card.dat that included also a 2j process such that the majority of possible events are accounted for. 

You can follow these steps for your own process and model of interest and check that the reweighting module can account for all possible events that will show up in the NanoAOD file. Once you are happy, you can remove `-N 10 -v` from the command and then the script will run over the whole file.


