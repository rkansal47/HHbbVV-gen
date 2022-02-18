#!/bin/bash -x

if [ -d /afs/cern.ch/user/${USER:0:1}/$USER ]; then
  export HOME=/afs/cern.ch/user/${USER:0:1}/$USER # crucial on lxplus condor but cannot set on cmsconnect!
fi
env

# example configuration 50 0 1 3
NEVENT=$1
SEED=$2 # no use here
NTHREAD=$3
FRAGMENT=fragments/HHToBBVVToBBQQQQ_cHHH1_fragment.py
CMSTARBALL=genmodules.tgz
LHESCRIPT=run_generic_tarball_cvmfs_jhu.sh
LHEEXTSCRIPT=lhe_modifier.py
[ -f $FRAGMENT ] || exit $? ;

WORKDIR=`pwd`

export SCRAM_ARCH=slc7_amd64_gcc700
export RELEASE=CMSSW_10_6_29
export RELEASE_HLT=CMSSW_9_4_14_UL_patch1
source /cvmfs/cms.cern.ch/cmsset_default.sh

if [ -r $RELEASE/src ] ; then
  echo release $RELEASE already exists
else
  scram p CMSSW $RELEASE
fi
cd $RELEASE/src
eval `scram runtime -sh`

######## Plugin the JHUGen ########
# git cms-addpkg GeneratorInterface/Core
# git cms-addpkg GeneratorInterface/LHEInterface
tar xzf $WORKDIR/$CMSTARBALL
sed -i "s/run_generic_tarball_cvmfs/run_generic_tarball_cvmfs_jhu/g" GeneratorInterface/Core/src/BaseHadronizer.cc
cp $WORKDIR/$LHESCRIPT GeneratorInterface/LHEInterface/data/$LHESCRIPT
cp $WORKDIR/$LHEEXTSCRIPT GeneratorInterface/LHEInterface/data/$LHEEXTSCRIPT
chmod +x GeneratorInterface/LHEInterface/data/$LHESCRIPT
# git cms-checkdeps -a # to save time because we don't change much of the code

######## (END) ########

mkdir -p Configuration/GenProduction/python/
cp $WORKDIR/$FRAGMENT Configuration/GenProduction/python/
# replace the event number (no __NEVENT__ in this fragment)
sed "s/__NEVENT__/$NEVENT/g" -i Configuration/GenProduction/python/$FRAGMENT
eval `scram runtime -sh`
scram b -j $NTHREAD

cd $WORKDIR

# following workflows copied from https://cms-pdmv.cern.ch/mcm/chained_requests?prepid=JME-chain_RunIISummer19UL17GEN_flowRunIISummer19UL17SIM_flowRunIISummer19UL17DIGIPremix_flowRunIISummer19UL17HLT_flowRunIISummer19UL17RECO_flowRunIISummer19UL17MiniAOD_flowRunIISummer19UL17NanoAOD-00008&page=0&shown=15
# note this is a deprecated routine

# begin LHEGEN
# SEED=$(($(date +%s) % 100000 + 1)) use seed from input argument

