'''
Inverting an alignment mapping file from target->source to source->target
'''
import re

input_file = r"C:\Users\anton\Documents\Documenti importanti\SSLMIT FORLI M.A. SPECIALIZED TRANSLATION 2019-2021\tesi\CORPUS\stplc_full\corpus\aligment files\lexb_aligned_de-it.txt"
output_file = r"C:\Users\anton\Documents\Documenti importanti\SSLMIT FORLI M.A. SPECIALIZED TRANSLATION 2019-2021\tesi\CORPUS\stplc_full\corpus\aligment files\lexb_aligned_it-de.txt"


with open(input_file, "r", encoding="utf-8") as inp:
    input_map = inp.read().splitlines()

out_list = []

for line in input_map:
    reg = re.search(r"(.+)\t(.+)", line)
    out_list.append("%s\t%s" % (reg.group(2), reg.group(1)))

with open(output_file, "w", encoding="utf-8") as out:
    out.write("\n".join(out_list))
