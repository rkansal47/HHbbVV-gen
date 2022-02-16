import FWCore.ParameterSet.Config as cms

#Link to datacards:
#https://github.com/cms-sw/genproductions/tree/master/bin/MadGraph5_aMCatNLO/cards/production/2017/13TeV/BulkGraviton_hh_granular
from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunes2017.PythiaCP5Settings_cfi import *
from Configuration.Generator.PSweightsPythia.PythiaPSweightsSettings_cfi import *

generator = cms.EDFilter("Pythia8GeneratorFilter",
    maxEventsToPrint = cms.untracked.int32(1),
    pythiaPylistVerbosity = cms.untracked.int32(1),
    filterEfficiency = cms.untracked.double(1.0),
    pythiaHepMCVerbosity = cms.untracked.bool(False),
    comEnergy = cms.double(13000.),
    RandomizedParameters = cms.VPSet(),
)

mpoints=[]
mpoints.append([1000, 125])

for point in mpoints:
    generator.RandomizedParameters.append(
        cms.PSet(
            ConfigWeight = cms.double(1),
            GridpackPath =  cms.string('/cvmfs/cms.cern.ch/phys_generator/gridpacks/2017/13TeV/madgraph/V5_2.6.5/BulkGraviton_hh_GF_HH_narrow/BulkGraviton_hh_GF_HH_narrow_M1000_slc7_amd64_gcc700_CMSSW_10_6_19_tarball.tar.xz'),
            ConfigDescription = cms.string('BulkGraviton_hh_GF_HH_narrow'),
            PythiaParameters = cms.PSet(
                pythia8CommonSettingsBlock,
                pythia8CP5SettingsBlock,
                pythia8PSweightsSettingsBlock,
                # processParameters = cms.vstring('25:onMode = off',
                #                                 '25:oneChannel = 1 0.33333 100 5 -5',
                #                                 '25:addChannel = 1 0.33333 100 4 -4',
                #                                 '25:addChannel = 1 0.11111 100 3 -3',
                #                                 '25:addChannel = 1 0.11111 100 2 -2',
                #                                 '25:addChannel = 1 0.11111 100 1 -1',
                #                                 'ResonanceDecayFilter:filter = on'
                # ),
		parameterSets = cms.vstring('pythia8CommonSettings',
                                    'pythia8CP5Settings',
                                    'pythia8PSweightsSettings',
                			        # 'processParameters',
		)
            )
        )
    )
