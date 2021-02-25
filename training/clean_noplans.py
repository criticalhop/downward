import sys
import os
import re
import os
import pwd
from shutil import copyfileobj, copy
import bz2
import string

def get_username():
    return pwd.getpwuid( os.getuid() )[ 0 ]

filt = re.compile("^"+string.ascii_letters+string.digits+"-_:=")
transr = re.compile("([^\\[^\\]^\\s]+)")

def lisp_to_list(v):
    return [eval(",".join(transr.sub(r'"\1"' ,filt.sub('',v).replace("(","[").replace(")","]")).split()))]

cur_dir = sys.argv[1]
out_dir = sys.argv[2]

all_files = os.listdir(cur_dir)

to_move = []

for i, hyperc_rundir in enumerate(all_files):
    good = True
    abspath = f"{cur_dir}/{hyperc_rundir}"
    print(f"Entering {abspath}, processing {i} of {len(all_files)}")
    if not os.path.isdir(abspath): continue
    # TODO HERE: process problem and domain files
    # lowercase everything for prolog!!!

    # 1. prepare safe translation map for predicates
    domain_file = f"{cur_dir}/{hyperc_rundir}/domain.pddl"
    problem_file = f"{cur_dir}/{hyperc_rundir}/problem.pddl"

    try:
        for solve_attempt_dir in os.listdir(abspath):
            abssubpath = f"{abspath}/{solve_attempt_dir}"
            planfile = f"{abssubpath}/out.plan"
            print(f"Entering {abssubpath}")
            if not os.path.isfile(planfile):
                good = False
                break
    except FileNotFoundError:
        good = False
    if good:
        to_move.append(hyperc_rundir)

import shutil

for hyperc_rundir in to_move:
    abspath = f"{cur_dir}/{hyperc_rundir}"
    topath = f"{out_dir}/{hyperc_rundir}"
    print("Moving", abspath, topath)
    shutil.move(abspath, topath)

