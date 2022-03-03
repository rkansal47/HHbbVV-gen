#!/usr/bin/python

import argparse
import os
from string import Template


def write_template(templ_file: str, out_file: str, templ_args: dict):
    """Write to ``out_file`` based on template from ``templ_file`` using ``templ_args``"""

    with open(templ_file, "r") as f:
        templ = Template(f.read())

    with open(out_file, "w") as f:
        f.write(templ.substitute(templ_args))


def main(args):
    tag = args.tag
    sample = args.sample

    locdir = f"condor/{tag}"
    os.system(f"mkdir -p {locdir}/logs")

    localcondor = f"{locdir}/submit_{sample}.jdl"
    executable = f"onestop_ul_{sample}.sh"
    localexecutable = f"{locdir}/{executable}"

    sample_dir = f"/store/user/lpcdihiggsboost/gen/{sample}/"

    odir = f"{sample_dir}/ULv1/{tag}/"
    odir_ul = f"{sample_dir}/ULv2/{tag}/"
    # odir_lhe = f"{sample_dir}/LHE/{tag}/"

    redirector = "root://cmseos.fnal.gov//"

    os.system(f"xrdfs {redirector} mkdir -p {odir}")
    os.system(f"xrdfs {redirector} mkdir -p {odir_ul}")

    print("Made EOS Directories")

    exe_templ_file = open(executable)
    exe_file = open(localexecutable, "w")
    for line in exe_templ_file:
        line = line.replace("OUTPUT_DIR", f"{redirector}{odir}")
        line = line.replace("OUTPUT_ULDIR", f"{redirector}{odir_ul}")
        # line = line.replace("OUTPUT_DIR_LHE", odir_lhe)
        exe_file.write(line)
    exe_file.close()
    exe_templ_file.close()

    proxy = os.environ["X509_USER_PROXY"]

    cwd = os.getcwd()

    seedfile = f"{locdir}/seed.txt"
    f = open(seedfile, "w")
    for i in range(args.start, args.end):
        f.write("%i\n" % i)
    f.close()

    condor_templ_file = open(f"submit_templ_{args.where}.jdl")
    condor_file = open(localcondor, "w")
    for line in condor_templ_file:
        line = line.replace("EXECUTABLE", localexecutable)
        line = line.replace("DIRECTORY", locdir)
        line = line.replace("LOCDIR", cwd)
        line = line.replace("SEEDFILE", seedfile)
        line = line.replace("PROXY", proxy)
        if args.mx:
            line = line.replace("MX", "%i" % args.mx)
        if args.my:
            line = line.replace("MY", "%i" % args.my)
        condor_file.write(line)
    condor_file.close()
    condor_templ_file.close()

    if args.submit:
        os.system("condor_submit %s" % localcondor)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", dest="tag", default="Test", help="process tag", type=str)
    parser.add_argument(
        "--where",
        default="lxplus",
        choices=["lpc", "lxplus"],
        help="submitting at lxplus or lpc",
        type=str,
    )
    parser.add_argument(
        "--sample",
        dest="sample",
        choices=["XHY", "jhu_HHbbWW", "pythia_HHbbWW", "jhu_HHbbZZ"],
        help="sample",
    )
    parser.add_argument(
        "--submit", dest="submit", action="store_true", help="submit jobs when created"
    )
    parser.add_argument("--start", dest="start", default=1, help="start seed >0", type=int)
    parser.add_argument("--end", dest="end", default=1000, help="endseed", type=int)
    parser.add_argument("--mx", dest="mx", default=None, help="mx", type=int)
    parser.add_argument("--my", dest="my", default=None, help="my", type=int)
    args = parser.parse_args()

    main(args)
