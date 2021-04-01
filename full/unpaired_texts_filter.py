'''
A filter for unpaired bitexts:
    - identifying texts that have no corresponding translation and filter them out in order to allow text pairing for
      subsequent alignment
      This is done by comparing sets of file IDs in order to discard texts whose translation has not been downloaded
    - creating .txt report file to keep track of eliminated texts.
'''

import argparse
import os.path
import re

#  define cmd arguments
parser = argparse.ArgumentParser(description="A filter for unpaired bitexts:\n- identifying texts that have no "
                                             "corresponding translation and filter them out in order to allow text"
                                             " pairing for subsequent alignment\nThis is done by comparing sets of"
                                             " file IDs in order to discard texts whose translation has not been "
                                             "downloaded\n- creating .txt report file to keep track of"
                                             " eliminated texts.")
parser.add_argument("it_folder", help="the full location of the folder containing the Italian texts")
parser.add_argument("de_folder", help="the full location of the folder containing the German texts")
args = parser.parse_args()


#  processing arguments
IT_path = args.it_folder
DE_path = args.de_folder

#  regex pattern to extract IDs from filenames. Filenames are in the following form: "STPLC_IT_1234", "STPLC_DE_1234"
pattern = re.compile(r"STPLC_(it|de)_(\d{4})\.txt")

it_set = set()                                                  # building a set of IDs of Italian texts
for text in os.listdir(IT_path):
    try:
        it_set.add(pattern.search(text).group(2))               # getting text ID and adding to the IT set of IDs
    except:
        continue

de_set = set()                                                  # building a set of IDs of Italian texts
for text_ in os.listdir(DE_path):
    try:
        de_set.add(pattern.search(text_).group(2))              # getting text ID and adding to the DE set of IDs
    except:
        continue

differences = it_set.symmetric_difference(de_set)               # finding symmetric differences between sets of IDs
print("Identifying unpaired texts...")

it_eliminated_texts = ["Eliminated texts (IT):"]                # info for the report file
de_eliminated_texts = ["Eliminated texts (DE):"]

#  eliminating unpaired texts
for it_file in IT_texts:                                                # iterating over Italian texts
    if any(x in it_file for x in differences):                          # if the text ID is in the "differences" set
        it_eliminated_texts.append(os.path.join(IT_path, it_file))      # adding to list for the report file
        os.remove(os.path.join(IT_path, it_file))                       # removing text
print("\nItalian unpaired files eliminated.")

for de_file in DE_texts:                                                # iterating over German texts
    if any(x in de_file for x in differences):                          # if the text ID is in the "differences" set
        de_eliminated_texts.append(os.path.join(DE_path, de_file))      # adding to list for the report file
        os.remove(os.path.join(DE_path, de_file))                       # removing text
print("\nGerman unpaired files eliminated.")

#  building the .txt report file
text1 = "\n".join(it_eliminated_texts)
text2 = "\n".join(de_eliminated_texts)
text = text1 + "\n\n\n" + text2

with open("report_unpaired_filter.txt", "w") as file:
    file.write(text)

print("\nReport file created.")
print("\nDone!")


