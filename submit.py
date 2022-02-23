#!/usr/bin/python

import argparse
import os

def main(args):
    locdir = "condor/" + args.tag
    tag = args.tag
    sample = args.sample
    os.system(f"mkdir -p {locdir}/logs")
    localcondor = f"{locdir}/submit_{sample}.jdl"
    executable = f"onestop_ul_{sample}.sh"
    localexecutable = f"{locdir}/{executable}"
    odir = f"root://cmseos.fnal.gov//store/user/lpcdihiggsboost/genHHbbVV/ULv1/{tag}/"
    odir_ul = f"root://cmseos.fnal.gov//store/user/lpcdihiggsboost/genHHbbVV/ULv2/{tag}/"

    exe_templ_file = open(executable)
    exe_file = open(localexecutable, "w")
    for line in exe_templ_file:
        line = line.replace("OUTPUT_DIR", odir)
        line = line.replace("OUTPUT_ULDIR", odir_ul)
        exe_file.write(line)
    exe_file.close()
    exe_templ_file.close()

    proxy = os.environ["X509_USER_PROXY"]

    cwd = os.getcwd()
    
    seedfile = f"{locdir}/seed.txt"
    f = open(seedfile, "w")
    for i in range(1):
        f.write("%i\n"%i)
    f.close()
            
    condor_templ_file = open("submit_templ.jdl")
    condor_file = open(localcondor, "w")
    for line in condor_templ_file:
        line = line.replace("EXECUTABLE", localexecutable)
        line = line.replace("DIRECTORY", locdir)
        line = line.replace("LOCDIR", cwd)
        line = line.replace("SEEDFILE", seedfile)
        line = line.replace("PROXY", proxy)
        condor_file.write(line)
    condor_file.close()
    condor_templ_file.close()

    if args.submit:
        os.system('condor_submit %s' % localcondor)    

if __name__ == "__main__":
            
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag",       dest="tag",       default="Test",                help="process tag", type=str)
    parser.add_argument('--sample',    dest='sample',    choices=["jhu_HHbbVV","pythia_HHbbVV"], help='sample')
    parser.add_argument("--submit",    dest='submit',    action='store_true',           help="submit jobs when created")
    args = parser.parse_args()

    main(args)
