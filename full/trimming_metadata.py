'''
Script for trimming metadata using regular expressions.
'''

input_corpus = r"C:\Users\anton\Documents\Documenti importanti\SSLMIT FORLI M.A. SPECIALIZED TRANSLATION 2019-2021\tesi\CORPUS\stplc_full\corpus\vert files\lexb_de.vert"
output_corpus = r"C:\Users\anton\Documents\Documenti importanti\SSLMIT FORLI M.A. SPECIALIZED TRANSLATION 2019-2021\tesi\CORPUS\stplc_full\corpus\vert files\lexb_de_trimmed.vert"

with open(input_corpus, "r+", encoding="utf-8") as input_corp:
    corp = input_corp.read().splitlines()

# escaping the corpus (only lines containing text, not tags obs) to make it parsable
replace = [
    (' " ', '" '),
    ('=" ', '="')
]

trimmed_corp = []
for line in corp:
    if line.startswith('<text'):
        for (find, sub) in replace:
            line = line.replace(find, sub)
        trimmed_corp.append(line)
    else:
        trimmed_corp.append(line)

with open(output_corpus, "w+", encoding="utf-8") as corp_out:
    corp_out.write("\n".join(trimmed_corp))

print("Done")