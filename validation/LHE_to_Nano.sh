#!/usr/bin/env bash

set -x
set -e

#source /cvmfs/cms.cern.ch/cmsset_default.sh

LHE_PATH=$1
NANOGEN_PATH=$2
NEVENTS=$3

if [ -z "$4" ]; then
    WORKDIR=${TMPDIR}
else
    WORKDIR=$4
fi
echo "Using ${WORKDIR} as working directory."

EDM_PATH=${WORKDIR}/edm.root

cmsDriver.py --python_filename ${WORKDIR}/lhe_edm.py --eventcontent LHE --datatier LHE \
    --fileout file:$EDM_PATH --conditions auto:mc --step NONE --filein file:$LHE_PATH \
    --no_exec --mc -n $NEVENTS

cmsDriver.py PhysicsTools/NanoAODTools/python/postprocessing/modules/reweighting/hadronizer.py \
    --filein file:$EDM_PATH --fileout $NANOGEN_PATH --mc --eventcontent NANOAODGEN \
    --datatier NANOAODSIM --conditions auto:mc --step GEN,NANOGEN --nThreads 10 \
    --python_filename ${WORKDIR}/edm_nano.py --no_exec -n $NEVENTS \
    --customise PhysicsTools/NanoAOD/nanogen_cff.pruneGenParticlesNano 
#PhysicsTools/NanoAOD/nanogen_cff.setLHEFullPrecision 

PRODMODE="GGF"
insert="process.rivetProducerHTXS.ProductionMode = '${PRODMODE}'"
sed -i "/^process = pruneGenParticlesNano(process).*/a ${insert}" ${WORKDIR}/edm_nano.py

cmsRun ${WORKDIR}/lhe_edm.py
cmsRun ${WORKDIR}/edm_nano.py
