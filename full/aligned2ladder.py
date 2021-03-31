'''
aligned2ladder.py
adapted by antcont

Based on calign.py, fixgaps.py and compressrng.py by Milos Jakubicek 2012
(https://www.sketchengine.eu/documentation/mn-mapping-helper-scripts/)

Generating an alignment definition file from parallel corpora (both with numeric and string structure attribute values)
(using the Intertext XML alignment file) for SkE/NoSkE (ladder format)

For the "raw" alignment file (no compressing, no fixing gaps), when writing the output file join "alignment_list"
For alignment definition file with gap fixing, join "alignment_list_fixedgaps"
For compressed and gap-fixed alignment definition file, join "final".
'''

import re


alignment_file = r"C:\Users\anton\Documents\Documenti importanti\SSLMIT FORLI M.A. SPECIALIZED TRANSLATION 2019-2021\tesi\CORPUS\stplc_full\corpus\corpus XML\LexB.it.de.xml"
output_mapping_file_st = r"C:\Users\anton\Documents\Documenti importanti\SSLMIT FORLI M.A. SPECIALIZED TRANSLATION 2019-2021\tesi\CORPUS\stplc_full\corpus\corpus XML\LexB_ladder_de-it.txt"    # target to source (e.g. if alignment_file is it-de, this will be de-it)
output_mapping_file_ts = r"C:\Users\anton\Documents\Documenti importanti\SSLMIT FORLI M.A. SPECIALIZED TRANSLATION 2019-2021\tesi\CORPUS\stplc_full\corpus\corpus XML\LexB_ladder_it-de.txt"    # source to target (e.g. if alignment_file is it-de, this will be it-de)


with open(alignment_file, "r", encoding="utf-8") as map:
    map_file = map.read().splitlines()


def tr_line(aligned, line_nr):
    if not aligned:
        return -1
    aligned = aligned.split()
    beg, end = aligned[0], aligned[-1]
    if beg == end:
        b = beg
        if b == -1:
            print("Skipping invalid beg/end ('%s') on line %d\n"\
                             % (beg, line_nr + 1))
            return None
        return b
    else:
        b = beg
        e = end
        if b == -1 or e == -1:
            if b == -1 and e == -1:
                print("Skipping invalid beg, end ('%s','%s') on "\
                                 "line %d\n" % (beg, end, line_nr + 1))
                return None
            elif b == -1:
                print("Invalid beg ('%s') on line %d, using end\n"\
                                 % (beg, line_nr + 1))
                return e
            else: # e == -1
                print("Invalid end ('%s') on line %d, using beg\n"\
                                 % (end, line_nr + 1))
                return b
        return "%d,%d" % (int(b), int(e))

# NB: here and below I'm calling source the attribute values appearing BEFORE the semicolon,
# even if it is actually not the source in the Intertext mapping file
list_source = []
list_target = []

for line_nr, line in enumerate(map_file):
    line_m = re.match(r".*xtargets=(\"|')([^\1]+?)\1.*", line)
    if not line_m:
        continue
    aligned = line_m.group(2).split(";")
    if len(aligned) > 2:
        print("Skipping invalid mapping on line %d\n" % line_nr + 1)
        continue
    if not aligned[0]:
        pass
    elif " " not in aligned[0] and aligned[0] != None:   # if only 1 source segment
        list_source.append(aligned[0])
    else: # if more than one source segment
        for seg in aligned[0].split():
            if seg != None and aligned[0] not in list_source:
                list_source.append(seg)
    if not aligned[1]:
        pass
    elif " " not in aligned[1] and aligned[1] != None:  # if only 1 target segment
        list_target.append(aligned[1])
    else:   # if more than one target segment
        for seg in aligned[1].split():
            if seg != None and aligned[1] not in list_target:
                list_target.append(seg)

# converting (string)id lists to dictionaries by assigning to each an index with enumerate()
dict_source = {}
dict_target = {}

for id_int, id_s in enumerate(list_source):
    dict_source[id_s] = str(id_int)
for id_int, id_s in enumerate(list_target):
    dict_target[id_s] = str(id_int)

print(len(dict_source))
print(len(dict_target))

