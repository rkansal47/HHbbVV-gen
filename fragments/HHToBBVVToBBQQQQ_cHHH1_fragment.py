import FWCore.ParameterSet.Config as cms

externalLHEProducer = cms.EDProducer(
    "ExternalLHEProducer",
    args=cms.vstring(
        "/cvmfs/cms.cern.ch/phys_generator/gridpacks/slc6_amd64_gcc700/13TeV/powheg/V2/ggHH_EWChL_NNPDF31_13TeV_M125_cHHH1/v3/ggHH_EWChL_slc6_amd64_gcc700_CMSSW_10_2_5_patch1_my_ggHH_EWChL.tgz"
    ),
    nEvents=cms.untracked.uint32(10),
    numberOfParameters=cms.uint32(1),
    outputFile=cms.string("cmsgrid_final.lhe"),
    scriptName=cms.FileInPath(
        "GeneratorInterface/LHEInterface/data/run_generic_tarball_cvmfs_jhu.sh"
    ),
)

from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunes2017.PythiaCP5Settings_cfi import *
from Configuration.Generator.PSweightsPythia.PythiaPSweightsSettings_cfi import *
from Configuration.Generator.Pythia8PowhegEmissionVetoSettings_cfi import *

generator = cms.EDFilter(
    "Pythia8HadronizerFilter",
    maxEventsToPrint=cms.untracked.int32(1),
    pythiaPylistVerbosity=cms.untracked.int32(1),
    filterEfficiency=cms.untracked.double(1.0),
    pythiaHepMCVerbosity=cms.untracked.bool(False),
    comEnergy=cms.double(13000.0),
    PythiaParameters=cms.PSet(
        pythia8CommonSettingsBlock,
        pythia8CP5SettingsBlock,
        pythia8PSweightsSettingsBlock,
        pythia8PowhegEmissionVetoSettingsBlock,
        processParameters=cms.vstring(
            "POWHEG:nFinal = 2",
            "25:onMode = off",
            "25:onIfMatch = 5 -5",
            "ResonanceDecayFilter:filter = on",
        ),
        parameterSets=cms.vstring(
            "pythia8CommonSettings",
            "pythia8CP5Settings",
            "pythia8PSweightsSettings",
            "pythia8PowhegEmissionVetoSettings",
            "processParameters",
        ),
    ),
)
