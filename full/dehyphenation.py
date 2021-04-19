'''
Dehyphenation
'''
import argparse
from lxml import etree
from nltk import word_tokenize
from collections import Counter
import regex
from pathlib import Path

#  define cmd arguments
parser = argparse.ArgumentParser(description="Script for dehyphenation.")
parser.add_argument("corpus", help="the corpus in .xml format to be dehyphenated")
parser.add_argument("-o", "--overwrite", help="(optional) overwriting the old corpus; by default, a new file is created",
                    action="store_true")
args = parser.parse_args()

#  processing arguments
input_corpus = args.corpus
overwrite = args.overwrite


def dehyphenation(path_in):
    '''
    It generates vocabularies for each corpus (it and de) and validates whether a hyphenated word is more frequent as
    1) hyphenated or 2) merged. If 2, it converts the word from hyphenated to merged.
    It has to be re-run because it considers only the first instance of hyphenated word in the sentence.
    '''
    #Generating vocabularies
    print("Generating vocabularies...")
    corpus_ = []
    tree = etree.parse(path_in)  # parsing the corpus
    root = tree.getroot()
    segments = root.findall("text/s")
    for segment in segments:
        corpus_.append(segment.text.lower())
    vocab = Counter(word_tokenize("\n".join(corpus_)))   # tokenizing and counting frequencies
    counter_dehyph = 0
    print("Dehyphenating...")
    reg = regex.compile(r"(([A-Za-zöäüÖÄÜ]+)\-([A-Za-zöäüÖÄÜ]+))")

    for segment in segments:
        found_it = regex.search(reg, segment.text)

        if found_it:
            frequency_hyph = vocab[found_it.group(1)]
            merged_token = found_it.group(2) + found_it.group(3)
            try:
                frequency_merged = vocab[merged_token]
            except:
                continue
            if frequency_hyph >= frequency_merged:
                continue
            if frequency_hyph == 0:  # to avoid unexplainable ZeroDivisionError in the following elif
                continue

            elif (frequency_merged/frequency_hyph) > 10 and (frequency_hyph+frequency_merged) > 40:
                # if hyphenated form occurs more than once, we modify it only if the merged form
                # occurs more than 10x more than the hyphenated and their global frequency is > 40
                print(found_it.group(1))
                print(frequency_hyph, "vs.", frequency_merged, "\t", float(frequency_merged/frequency_hyph),
                      "x,\t tot", frequency_merged+frequency_hyph)
                print(segment.text)
                new_segment = regex.sub(reg, merged_token, segment.text, 1)
                segment.text = new_segment
                print(new_segment)
                print()
                counter_dehyph += 1

    #  writing dehyphenated corpus
    if overwrite:
        tree.write(input_corpus, encoding="UTF-8")

    else:  # if overwrite == False (by default)
        filename_old = Path(input_corpus).stem
        filename_new = filename_old + "_dehyph.xml"
        tree.write(filename_new, encoding="UTF-8")

    print("Dehyphenated: ", counter_dehyph)


dehyphenation(input_corpus)

print("Done.")