#!/bin/bash

set -x
#set -e

nanoAODTools_dir=$1
dataset=$2
csv=$3
output=$4
extraBranches=$5
extraCollections=$6
doTest=$7
keepNoTag=$8
NoTagIndex=$9
inclusiveSample=${10}

if [[ -n ${11} ]]; then
    export X509_USER_PROXY=${11}
    voms-proxy-info -all
    voms-proxy-info -all -file ${11}
fi

if [[ -n ${12} && -n ${13} ]]; then
    ClusterId=${12}
    ProcId=${13} 
else
    ClusterId=local
    ProcId=run
fi

cd $nanoAODTools_dir
source /cvmfs/cms.cern.ch/cmsset_default.sh 
eval `scramv1 runtime -sh`

postfix=_Skimmed_${ClusterId}_${ProcId}

options=""
if [[ "$extraBranches" != "None" ]]; then
  options="${options} --extraBranches ${extraBranches}"
fi
if [[ "$extraCollections" != "None" ]]; then
  options="${options} --extraCollections ${extraCollections}"
fi
if [[ "$doTest" != "None" ]]; then
  options="${options} --test"
fi
if [[ "$keepNoTag" != "None" ]]; then
  options="${options} --keepNoTag"
fi
if [[ "$NoTagIndex" != "None" ]]; then
  options="${options} --NoTagIndex ${NoTagIndex}"
fi
if [[ "$inclusiveSample" != "None" ]]; then
  options="${options} --inclusiveSample $inclusiveSample}"
fi

echo ${options}

python eventIDSkimming/eventID_skim.py ${dataset} ${csv} -o ${output} ${options}

#mkdir -p ${outDir}
#cp ${TMPDIR}/*${postfix}.root ${outDir}/

#split=$(echo $in_file | tr "/" "\n")
#for s in $split
#do
#    filename=$s
#done
