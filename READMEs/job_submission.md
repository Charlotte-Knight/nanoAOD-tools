# Job submission

It's possible to run the event-ID skimming and reweighting scripts on condor. The intention is to allow running of multiple datasets at a time. It does not parallelise within a dataset by for example, submitting a job for every file. If neccessary, this functionality can be added in future. For now, running over a whole dataset takes O(hours) and I recommend running with `JobFlavour = workday`.

## Event-ID skimming

For the event-ID skimming you do this by running the same command line as you would interactively but adding the `--job-json` option. For example:

```
python eventIDSkimming/eventID_skim.py theDataset eventIDs.csv -o output.root --job-json job_submission.json
```

You can repeat this and add successive jobs to the json file like:

```
python eventIDSkimming/eventID_skim.py theDataset_2 eventIDs_2.csv -o output_2.root --job-json job_submission.json
```
and continue to do this until all jobs you want to submit are added.

Before submitting to condor, you need to generate a grid proxy. You can begin to do that by running:

```
voms-proxy-init --voms cms
```
which will output something like
```
Contacting voms2.cern.ch:15002 [/DC=ch/DC=cern/OU=computers/CN=voms2.cern.ch] "cms"...
Remote VOMS server contacted succesfully.

Created proxy in /tmp/x509up_u140261.

Your proxy is valid until Fri Apr 08 01:16:03 CEST 2022
```
Copy this file onto a permanent space, e.g. the NanoAODTools directory.
```
cp /tmp/x509up_u140261 x509up
```

Now that we have the grid proxy you can convert this json into a directory containing a .sub file to submit to condor. 
```
python condor/skimmingJsonToSub.py job_submission.json ~/private/condor/test_job x509up
```
The second argument is the directory containing the .sub file. It must be an AFS directory because you cannot submit to condor from eos. The last argument should point to where you saved your grid proxy.

Now go to the directory and submit

```
pushd ~/private/condor/test_job
condor_submit submit.sub
popd
```

## Reweighting

Submitting reweighting to condor is done in the exact same way, using the `--job-json` argument and using `reweightingJsonToSub.py` instead of `skimmingJsonToSub.py`. You also do not need to worry about the grid proxy.

## Checking jobs

There's helpful little [script](../eventIDSkimming/check_jobs.py) for checking your jobs ran correctly. It will recursively search within a directory looking for root files. It will then attempt to open the root file and tell you how many events are in it.

```
$ ls test
test_ggh_skim.root

$ python eventIDSkimming/check_jobs.py test
test/test_ggh_skim.root:  okay 
 0.300k events
```