# substituting string values with ids (from dictionary) and creating final alignment definition file in ladder format
alignment_list = []
for line_nr, line in enumerate(map_file):
    line_m = re.match(r".*xtargets=(\"|')([^\1]+?)\1.*", line)
    if not line_m:
        continue
    aligned = line_m.group(2).split(";")
    if not aligned[0]:            # taking care of 0:n and n:0 alignments
        l1 = tr_line(aligned[0], line_nr)
    elif " " not in aligned[0] and aligned[0] != None:
        l1 = tr_line(dict_source[aligned[0]], line_nr)  # changing id from string to integer and processing with tr_line
    else:
        l1 = tr_line(" ".join([str(dict_source[seg_id]) for seg_id in aligned[0].split()]), line_nr)
    if not aligned[1]:
        l2 = tr_line(aligned[1], line_nr)
    elif " " not in aligned[1] and aligned[1] != None:
        l2 = tr_line(dict_target[aligned[1]], line_nr)          # changing id from string to integer
    else:
        l2 = tr_line(" ".join([str(dict_target[seg_id]) for seg_id in aligned[1].split()]), line_nr)
    if l1 != None and l2 != None:
        alignment_list.append("%s\t%s\n" % (l1, l2))


# fixing gaps
alignment_list_fixedgaps = []
last_l1 = last_l2 = -1
for line in alignment_list:
    l1, l2 = line[:-1].split("\t")
    l1 = l1.split(",")
    l2 = l2.split(",")
    l1[0] = int(l1[0])
    l2[0] = int(l2[0])
    l1[-1] = int(l1[-1])
    l2[-1] = int(l2[-1])
    while l1[0] > last_l1 + 1:
        last_l1 += 1
        alignment_list_fixedgaps.append("%d\t-1\n" % last_l1)
    while l2[0] > last_l2 + 1:
        last_l2 += 1
        alignment_list_fixedgaps.append("-1\t%d\n" % last_l2)
    if l1[-1] != -1:
        last_l1 = l1[-1]
    if l2[-1] != -1:
        last_l2 = l2[-1]
    alignment_list_fixedgaps.append(line)


final = []
# compressing
def print_range(beg, end, rightEmpty, final):
    if beg == end:
        if rightEmpty:
            final.append("%d\t-1\n" % beg)
        else:
            final.append("-1\t%d\n" % beg)
    else:
        if rightEmpty:
            final.append("%d,%d\t-1\n" % (beg, end))
        else:
            final.append("-1\t%d,%d\n" % (beg, end))

beg_l1 = beg_l2 = end_l1 = end_l2 = None

#for line in alignment_list:
for line in alignment_list_fixedgaps:
    l1, l2 = line[:-1].split("\t")
    l1 = l1.split(",")
    l2 = l2.split(",")
    l1[0] = int(l1[0])
    l2[0] = int(l2[0])
    l1[-1] = int(l1[-1])
    l2[-1] = int(l2[-1])
    if l2[0] == -1:
        if beg_l1 == None:
            beg_l1 = l1[0]
            end_l1 = l1[-1]
        else:
            end_l1 = l1[-1]
        continue
    elif beg_l1 != None:
        print_range(beg_l1, end_l1, True, final)
        beg_l1 = None
    if l1[0] == -1:
        if beg_l2 == None:
            beg_l2 = l2[0]
            end_l2 = l2[-1]
        else:
            end_l2 = l2[-1]
        continue
    elif beg_l2 != None:
        print_range(beg_l2, end_l2, False, final)
        beg_l2 = None
    final.append(line)
if beg_l1:
    print_range(beg_l1, end_l1, True, final)
elif beg_l2:
    print_range(beg_l2, end_l2, False, final)


print(len(alignment_list))
print(len(alignment_list_fixedgaps))
print(len(final))


# writing source-target mapping file
with open(output_mapping_file_st, "w", encoding="utf-8") as finalmap:
    finalmap.write("".join(alignment_list))   # by joining alignment_list I am skipping both compressing and fixing gaps

# inverting and writing target-source mapping file
target2source = []
for line in alignment_list:     # same as above (change to "alignment_list_fixedgaps" or "final" if needed)
    reg = re.search(r"(.+)\t(.+)", line)
    target2source.append("%s\t%s" % (reg.group(2), reg.group(1)))

with open(output_mapping_file_ts, "w", encoding="utf-8") as out:
    out.write("\n".join(target2source))


print("Done")