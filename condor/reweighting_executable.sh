#!/bin/bash

set -x
#set -e

nanoAODTools_dir=$1
outDir=$2
in_file=$3
rw_path=$4
n_start=$5
n_entries=$6
method=$7

#if [[ -n $8 ]]; then
#    export X509_USER_PROXY=$8
#    voms-proxy-info -all
#    voms-proxy-info -all -file $8
#fi

if [[ -n $8 && -n $9 ]]; then
    ClusterId=$8
    ProcId=$9
else
    ClusterId=local
    ProcId=run
fi

cd $nanoAODTools_dir
source /cvmfs/cms.cern.ch/cmsset_default.sh 
eval `scramv1 runtime -sh`

postfix=_reweighted_${ClusterId}_${ProcId}

python scripts/run_reweighting.py ${TMPDIR} ${in_file} ${rw_path} --first-entry ${n_start} -N ${n_entries} -s ${postfix} -m ${method} --drop

mkdir -p ${outDir}
cp ${TMPDIR}/*${postfix}.root ${outDir}/

#split=$(echo $in_file | tr "/" "\n")
#for s in $split
#do
#    filename=$s
#done