FRAGMENT0=(${FRAGMENT//\// })
FRAGMENT0=${FRAGMENT0[-1]}
cmsDriver.py Configuration/GenProduction/python/$FRAGMENT0 --python_filename JME-RunIISummer19UL17GEN-00016_1_cfg.py --eventcontent RAWSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN --fileout file:lhegen.root --conditions 106X_mc2017_realistic_v6 --beamspot Realistic25ns13TeVEarly2017Collision --customise_commands "process.source.numberEventsInLuminosityBlock = cms.untracked.uint32(200)"\\nprocess.source.numberEventsInLuminosityBlock="cms.untracked.uint32(100)" --step GEN --geometry DB:Extended --era Run2_2017 --mc --nThreads $NTHREAD -n $NEVENT || exit $? ;

# begin SIM
cmsDriver.py  --python_filename JME-RunIISummer19UL17SIM-00010_1_cfg.py --eventcontent RAWSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM --fileout file:sim.root --conditions 106X_mc2017_realistic_v6 --beamspot Realistic25ns13TeVEarly2017Collision --step SIM --geometry DB:Extended --filein file:lhegen.root --era Run2_2017 --runUnscheduled --mc --nThreads $NTHREAD -n $NEVENT || exit $? ;

# begin DRPremix
cmsDriver.py  --python_filename JME-RunIISummer19UL17DIGIPremix-00010_1_cfg.py --eventcontent PREMIXRAW --customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM-DIGI --fileout file:digi.root --pileup_input "dbs:/Neutrino_E-10_gun/RunIISummer20ULPrePremix-UL17_106X_mc2017_realistic_v6-v3/PREMIX" --conditions 106X_mc2017_realistic_v6 --step DIGI,DATAMIX,L1,DIGI2RAW --procModifiers premix_stage2 --geometry DB:Extended --filein file:sim.root --datamix PreMix --era Run2_2017 --runUnscheduled --mc --nThreads $NTHREAD -n $NEVENT > digi.log 2>&1 || exit $? ; # too many output, log into file

# begin HLT (UL only)
if [ -r $RELEASE_HLT/src ] ; then
  echo release $RELEASE_HLT already exists
else
  scram p CMSSW $RELEASE_HLT
fi
cd $RELEASE_HLT/src
eval `scram runtime -sh`
cd $WORKDIR
cmsDriver.py  --python_filename JME-RunIISummer19UL17HLT-00020_1_cfg.py --eventcontent RAWSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM-RAW --fileout file:hlt.root --conditions 94X_mc2017_realistic_v15 --customise_commands 'process.source.bypassVersionCheck = cms.untracked.bool(True)' --step HLT:2e34v40 --geometry DB:Extended --filein file:digi.root --era Run2_2017 --mc --nThreads $NTHREAD -n $NEVENT || exit $? ;

# begin RECO
if [ -r $RELEASE/src ] ; then
  echo release $RELEASE already exists
else
  scram p CMSSW $RELEASE
fi
cd $RELEASE/src
eval `scram runtime -sh`
cd $WORKDIR
cmsDriver.py  --python_filename JME-RunIISummer19UL17RECO-00020_1_cfg.py --eventcontent AODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier AODSIM --fileout file:reco.root --conditions 106X_mc2017_realistic_v6 --step RAW2DIGI,L1Reco,RECO,RECOSIM --geometry DB:Extended --filein file:hlt.root --era Run2_2017 --runUnscheduled --mc --nThreads $NTHREAD -n $NEVENT || exit $? ;

# begin MiniAOD and MiniAODv2 (in 20UL config)
cmsDriver.py  --python_filename JME-RunIISummer19UL17MiniAOD-00020_1_cfg.py --eventcontent MINIAODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier MINIAODSIM --fileout file:miniaod.root --conditions 106X_mc2017_realistic_v6 --step PAT --geometry DB:Extended --filein file:reco.root --era Run2_2017 --runUnscheduled --mc --nThreads $NTHREAD -n $NEVENT || exit $? ;

cmsDriver.py  --python_filename JME-RunIISummer19UL17MiniAOD-00020_1_cfg.py --eventcontent MINIAODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier MINIAODSIM --fileout file:miniaod_20ul.root --conditions 106X_mc2017_realistic_v9 --step PAT --procModifiers run2_miniAOD_UL --geometry DB:Extended --filein file:reco.root --era Run2_2017 --runUnscheduled --mc --nThreads $NTHREAD -n $NEVENT || exit $? ;

# mv wmlhegs.root wmlhegs_${SEED}.root
# mv miniaod.root miniaod_${SEED}.root
# mv miniaod_20ul.root miniaod_20ul_${SEED}.root


############ Start DNNTuples ############
# use CMSSW_11_1_0_pre8 which has Puppi V14
# export SCRAM_ARCH=slc7_amd64_gcc820
# scram p CMSSW CMSSW_11_1_0_pre8
# cd CMSSW_11_1_0_pre8/src
# eval `scram runtime -sh`
#
# git cms-addpkg PhysicsTools/ONNXRuntime
# # clone this repo into "DeepNTuples" directory
# git clone https://github.com/colizz/DNNTuples.git DeepNTuples -b dev-UL-hww
# # Use a faster version of ONNXRuntime
# $CMSSW_BASE/src/DeepNTuples/Ntupler/scripts/install_onnxruntime.sh
# scram b -j $NTHREAD
#
# cd DeepNTuples/Ntupler/test/
# cmsRun DeepNtuplizerAK8.py inputFiles=file:${WORKDIR}/miniaod.root
# mv output.root ${WORKDIR}/output.root
