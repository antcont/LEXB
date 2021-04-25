"""
A counter for sentence pairs and tokens in a parallel corpus.
It also calculates the TTR (Type-Token Ratio)
"""

import argparse
from nltk import word_tokenize
from lxml import etree


def segment_counter(path, min, max):
    '''
    A simple sentence pair counter according to a given length (tokens).
    '''
    print("Counting segments...\n")
    nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}
    tree = etree.parse(path)
    root = tree.getroot()
    counter_total = 0
    counter_right_length = 0
    for tu in root.iter("tu"):
        counter_total += 1
        source_segment = tu.find("./tuv[@xml:lang='it']/seg", namespaces=nsmap).text
        target_segment = tu.find("./tuv[@xml:lang='de']/seg", namespaces=nsmap).text
        source_tokens = source_segment.split()
        target_tokens = target_segment.split()
        if min <= len(source_tokens) <= max and min <= len(target_tokens) <= max:
            counter_right_length += 1
            """print(source_segment)
            print(target_segment)
            print()"""
    print("Total sentence pair count: ", counter_total)
    #print("Sentence pairs with length between %i and %i tokens: %s" % (min, max, counter_right_length))


def token_counter(path):
    print("Counting tokens...\n")
    nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}
    tree = etree.parse(path)
    root = tree.getroot()

    corpus_it = []
    corpus_de = []

    for tu in root.iter("tu"):
        source_segment = tu.find("./tuv[@xml:lang='it']/seg", namespaces=nsmap).text
        target_segment = tu.find("./tuv[@xml:lang='de']/seg", namespaces=nsmap).text
        corpus_it.append(source_segment)
        corpus_de.append(target_segment)

    #  tokenizing
    it_tokens = word_tokenize("\n".join(corpus_it))
    de_tokens = word_tokenize("\n".join(corpus_de))

    print("Italian corpus token count: ", len(it_tokens))
    print("German corpus token count: ", len(de_tokens))
    print("Total token count: ", len(it_tokens)+len(de_tokens), "\n")
    print("Italian corpus type count: ", len(set(it_tokens)))
    print("German corpus type count: ", len(set(de_tokens)))
    print("Total type count: ", len(set(it_tokens+de_tokens)), "\n")
    print("TTR Italian corpus: ", len(set(it_tokens))/len(it_tokens))
    print("TTR German corpus: ", len(set(de_tokens))/len(de_tokens))
    print("TTR total corpus: ", (len(set(it_tokens))+len(set(de_tokens)))/(len(it_tokens)+len(de_tokens)))




if __name__ == '__main__':
    #  defining and processing cmd arguments
    parser = argparse.ArgumentParser(description="A counter for sentence-pairs and total tokens")
    parser.add_argument("parallelCorpus", help="the parallel corpus in TMX format")
    args = parser.parse_args()
    parallelCorpus = args.parallelCorpus

    segment_counter(parallelCorpus, 0, 1000)
    token_counter(parallelCorpus)



