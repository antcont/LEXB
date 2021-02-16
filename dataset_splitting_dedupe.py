'''
Dividing dataset into training set and test set. Test set contains 4000? proper (starting with uppercase letter) sentences with 10-20 words length.
Before selecting the test set, we carry out an advanced deduplication operation (Pinnis 2018), in order to avoid having almost-duplicates
in training set and test set, but still keeping that potentially useful almost-duplicates in the training set.

working partially: it creates the test set in the right way, BUT i did not still succeed in removing test-set segments from dataset to obtain training set
problem?: Total segments between 10 and 20 tokens:  6119
'''
import random
import regex

corpus_txt = r"C:\Users\anton\Documents\Documenti importanti\SSLMIT FORLI M.A. SPECIALIZED TRANSLATION 2019-2021\tesi\corpus\stplc_08022021_cleaned.txt"

with open(corpus_txt, "r", encoding="utf-8") as corp:
    corpus = corp.read().splitlines()

print("Segments of total dataset: ", len(corpus))


# deduplicating (Pinnis 2018)
print("Deduplicating TUs...")
tu_dict = {}        #tu_dict must be in the form of -> original string: normalized string
for line in corpus:
    modified = line.lower().replace(" ", "")  # lowercasing and removing simple whitespaces
    punctuation = regex.compile(r"[\\!\"#\$%&'\(\)\*\+,\-\./:;<=>\?@\[\]\^_`\{\|\}~„“”\s]")
    numbers = regex.compile(r"\d+")
    while regex.search(punctuation, modified):
        modified = regex.sub(punctuation, "", modified)  # removing punctuation
    while regex.search(numbers, modified):
        modified = regex.sub(numbers, "X", modified)  # substituting digits with "X" placeholder
        tu_dict[line] = modified

new_dict = {}
blacklist = set()
for x, y in tu_dict.items():                    #deduplication
    if y not in new_dict.values():
        new_dict[x] = y
    else:
        # if it is an almost-duplicate, put its normalized version in a blacklist set
        # these almost-duplicates will be removed from the deduplicated dataset, in order for them not to be selected for the test set
        blacklist.add(tu_dict[x])

print(type(blacklist))
print(len(blacklist))

print(len(new_dict))
delete = []                                         # creating a list of keys we want to delete
for x, y in new_dict.items():
    for dup in blacklist:
        if dup == y:
            delete.append(x)

print(len(delete))

for i in delete:                                    # removing almost-duplicates from deduplicated dict
    del new_dict[i]

print(len(new_dict))            # length of deduplicated dataset event without almost-dupes


#extracting list of original source-target pairs
dedup_list = []
for x in new_dict.keys():
    dedup_list.append(x)

dataset = list((source, target.strip()) for source, target in (line.split("\t") for line in dedup_list))    #converting dataset to list of tuples (source, target)

#temporarily putting all segments of length 10-20 words starting with uppercase letter in a separate list
segments10_20 = list()
for tu in dataset:
    (source, target) = tu
    if 10 <= len(source.split()) <= 20 and 10 <= len(target.split()) < 20 and source[0].isupper() and target[0].isupper(): # subsampling only 10-20-word segments starting with uppercase letter
        dataset.remove(tu)              # removing temporarily from dataset
        segments10_20.append(tu)        # putting to a separate list for subsampling

print("Total segments between 10 and 20 tokens: ", len(segments10_20))

random.shuffle(segments10_20)               # shuffling temporary 10-20 segment list
test_set_ = list(segments10_20[:4000])      # generating test_set by taking first 2000 random segments from shuffled list

print("Test set has %i segments." % len(test_set_))

#converting test_set_ to list of strings (not list of tuples)
test_set = []
for tu in test_set_:
    test_set.append("\t".join(tu))

print(test_set)
print(corpus)
# removing test set from whole dataset (doesn't work at the moment)
for TU in test_set:
    if TU in corpus:
        corpus.remove(TU)
    else:
        print("Error: test set segment not found in whole dataset")

# exporting training set and test set separately to tab-separated txt files
corpus = ["it\tde"] + corpus    # necessary?
training_set = "\n".join(corpus)
with open("training-set.txt", "w", encoding="utf-8") as training:
    training.write(training_set)
print("Training set size (TUs): ", len(corpus))

test_set = ["it\tde"] + test_set    #is this necessary?
test_set = "\n".join(test_set)
with open("test-set_4000.txt", "w", encoding="utf-8") as test:
    test.write(test_set)
print("Test set size (chars): ", len(test_set))

print("Done.")


