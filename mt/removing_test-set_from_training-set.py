'''
Getting (new) training set by subtracting (old) test set to (new) total dataset.
A simple and advanced deduplication operations are again carried out on the dataset(s).
Input and output are txt newline-separated lines of tab-separated sentences

Use it when test set has been modified/corrected and we need an up-to-date training test,
and when new data is added to training set.
'''
import argparse
from pathlib import Path
import regex

#  define cmd arguments
parser = argparse.ArgumentParser(description="Script to validate non-overlapping between training set and test set.")
parser.add_argument("trainingSet", help="training set in txt format")
parser.add_argument("testSet", help="test set in txt format")
parser.add_argument("reference", help="reference in txt format")
args = parser.parse_args()

#  processing arguments
trainingSet = args.trainingSet
testSet = args.testSet
reference = args.reference


#  reading the files' lines
with open(trainingSet, "r", encoding="utf-8") as data:
    dataset = data.read().splitlines()

with open(testSet, "r", encoding="utf-8") as test:
    test_set = test.read().splitlines()

with open(reference, "r", encoding="utf-8") as ref:
    reference = ref.read().splitlines()


#  checking test and ref have same length
if len(test_set) != len(reference):
    print("Error: test and reference have different lengths.")
    exit()


bi_test_set = []
#  create bilingual test_set lines with tab-separated sentence pairs
for i in range(len(test_set)):
    bi_test_set.append(test_set[i] + "\t" + reference[i])


#  creating new training set
training_set = []
for TU in dataset:
    if TU not in bi_test_set:
        training_set.append(TU)
    #else:
        #print("Error: test set segment not found in the original dataset. Couldn't remove it from the training set.")


#  simple deduplication of sentence pairs in the training set
training_set = list(dict.fromkeys(training_set))


print(len(dataset))
print(len(bi_test_set))
print(len(training_set))



print("Advanced deduplication...")
#  normalizing the test set
tu_dict_test = {}        #tu_dict must be in the form of -> original string: normalized string
for line in bi_test_set:
    modified = line.lower().replace(" ", "")  # lowercasing and removing simple whitespaces
    punctuation = regex.compile(r"[\\!\"#\$%&'\(\)\*\+,\-\./:;<=>\?@\[\]\^_`\{\|\}~„“”\s]")
    dates = regex.compile(r"\d\d?[gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre|Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember]\d{4}")
    numbers = regex.compile(r"\d+")
    while regex.search(punctuation, modified):
        modified = regex.sub(punctuation, "", modified)  # removing punctuation
    while regex.search(dates, modified):
        modified = regex.sub(dates, "Y", modified) #replacing dates with "Y" placeholder
    while regex.search(numbers, modified):
        modified = regex.sub(numbers, "X", modified)  # replacing digits with "X" placeholder
        tu_dict_test[line] = modified

#  normalizing the training set
tu_dict_training = {}        #tu_dict must be in the form of -> original string: normalized string
for line in training_set:
    modified = line.lower().replace(" ", "")  # lowercasing and removing simple whitespaces
    punctuation = regex.compile(r"[\\!\"#\$%&'’°\(\)\*\+,\-\./:;<=>\?@\[\]\^_`\{\|\}~„“”\s]")
    dates = regex.compile(r"(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre|Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)")
    numbers = regex.compile(r"\d+")
    while regex.search(punctuation, modified):
        modified = regex.sub(punctuation, "", modified)  # removing punctuation
    while regex.search(dates, modified):
        modified = regex.sub(dates, "Y", modified) #replacing dates with "Y" placeholder
    while regex.search(numbers, modified):
        modified = regex.sub(numbers, "X", modified)  # replacing digits with "X" placeholder
        tu_dict_training[line] = modified

#  using the normalized test set as blacklist for deduplication
blacklist = set()
for x, y in tu_dict_training.items():
    if y in tu_dict_test.values():
        blacklist.add(tu_dict_training[x])

delete = []                                         # creating a list of keys we want to delete
for x, y in tu_dict_training.items():
    if y in blacklist:
        delete.append(x)

#print(len(delete))

for i in delete:  # removing almost-duplicates from deduplicated dict (from which I will extract segments for test set)
    del tu_dict_training[i]

#  extracting list of original source-target pairs
training_deduped = []
for x in tu_dict_training.keys():
    training_deduped.append(x)

#  export new training set
filename_old = Path(trainingSet).stem
filename_new = filename_old + "_validated_deduplicated.txt"
with open(filename_new, "w", encoding="utf-8") as tr:
    tr.write("\n".join(training_deduped))

print("Done.")