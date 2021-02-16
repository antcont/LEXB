'''
Dividing dataset into training set and test set. Test set contains 4000? proper (starting with uppercase letter) sentences with 10-20 words length.
Before selecting the test set, we carry out an advanced deduplication operation (Pinnis 2018), in order to avoid having almost-duplicates
in training set and test set, but still keeping that potentially useful almost-duplicates in the training set.
'''
import random

corpus_txt = r"C:\Users\anton\Dropbox\Eurac_tesi\custom_MT\corpus\stplc_08022021_cleaned.txt"

with open(corpus_txt, "r", encoding="utf-8") as corp:
    corpus = corp.readlines()

dataset = list((source, target.strip()) for source, target in (line.split("\t") for line in corpus))    #converting dataset to list of tuples (source, target)
print("Segments of total dataset: ", len(dataset))

#temporarily putting all segments of length 10-20 words starting with uppercase letter in a separate list
segments10_20 = list()
for tu in dataset:
    (source, target) = tu
    if 10 <= len(source.split()) <= 20 and 10 <= len(target.split()) < 20 and source[0].isupper() and target[0].isupper(): # subsampling only 10-20-word segments starting with uppercase letter
        dataset.remove(tu)              # removing temporarily from dataset
        segments10_20.append(tu)        # putting to a separate list for subsampling

print("Total segments between 10 and 20 tokens: ", len(segments10_20))

random.shuffle(segments10_20)               # shuffling temporary 10-20 segment list
test_set_ = list(segments10_20[:2000])      # generating test_set by taking first 2000 random segments from shuffled list
del segments10_20[:2000]                    # removing test segments from temporary 10-20 segment list
for tu in segments10_20:
    dataset.append(tu)                      # re-appending remaining 10-20 segments to training set (our initial "dataset" variable)

print("Training set has %i segments." % len(dataset))
print("Test set has %i segments." % len(test_set_))


# exporting training set and test set separately to tab-separated txt files
training_set = []
for tu in dataset:
    training_set.append("\t".join(tu))
training_set = "\n".join(training_set)
with open("training-set.txt", "w", encoding="utf-8") as training:
    training.write(training_set)

test_set = []
for tu in test_set_:
    test_set.append("\t".join(tu))
test_set = "\n".join(test_set)
with open("test-set_2000.txt", "w", encoding="utf-8") as test:
    test.write(test_set)

print("Done.")



