# Plotting reweighted distributions

After reweighting your NanoAOD, you may wish to plot some distributions for different reweighting points. In some cases, it is important that a variable's distribution does not change under an EFT, e.g. the diphoton mass in a H->gg analysis. The [shape_plots.py](../eventIDSkimming/shapePlots.py) script exists for this purpose. It will plot the distribution for a variable under the SM hypothesis and for every reweighting point in the NanoAOD.

It is ran like:
```
python eventIDSkimming/shapePlots.py reweighted_nanoaod.root variable_name
```
where `variable_name` corresponds to the variable/branch in the NanoAOD which you would like to plot. Options for this script include:
- `--weight-branch` By default, standalone reweighting using the 'genWeight' branch as the original weights to scale. Use this option to specify a different branch to act as the original weight.
- `--config` path to the reweighting module config.json file. If specified, information about the different reweighting points will be given.
- `--range` the range of the histogram, e.g. (100,150)
- `--binNumber` the number of bins in the histogram
- `--xlabel` for the histogram
- `--save-path` directory to save the plots to