'''
Removing test set sentences from training data, if there.
Use it when a new test set is used (or when new data is added to training set) and an up-to-date, deduplicated
training set is needed

Input and output are txt newline-separated lines of tab-separated sentences

NB: simple+advanced deduplication (removing duplicates and near-duplicates)
NB2: near-duplicates are removed from the test set! If you want to keep near-duplicates in the training data only,
     consider dataset re-splitting with /dataset_deduplication_splitting.py
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
def normalise(line):
    modified = line.lower().replace(" ", "")  # lowercasing and removing simple whitespaces
    punctuation = regex.compile(r"[\\!\"#\$%&'’°\(\)\*\+,\-\./:;<=>\?@\[\]\^_`\{\|\}~„“”\s]")
    texts = regex.compile(
        r"(decretodelpresidentedellarepubblica|dekretedespräsidentenderrepublik|decretodelpresidentedellaprovincia|decretodelpresidentedellagiuntaprovinciale|leggeregionale|leggeprovinciale|legge|l\.p\.|d\.p\.Gg\.p\.|l\.g\.|landesgesetz(es)?|regionalgesetz(es)?|d\.p\.p\.|d\.lh\.|dekret(e?s)?deslandeshauptmanns|deliberazioneprovinciale|deliberazionedellagiuntaprovinciale|beschluss(es)?|dekret(es)?|decreto|delibera)")
    sections = regex.compile(r"(articolo|titolo|comma|art\.|artikel|absatz|titel)")
    dates = regex.compile(
        r"(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre|januar|jänner|februar|märz|april|mai|juni|juli|august|september|oktober|november|dezember)")
    #  series of numbers (ex. "1, 2, 3 e 4")
    numbers_and = regex.compile(
        r"(,?\d\d?\/?(bis|ter|quater|quinquies|sexies|septies|octies|novies|decies|undecies|duodecies)?){1,5}( (e|und) \d\d?\/?(bis|ter|quater|quinquies|sexies|septies|octies|novies|decies|undecies|duodecies)?)")
    numbers = regex.compile(
        r"\d+[/\-]?(bis|ter|quater|quinquies|sexies|septies|octies|novies|decies|undecies|duodecies)?")
    while regex.search(texts, modified):
        modified = regex.sub(texts, "T", modified)  # replacing text types with "T" placeholder
    while regex.search(sections, modified):
        modified = regex.sub(sections, "S", modified)  # replacing section types with "S" placeholder
    while regex.search(dates, modified):
        modified = regex.sub(dates, "Y", modified)  # replacing dates with "Y" placeholder
    while regex.search(numbers_and, modified):
        modified = regex.sub(numbers_and, "X", modified)  # replacing series of numbers with "X" placeholder
    while regex.search(numbers, modified):
        modified = regex.sub(numbers, "X", modified)  # replacing digits with "X" placeholder
    while regex.search(punctuation, modified):
        modified = regex.sub(punctuation, "", modified)  # removing punctuation

    return line, normalised


#  normalizing the test set
tu_dict_test = {}        #tu_dict must be in the form of -> original string: normalized string
for line in bi_test_set:
    line, normalised = normalise(line)
    tu_dict_test[normalised] = line

blacklist = set()   # blacklist of normalised string representation to be removed from training set

#  normalizing the training set
tu_dict_training = {}        #tu_dict must be in the form of -> original string: normalized string
for line in training_set:
    line, normalised = normalise(line)
    if normalised not in tu_dict_test.keys():       #  near-duplicates are excluded from the training set
        tu_dict_training[normalised] = line


#  extracting list of original source-target pairs
training_deduped = []
for x in tu_dict_training.values():
    training_deduped.append(x)

#  export new training set
filename_old = Path(trainingSet).stem
filename_new = filename_old + "_validated_deduplicated.txt"
with open(filename_new, "w", encoding="utf-8") as tr:
    tr.write("\n".join(training_deduped))

print("Done.")