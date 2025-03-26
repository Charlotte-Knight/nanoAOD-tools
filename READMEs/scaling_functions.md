# Deriving STXS scaling functions

[EFT2Obs](https://github.com/ajgilbert/EFT2Obs) is a framework designed primarily to derive scaling functions for EFT studies. It is possible to use this standalone reweighting and feed the output into the EFT2Obs framework to derive scaling functions. The advantage of doing this - as opposed to only using EFT2Obs - is that if you are reweighting fully-simulated NanoAOD, you can apply reco-level selection criteria such that the derived scaling functions take acceptance effects into account.

The EFT2Obs workflow can be summarised as:
1. Define process and reweighting points with the proc_card.dat and reweight_card.dat .
2. Make a gridpack from these cards.
3. Produce events with this gridpack. These events are reweighted, showered by Pythia, and are categorised by Rivet. The output is given by a yoda file which is essentially a collection of histograms.
4. Given this yoda file, the [get_scaling.py](../equationExtraction/get_scaling.py) script is used to derive the scaling functions.

In comparison, the standalone reweighting workflow is:
1. Define process and reweighting points with the proc_card.dat and reweight_card.dat .
2. Produce standalone reweighting moduke.
3. Find some NanoAOD generated with the same process. This will probably be a centrally-produced dataset.
4. Reweight this nanoAOD according to instructions in the [walkthrough tutorial](walkthrough.md).
5. Use [nanoToYoda.py](../equationExtraction/nanoToYoda.py) to convert the reweighted NanoAOD to a yoda file.
6. Extract the scaling equations using [get_scaling.py](../equationExtraction/get_scaling.py).

Deriving scaling equations for particular STXS bins can be done by using the STXS classification that is available in centrally-produced NanoAOD. The [nanoToYoda.py](../equationExtraction/nanoToYoda.py) script can read the STXS tags and bin the events accordingly in the yoda file. The script can actually use any appropriate branch in the NanoAOD to bin the events. Therefore, it is possible to write an analysis that runs over the reweighted NanoAOD and adds a new branch that corresponds to whatever binning you would like. For example, you could define 10 bins, and if an event lands in the first bin, you would fill that branch with a "1". If it was the second bin, fill it with "2" etc. 

You may want to derive equations for particular analysis categories. This can be more tricky since the analysis can take a long time to write in the NanoAOD framework. An alternative to writing an analysis is the event ID skimming [approach](event_id_skimming.md) that would be performed between steps 3 and 4 in the standalone reweighting workflow.

NOTE: the functionality of the [nanoToYoda.py](../equationExtraction/nanoToYoda.py), [get_scaling.py](../equationExtraction/get_scaling.py) and [convert_EFT2Obs_json.py](../equationExtraction/convert_EFT2Obs_json.py) are now combined into one script called [nanoToJson.py](../equationExtraction/nanoToJson.py). The old scripts are still in the repository and the original tutorial is kept since the explanations are still relevant. I recommend reading Example 1-3 and then the last section which is specific to[nanoToYoda.py](../equationExtraction/nanoToYoda.py).

## Example 1: STXS equations for the GGH process

Follow the [walkthrough tutorial](walkthrough.md) which will take you through steps 1-4 in the standalone workflow described above.

Now that we have some reweighted GGH NanoAOD events, we will use the [nanoToYoda.py](../equationExtraction/nanoToYoda.py) to convert the reweighted NanoAOD to a yoda file with:
```
python equationExtraction/nanoToYoda.py ggH_reweighted_nanoAOD.root ggh.yoda
```
The options which are worth mentioning at this point include:
- `--tag-branch` tells the script which branch of the NanoAOD to use for tagging/binning the events. The default is 'HTXS_stage1_2_cat_pTjet30GeV' which is why it is actually not needed for this example.
- `--inclusive` tells the script to treat every event as being in the same bin. This is useful for deriving an inclusive scaling equation.
- `--weight-branch` specifies which branch of NanoAOD to act as the SM weights. By default this is 'genWeight' branch.

Extracting equations from the yoda file is done by:
```
python equationExtraction/get_scaling.py -c rw_module/config.json -i ggh.yoda \
  --hist "/MyHist" --save json
```
where config file is the same one you would have made in the [walkthrough tutorial](walkthrough.md). It can also be found in the reweighting module directory. The equations are given in a json file. Converting this into a better format is done with:
```
python equationExtraction/convert_EFT2Obs_json.py MyHist.json MyHist_converted.json
```
Options for this script include:
- `--key` path to a json file which gives a name to every bin. The converted json will use these names. See [here](../equationExtraction/tagKeys/HTXS_stage1_2_cat_pTjet30GeV.json) for an example.
- `--relative-threshold` if set, the script will remove terms where the coefficients are, as a fraction to the biggest coefficient, smaller than the threshold. This is done on a bin-by-bin basis. The option is useful for removing terms that are unimportant, the default threshold is 0.001.

## Example 2: Deriving analysis category equations

If following the event ID skimming [approach](event_id_skimming.md), then your reweighted NanoAOD will contain a branch named 'category'. Therefore, producing category scaling equations can be done by repeating the steps in example 1 except including `--tag-branch category` when running [nanoToYoda.py](../equationExtraction/nanoToYoda.py).

## Example 3: Deriving process x category equations

You may want to bin by both process and category, e.g. STXS_bin0_CAT0, STXS_bin0_CAT1, ..., STXS_bin1_CAT0, ... STXS_binN_CATM. This can be achieved by running:
```
python equationExtraction/nanoToYoda.py ggH_reweighted_nanoAOD.root ggh.yoda \ 
  --tag-branch HTXS_stage1_2_cat_pTjet30GeV --tag-branch2 category \ 
  --keys key1.json,key2.json --key-output key1_key2.json
```
The `--tag-branch` arguments tell the script which branches to bin with. The `--keys` are json files that give names to each bin (see [here](../equationExtraction/tagKeys/HTXS_stage1_2_cat_pTjet30GeV.json)). The script will create a new key.json file with names like STXS_bin0_CAT0 etc. that can be used in [convert_EFT2Obs_json.py](../equationExtraction/convert_EFT2Obs_json.py).

Repeat the [get_scaling.py](../equationExtraction/get_scaling.py) and [convert_EFT2Obs_json.py](../equationExtraction/convert_EFT2Obs_json.py) commands:
```
python equationExtraction/get_scaling.py -c rw_module/config.json -i ggh.yoda \
  --hist "/MyHist" --save json

python equationExtraction/convert_EFT2Obs_json.py MyHist.json MyHist_converted.json \
  --key key1_key2.json
```

## nanoToJson

The [nanoToYoda.py](../equationExtraction/nanoToYoda.py) script uses the same arguments used in the scripts described in Examples 1-3. For example, to create STXS stage 1.2 equations for the ggH example you could simply do:
```
python equationExtraction/nanoToJson.py rw_module/config.json ggH_reweighted_nanoAOD.root 
```
This will create a json file `ggH_reweighted_nanoAOD.json` in your working directory. The output directory can be specified with `--outputDir`.

You could do the process x category equations with:
```
python equationExtraction/nanoToJson.py rw_module/config.json ggH_reweighted_nanoAOD.root
  --tag-branch HTXS_stage1_2_cat_pTjet30GeV --tag-branch2 category \ 
  --keys key1.json,key2.json --outputDir equations
```

There are a few additional features with [nanoToYoda.py](../equationExtraction/nanoToYoda.py) as well. 
1. You can feed in multiple root files to be converted (equivalent to running the script separately on every file)
```
python equationExtraction/nanoToJson.py rw_module/config.json ggH_reweighted_nanoAOD.root VH_reweighted_nanoAOD.root ...
```
2. It will create uncertainties for each term using the bootstrap method. You can use the `--nBootstrap' option to specify how many resamples to use, the default is 5.
3. You can use the `--stage0` option to create an STXS stage 0 equation
```
python equationExtraction/nanoToJson.py rw_module/config.json ggH_reweighted_nanoAOD.root --key equationExtraction/tagKeys/HTXS_stage1_2_cat_pTjet30GeV.json  --stage0 GG2H
```