'''
Creating alignment mapping file for Manatee/NoSketchEngine

Adapted from calign.py, fixgaps.py and compressrng.py by Milos Jakubicek 2012
'''
import re

alignment_file = r"C:\Users\anton\Desktop\prove_download_scraper\stplc_full_25.02\prova11.it.de.xml"
output_mapping_file = r"C:\Users\anton\Desktop\prove_download_scraper\stplc_full_25.02\mapping_final.txt"

with open(alignment_file, "r", encoding="utf-8") as map:
    map_file = map.read().splitlines()


def tr_line (aligned, line_nr):
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

#generating alignment mapping file
alignment_list = []
for line_nr, line in enumerate(map_file):
    line_m = re.match(r".*xtargets=(\"|')([^\1]+?)\1.*", line)
    if not line_m:
        continue
    aligned = line_m.group(2).split(";")
    if len(aligned) > 2:
        print("Skipping invalid mapping on line %d\n" % line_nr + 1)
        continue
    l1 = tr_line(aligned[0], line_nr)
    l2 = tr_line(aligned[1], line_nr)
    if l1 != None and l2 != None:
        alignment_list.append("%s\t%s\n" % (l1, l2))
        print("%s\t%s\n" % (l1, l2))

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
        print_range (beg_l1, end_l1, True, final)
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

with open(output_mapping_file, "w", encoding="utf-8") as finalmap:
    finalmap.write("\n".join(final))

print("Done")