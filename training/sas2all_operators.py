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

if len(sys.argv) > 1:
    cur_dir = sys.argv[1]
else:
    cur_dir = f"/tmp/hyperc/{get_username()}"


def clean_id(strid):
    return re.sub(r"[0-9]{15}", "_NNN_", strid)


def clean_pc_list(pc_list):
    # TODO: use a translation table from fixing predicates to do this
    for precondition in pc_list:
        if precondition[0] == "not":
            precondition[1][0] = clean_id(precondition[1][0])
        else:
            precondition[0] = clean_id(precondition[0])

all_files = os.listdir(cur_dir)

for i, hyperc_rundir in enumerate(all_files):
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
            # fd_i = open(sys.argv[1])
            abssubpath = f"{abspath}/{solve_attempt_dir}"
            print(f"Entering {abssubpath}")
            if not os.path.isdir(abssubpath): continue
            output_sas_file = f"{abssubpath}/output.sas"
            all_operators_file = f"{abspath}/all_operators"
            fd_i = open(output_sas_file)
            fd_o = open(all_operators_file, "w+")

            is_op = 0
            print("Processing", output_sas_file)
            for l in fd_i:
                if not is_op:
                    if l.startswith("begin_operator"):
                        is_op = 1
                else:
                    opl = l.split()
                    # op_schema_name = clean_id(opl[0])
                    op_schema_name = (opl[0])
                    op_arguments = ",".join(opl[1:])
                    all_op_line = f"{op_schema_name}({op_arguments})\n"
                    fd_o.write(all_op_line)
                    is_op = 0

            fd_i.close()
            fd_o.close()

            fd_plan = open(f"{abssubpath}/out.plan")
            fd_sas_plan = open(f"{abspath}/sas_plan", "w+")

            print("Processing plan file")
            for l in fd_plan:
                opl = l.split()
                op_schema_name = (opl[0])
                op_arguments = " ".join(opl[1:])
                all_op_line = f"{op_schema_name} {op_arguments}\n"
                fd_sas_plan.write(all_op_line)

            # print("Compressing the file")
            # with open(all_operators_file, 'rb') as input:
            #     with bz2.BZ2File(f"{all_operators_file}.bz2", 'wb', compresslevel=9) as output:
            #         copyfileobj(input, output)
    except FileNotFoundError:
        pass
        
copy(domain_file, cur_dir)

