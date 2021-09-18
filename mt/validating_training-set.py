'''
Removing test set sentences from training data, if there.
Use it when a new test set is used (or when new data is added to training set) and an up-to-date, deduplicated
training set is needed

Input and output are txt newline-separated lines of tab-separated sentences

NB: simple deduplication only!
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


#  creating new training set, with segments that are not contained in test-set
training_set = []
for TU in dataset:
    if TU not in bi_test_set:
        training_set.append(TU)


#  export new training set
filename_old = Path(trainingSet).stem
filename_new = filename_old + "_validated.txt"
with open(filename_new, "w", encoding="utf-8") as tr:
    tr.write("\n".join(training_set))

print("Done.")