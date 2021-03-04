import sys
fd = open(sys.argv[1], "r")

hintcount = 0
for line in fd:
    if "hint-" in line:
        hintcount += 1

fd.close()
hint_skip = int(hintcount * float(sys.argv[2])/100)


fd = open(sys.argv[1], "r")
new_file_lines = []
for l in fd:
    if "hint-" in l:
        if hint_skip:
            hint_skip -= 1
        else:
            continue
    new_file_lines.append(l)

open(sys.argv[3], "w+").write("\n".join(new_file_lines))

