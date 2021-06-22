'''
Dividing dataset into training set and test set. Test set contains 2000 proper (starting with uppercase letter and
ending with period, colon or semicolon) sentences with 10-20 words length (extend to 24 words?).
Before selecting the test set, we carry out an advanced deduplication operation (Pinnis 2018), in order to avoid having
almost-duplicates in training set and test set, but still keeping that potentially useful almost-duplicates in the
training set and keeping them from being selected for test set.
'''
import random
import regex
import argparse


#  define cmd arguments
parser = argparse.ArgumentParser(description="Script for dataset splitting (training set and test set) with advanced"
                                             "deduplication process to avoid almost-duplicates in the test set.")
parser.add_argument("dataset", help="the whole dataset in tab-separated txt format")
args = parser.parse_args()

#  processing arguments
total_dataset = args.dataset


with open(total_dataset, "r", encoding="utf-8") as corp:
    corpus__ = corp.read().splitlines()

print("Segments of total dataset before deduplication: ", len(corpus__))

#  simple deduplication
corpus = set(corpus__)

print("Segments of total dataset after simple deduplication: ", len(corpus))

#  deduplicating (adapted from Pinnis 2018)
print("Advanced deduplication...")
tu_dict = {}        #tu_dict must be in the form of -> original string: normalized string
for line in corpus:
    modified = line.lower().replace(" ", "")  # lowercasing and removing simple whitespaces
    punctuation = regex.compile(r"[\\!\"#\$%&'’°\(\)\*\+,\-\./:;<=>\?@\[\]\^_`\{\|\}~„“”\s]")
    texts = (r"(legge provinciale|l\.p\.|L\.P\.|D\.P\.G\.P\.|L\.G\.|Landesgesetz|Landesgesetzes)")
    sections = (r"(articolo|titolo|comma|art\.|abstatz|titel)")
    dates = regex.compile(r"\d\d?[ \./](gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre|januar|februar|märz|april|mai|juni|juli|august|september|oktober|november|dezember|\d\d?)[ \.\/]\d{4}")
    #  series of numbers (ex. "1, 2, 3 e 4")
    numbers_and = regex.compile(r"(,? ?\d\d?\/?(bis|ter|quater|quinquies|sexies|septies|octies|novies|decies|undecies|duodecies)?){1,5}( (e|und) \d\d?\/?(bis|ter|quater|quinquies|sexies|septies|octies|novies|decies|undecies|duodecies)?)")
    numbers = regex.compile(r"\d+/?(bis|ter|quater|quinquies|sexies|septies|octies|novies|decies|undecies|duodecies)?")
    while regex.search(texts, modified):
        modified = regex.sub(texts, "T", modified)  # replacing text types with "T" placeholder
    while regex.search(sections, modified):
        modified = regex.sub(sections, "S", modified)   # replacing section types with "S" placeholder
    while regex.search(dates, modified):
        modified = regex.sub(dates, "Y", modified)    # replacing dates with "Y" placeholder
    while regex.search(numbers_and, modified):
        modified = regex.sub(numbers_and, "X", modified)  # replacing series of numbers with "X" placeholder
    while regex.search(numbers, modified):
        modified = regex.sub(numbers, "X", modified)  # replacing digits with "X" placeholder
    while regex.search(punctuation, modified):
        modified = regex.sub(punctuation, "", modified)  # removing punctuation
        tu_dict[line] = modified

new_dict = {}
blacklist = set()
for x, y in tu_dict.items():                    #deduplication
    if y not in new_dict.values():
        new_dict[x] = y
    else:
        # if it is an almost-duplicate, put its normalized version in a blacklist set
        # these almost-duplicates will be removed from the deduplicated dataset, in order for them not to be selected
        # for the test set
        blacklist.add(tu_dict[x])

print("Number of almost-duplicates: ", len(blacklist))

#print(len(new_dict))
delete = []                                         # creating a list of keys we want to delete
for x, y in new_dict.items():
    for dup in blacklist:
        if dup == y:
            delete.append(x)
            continue

#print(len(delete))

for i in delete:  # removing almost-duplicates from deduplicated dict (from which I will extract segments for test set)
    del new_dict[i]

#print(len(new_dict))            # length of deduplicated dataset without almost-dupes

#  extracting list of original source-target pairs
dedup_list = []
for x in new_dict.keys():
    dedup_list.append(x)

#  converting dataset to list of tuples (source, target)
dataset = list((source, target.strip()) for source, target in (line.split("\t") for line in dedup_list))

#  temporarily putting all segments of length 10-20 words starting with uppercase letter in a separate list
segments10_20 = []
sentence_ending_punct = (".", ";", ":")
for tu in dataset:
    (source, target) = tu
    if 10 <= len(source.split()) <= 20\
            and 10 <= len(target.split()) <= 20\
            and source[0].isupper()\
            and target[0].isupper()\
            and source.endswith(sentence_ending_punct)\
            and target.endswith(sentence_ending_punct):              # subsampling only 10-24-word segments starting with uppercase letter and ending with either  . ; :
        dataset.remove(tu)              # removing temporarily from dataset
        segments10_20.append(tu)        # putting to a separate list for subsampling
        print(source)
        print(target)
        print()

print("Total segments between 10 and 20 tokens, starting with uppercase letter and ending with punctuation (.;:): ",
      len(segments10_20))


random.shuffle(segments10_20)              # shuffling temporary 10-20 segment list
test_set_ = list(segments10_20[:2040])     # generating test_set by taking first 2000 random segments from shuffled list

print("Test set has %i segments." % len(test_set_))

#  converting test_set_ to list of strings (not list of tuples)
test_set = []
for tu in test_set_:
    test_set.append("\t".join(tu))

# removing test set from whole dataset
for TU in test_set:
    if TU in corpus:
        corpus.remove(TU)
    else:
        print("Error: test set segment not found in the original dataset. Couldn't remove it from the training set.")

#  dividing into test set (only Italian sentences) and reference (corresponding German translations)
test_set_it = []
reference = []
for source, target in (line.split("\t") for line in test_set):
    test_set_it.append(source)
    reference.append(target)

#  exporting training set, test set and reference separately to tab-separated txt files
corpus = ["it\tde"] + list(corpus)    # necessary?
training_set = "\n".join(corpus)
with open("training-set__3.txt", "w", encoding="utf-8") as training:
    training.write(training_set)
print("Training set size (TUs): ", len(corpus))

test_set_it = "\n".join(test_set_it)
with open("test-set__3.txt", "w", encoding="utf-8") as test:
    test.write(test_set_it)
print("Test set size (chars): ", len(test_set_it))

reference = "\n".join(reference)
with open("reference__3.txt", "w", encoding="utf-8") as ref:
    ref.write(reference)

print("Done.")


