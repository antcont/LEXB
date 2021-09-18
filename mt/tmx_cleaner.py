
import argparse
import langid
import regex
import string
from Levenshtein import distance
from collections import Counter
from lxml import etree
from nltk import word_tokenize
from pathlib import Path


class ParallelCorpus:

    def __init__(self, parallelCorpus: str):
        self.parallelCorpus = parallelCorpus
        self.tree = etree.parse(parallelCorpus)

    def remove_untranslated(self):
        '''
        Removing TUs with identical or almost identical source and target.
        Almost identical source-target: sentence pairs with a Levenshtein edit distance < 2.0
        or an edit distance ratio < 0.1 (Lu et al. 2018)
        '''
        counter_untr = 0
        counter_similar = 0
        nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}
        tree = self.tree
        root = tree.getroot()
        body = root.find("body")
        print("Removing untranslated TUs and TUs with highly similar source-target...")
        for tu in root.iter("tu"):
            source_segment = tu.find("./tuv[@xml:lang='it']/seg", namespaces=nsmap).text
            target_segment = tu.find("./tuv[@xml:lang='de']/seg", namespaces=nsmap).text
            if source_segment == target_segment:
                try:
                    body.remove(tu)
                    counter_untr += 1
                except:
                    #print("An error occurred. TU was not removed: %s \t %s" % (source_segment, target_segment))
                    pass
            edit_distance = distance(source_segment, target_segment)
            avglen = (len(source_segment) + len(target_segment)) / 2
            edit_distance_ratio = edit_distance / avglen
            if edit_distance < 2 or edit_distance_ratio < 0.1:              # parameters by Lu et al. 2018
            #if SequenceMatcher(None, source_segment, target_segment).ratio() > 0.8:
                #print(edit_distance, edit_distance_ratio, "\n", source_segment, "\n", target_segment, "\n")
                try:
                    body.remove(tu)
                    counter_similar += 1
                except:
                    #print("An error occurred. TU was not removed: %s \t %s" % (source_segment, target_segment))
                    pass
        print("%i untranslated TUs removed." % counter_untr)
        print("%i TUs with highly similar source-target removed." % counter_similar)
        print()

    def remove_useless(self):
        '''
        Removing sentence pairs where at least one segment is only "Art. 1". "(1)", "1." "1bis."
        '''
        tree = self.tree
        counter_art_rem = 0
        regex_rem = regex.compile(r"^(Art\. \d{1,3}|\(\d{1,3}\)|\d{1,3}(bis|ter|quater|quinquies|sexies|septies|octies|novies|decies|undecies|duodecies)?\.)$")        # TUs where at least one segment is only "Art. 1". "(1)", "1." "1bis."
        root = tree.getroot()
        body = root.find("body")
        print("Removing some useless sentence pairs...")
        for tu in root.iter("tu"):
            for tuv in tu.iter("tuv"):
                seg = tuv.find("seg")
                seg_t = seg.text
                if regex_rem.search(seg_t):
                    try:
                        body.remove(tu)
                        counter_art_rem += 1
                    except:                 # error usually occurs because the TU has just been eliminated
                        #print("An error occurred. TU was not removed: %s" % seg_t)
                        pass
        print("%i useless sentence pairs removed ('Art. ...' or other non-essential segments)." % counter_art_rem)
        print()

    def punct_digit_filter(self):
        '''
        Removing translation units where at least one segment contains punctuation and/or digits only.
        '''
        tree = self.tree
        counter_art_rem2 = 0
        nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}
        regex_rem2 = regex.compile(r"^[\d\p{Punct}\s]+$")
        root = tree.getroot()
        body = root.find("body")
        print("Removing TUs with at least one segment with punctuation and/or numbers only...")
        for tu in root.iter("tu"):
            source_segment = tu.find("./tuv[@xml:lang='it']/seg", namespaces=nsmap).text
            target_segment = tu.find("./tuv[@xml:lang='de']/seg", namespaces=nsmap).text
            if regex_rem2.search(source_segment) or regex_rem2.search(target_segment):
                try:
                    body.remove(tu)
                    counter_art_rem2 += 1
                    print(source_segment, "\n", target_segment, "\n\n")
                except:
                    #print("An error occurred. TU was not removed: %s" % source_segment, target_segment)
                    pass
        print("%i TUs removed (at least one of the segments has punctuation and/or numbers only)." % counter_art_rem2)
        print()

    def non_alphabetical_ratio_filter(self):
        '''
        Filtering out TUs with segments having a number-punctuation/letters ratio higher than 0.6
        '''
        tree = self.tree
        counter = 0
        root = tree.getroot()
        body = root.find("body")
        print("Removing segments with (numbers+punctuation)/letters ratio > 0.8...")
        for tu in root.iter("tu"):
            for tuv in tu.iter("tuv"):
                seg = tuv.find("seg")
                seg_t = seg.text
                numbers = sum(c.isdigit() for c in seg_t)
                letters = sum(c.isalpha() for c in seg_t)
                punctuation = sum(c in string.punctuation for c in seg_t)
                try:
                    ratio = (numbers + punctuation) / letters
                except ZeroDivisionError:
                    ratio = 0.9
                if ratio > 0.8:
                    #print(ratio, "\t", seg_t)
                    try:
                        body.remove(tu)
                        counter += 1
                        print(source_segment, "\n", target_segment, "\n\n")
                    except:
                        #print("An error occurred. TU was not removed: %s" % seg_t)
                        pass
        print("%i TUs removed ((numbers+punctuation)/letters ratio > 0.8)" % counter)
        print()

    def noise_cleaning(self):
        regex_patterns = [
            regex.compile(r"^(Art\. \d{1,3}/?(?:bis|ter|quater|quinquies|sexies|septies|octies|novies|decies|undecies|duodecies)?) ?\-? ?(\(?\p{Lu}.+)"),  # segments beginning with "Art. 1" or "Art. 1 - "
            regex.compile(r"^((.+))$"),                         # removing "" character at the end of some segments
            regex.compile(r"^[“„'\"](([^“„'\"”]+))[“'\"”]$"),     # removing quotes if only at the beginning and end of segments
            regex.compile(r"^(\(\d{1,3}\)|•|\.(?!\.)|\-|\*|·) ?(.+)$"),       # removing "(1) ", "• ", ". "* ", "· " and "- " from beginning of segment
            regex.compile(r"^[“„'\"]?(\(?[A-Z]\)|[a-z]?\d\d?[\.\)]|[a-m]{1,2}\.|[a-z]\)) ?(?!Jänner|Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)([\p{L}“„'\"”].+)[“„'\"]?$"),      #removing "1.", "a.", "1)", "a)", "(1)", "(a)", "a1)", "a1.", "A)", "(A)" (even when preceded by apostrophes or quotation marks)  # added final square parentheses to eliminate eventual final quotation marks; added exceptions for n. and numbers followed by months
            regex.compile(r"^((.+(\(.+\))?(?<! n|Nr|Art|art|\p{Lu})[\.\);,])) ?\d\d?\d?\)$"),       #removing numbers with closed parenthesis at end of segment, like "1)" (if not preceded by "Art.", "Nr.", "n.", ")
            regex.compile(r"^((.+)) ?\(\d\d?\d?\)$"),           # removing (1) from end of segments
            regex.compile(r"^(\()(.+)\)$"),                     # removing round brackets when both at beginning and end of segment
            regex.compile(r"^\[ ?((.+)) ?\]?$"),  # removing square brackets both at beginning and end of segments
            regex.compile(r"^[“„'\"]?\d{1,2}/?(bis|ter|quater|quinquies|sexies|septies|octies|novies|decies|undecies|duodecies) (.+)$"), #removing instances like "5/bis " at the beginning of the segment
            regex.compile(r"^(.''?\) )(\p{Lu}.+)$"),              # removing other noise (one/two apostrophes and a closed parenthesis) at the beginning of titles
            regex.compile(r"^((.+(?<! n| Nr| Art| art)\.)) \d\d?\.$"),      # removing numbers (1.) in sentence-final position (except when preceded by Nr. or n. or art)
            regex.compile(r"^(\d\d?\.\d\d?)\)? ?([\p{L}“„'\"”].+)$"),            # removing instances of particular numbers at sentence beginning, like "1.1" and "1.1)"
            regex.compile(r"^\(\d\d?/\w{3,10}\) ((.+))$"), #removing instances of (2/bis) and similar from beginning of segments
            regex.compile(r"^[A-Z] \d\d?\) ((.+))$"),    # removing instances of "A 12) " at the beginning of segments
            regex.compile(r"^(([^“„'\"”]+))[“'\"”]$"),     # removing quotes at the end of segment (if no other quotes in segment)
            regex.compile(r"^[“„'\"](([^“„'\"”]+))$"),     # removing quotes at the beginning of segment (if no other quotes in segment)
            regex.compile(r"^[IVX]{1,4}\.(\p{L}\.|\d\)) (.+)$"), # removing list markers with roman numeral and uppercase letter like "II.D." and "II.2)"
            regex.compile(r"^((.+))(>| \*\))$"),           # removing ">" and " *)" from end of segments
            regex.compile(r"^\d\d?\.\d\d?\.\d\d?(\.\d\d?)? ?((\p{L}.+))$"),   # removing "1.1.1" and "1.1.1.1" and "3.3.4.1.3" at the beginning of segments (with or without spaces)
            regex.compile(r"^\d\d?\.\d\d?\.\d\d?\.\d\d?\.\d\d? ?((\p{L}.+))$"), # removing "3.3.4.1.3" at the beginning of segments (with or without spaces)
            regex.compile(r"^[IVX]{1,4}[\.\)] ?((\p{L}.+))$"),    # remove uppercase roman numerals like "II." and "II)" from beginning of segments
            regex.compile(r"^\d\d?\.\d\d?\.(\d\d?\.)? ?(\p{L}.+)$"),       # remove "1.1." and "1.1.1."
            regex.compile(r"^\d\d?\.\d\d?\.\d\d?\.\d\d?\.(\d\d?\.)? ?(\p{L}.+)$"),  # remove "1.1.1.1." and "1.1.1.1.1."
            regex.compile(r"^[A-Z]{1,2}\.?\d\.? ((.+))$"),              # removing "C.5 ", "C.5. ", "H7 " at the beginning of segments
            regex.compile(r"^[A-MO-RT-Z]\. ((.+))$"),          #removing "A. " at the beginning of segments (except N. and S. (Numero; San Valentino etc.)
            regex.compile(r"^[A-Z]\d[\):] ((.+))$")             #removing "C3) " and "Q1: " at the beginning of sentences
        ]
        tree = self.tree
        counter_cleaned = 0
        root = tree.getroot()
        print("Yet another segment cleaning stage...")
        for tu in root.iter("tu"):
            for tuv in tu.iter("tuv"):
                seg = tuv.find("seg")
                seg_t = seg.text
                for regex_ in regex_patterns:                                   # iterating over list of regex patterns
                    if regex_.search(seg_t):
                        counter_cleaned += 1
                        #print(seg_t)
                        seg.text = regex_.search(seg_t).group(2)
                        #print(seg.text)
                        break                                               # to prevent regex overwriting on same segment
        if counter_cleaned == 0:
            global cleanable
            cleanable = False
        print("%i cleaning operations of noise at the beginning and end of segments." % counter_cleaned)
        print()

    def dehyphenation(self):
        '''
        It generates vocabularies for each corpus (it and de) and validates whether a hyphenated word is more frequent as
        1) hyphenated or 2) merged. If 2, it converts the word from hyphenated to merged.
        It has to be re-run because it considers only the first instance of hyphenated word in the sentence.
        '''
        tree = self.tree
        print("Generating vocabularies for dehyphenation...")
        corpus_it = []
        corpus_de = []
        nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}
        root = tree.getroot()

        for tu in root.iter("tu"):
            source_segment = tu.find("./tuv[@xml:lang='it']/seg", namespaces=nsmap).text
            target_segment = tu.find("./tuv[@xml:lang='de']/seg", namespaces=nsmap).text
            corpus_it.append(source_segment)
            corpus_de.append(target_segment)

        vocab_it = Counter(word_tokenize("\n".join(corpus_it)))    # italian vocabulary (dictionary of token:frequency)
        vocab_de = Counter(word_tokenize("\n".join(corpus_de)))    # german vocabulary

        def dehyph(root):
            counter_dehyphen_it = 0
            counter_dehyphen_de = 0
            print("Dehyphenating...")
            for tu in root.iter("tu"):
                source_segment = tu.find("./tuv[@xml:lang='it']/seg", namespaces=nsmap)
                target_segment = tu.find("./tuv[@xml:lang='de']/seg", namespaces=nsmap)
                source_text = source_segment.text
                target_text = target_segment.text
                re = regex.compile(r"(([A-Za-zöäüÖÄÜ]+)\-([A-Za-zöäüÖÄÜ]+))")
                found_it = regex.search(re, source_text)

                if found_it:
                    frequency_it_hyph = vocab_it[found_it.group(1)]
                    it_merged = found_it.group(2) + found_it.group(3)

                    try:
                        frequency_it_merged = vocab_it[it_merged]
                    except:
                        continue

                    if frequency_it_hyph >= frequency_it_merged:
                        continue
                    if frequency_it_hyph == 0:  # to avoid unexplainable ZeroDivisionError in the following elif
                        continue

                    elif (frequency_it_merged/frequency_it_hyph) > 10 and (frequency_it_merged+frequency_it_hyph) > 40:
                        # if hyphenated form occurs more than once, we modify it only if the merged form
                        # occurs more than 10x more than the hyphenated and their global frequency is > 40
                        #print(found_it.group(1))
                        #print(source_text)
                        new_it = regex.sub(re, it_merged, source_text, 1)
                        source_segment.text = new_it
                        #print(new_it)
                        #print()
                        counter_dehyphen_it += 1

                found_de = regex.search(re, target_text)

                if found_de:
                    frequency_de_hyph = vocab_de[found_de.group(1)]
                    de_merged = found_de.group(2) + found_de.group(3)

                    try:
                        frequency_de_merged = vocab_de[de_merged]
                    except:
                        continue

                    if frequency_de_hyph >= frequency_de_merged:
                        continue
                    if frequency_de_hyph == 0:  # to avoid unexplainable ZeroDivisionError in the following elif
                        continue

                    elif (frequency_de_merged / frequency_de_hyph) > 10 and (frequency_de_merged + frequency_de_hyph) > 40:
                        # if hyphenated form occurs more than once, we modify it only if the merged form
                        # occurs more than 10x more than the hyphenated and their global frequency is > 40
                        #print(found_de.group(1))
                        #print(target_text)
                        new_de = regex.sub(re, de_merged, target_text, 1)
                        target_segment.text = new_de
                        #print(new_de)
                        #print()
                        counter_dehyphen_de += 1

            print("Dehyphenated (Italian): ", counter_dehyphen_it)
            print("Dehypheanted (German): ", counter_dehyphen_de)

        for i in range(4):          # carry out dehyphenation 4 times
            root = tree.getroot()
            dehyph(root)

    def remove_blank_units(self):
        '''
        Removing 1:0 TUs. LF aligner actually already eliminates them, but new 1:0 TUs can be generated
        during other cleaning operations.
        '''
        tree = self.tree
        counter_rem = 0
        root = tree.getroot()
        body = root.find("body")
        print("Removing blank TUs...")
        for tu in root.iter("tu"):
            for tuv in tu.iter("tuv"):
                seg = tuv.find("seg")
                seg_t = seg.text
                regex_ = regex.compile(r"^\s+$")            # removing TUs where segments contain only whitespaces
                if regex_.search(seg_t):
                    body.remove(tu)
                    counter_rem += 1
                    #print(seg_t)
        print("%i TUs eliminated because half-empty." % counter_rem)
        print()

    def remove_whitespaces(self):
        '''
        Removing leading and trailing spaces
        '''
        tree = self.tree
        root = tree.getroot()
        print("Removing leading and trailing whitespaces...")
        for tu in root.iter("tu"):
            for tuv in tu.iter("tuv"):
                seg = tuv.find("seg")
                seg_t = seg.text
                regex_ = regex.compile(r"^\s*(.+)\s*$")        # clean TUs where segments start with whitespaces
                if regex_.search(seg_t):
                    seg.text = regex_.search(seg_t).group(1)
                    #print(seg_t)
        print("Corpus cleaned from leading and trailing whitespaces.")
        print()

    def language_filter(self):
        '''
        Discarding sentence pairs whose detected languages are not it-de.
        Workaround for unsolved issue of langid (doesn't work with segments with only UPPERCASE characters):
        if all uppercase, convert to lowercase, then run langid.
        '''
        tree = self.tree
        print("Removing TUs with wrong detected language...")
        langid.set_languages(['de', 'it'])
        nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}
        root = tree.getroot()
        body = root.find("body")
        counter = 0  # for testing purposes

        for tu in root.iter("tu"):
            source_segment = tu.find("./tuv[@xml:lang='it']/seg", namespaces=nsmap).text
            target_segment = tu.find("./tuv[@xml:lang='de']/seg", namespaces=nsmap).text

            if source_segment.isupper() and target_segment.isupper():
                source_segment = source_segment.lower()
                target_segment = target_segment.lower()

            try:
                detect_it = langid.classify(source_segment)
                detect_de = langid.classify(target_segment)
            except:
                continue

            if "de" in detect_it or "it" in detect_de:    # broader alternative (every language other than it or de) => if "it" not in detect_it or "de" not in detect_de:
                if len(source_segment.split()) > 8 and len(target_segment.split()) > 8: # just considering longer segments, shorter ones are more likely to be false positives
                    #print("\n\n", detect_it, detect_de, "\t", source_segment, "\n\t\t", target_segment)
                    body.remove(tu)
                    counter += 1

        print("%i TUs removed" % counter)

    def length_ratio_filter(self):
        '''
        Discarding sentence pairs whose length ratio is higher than a given threshold.
        [(longest_sentence + 15) / (shortest_sentence + 15)] > 1.5
        based on (https://github.com/modernmt/DataCollection/blob/dev/baseline/filter_hunalign_bitext.py)
        '''
        tree = self.tree
        print("Removing TUs with highly different length ratio between segments...")
        nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}
        root = tree.getroot()
        body = root.find("body")
        count = 0

        for tu in root.iter("tu"):
            source_segment = tu.find("./tuv[@xml:lang='it']/seg", namespaces=nsmap).text
            target_segment = tu.find("./tuv[@xml:lang='de']/seg", namespaces=nsmap).text
            li = [(len(source_segment) + 15), (len(target_segment) + 15)]
            li.sort(reverse=True)
            len_ratio = li[0] / li[1]

            if len_ratio > 1.5:
                body.remove(tu)
                #print(len_ratio, "\t", source_segment)
                #print("\t\t\t", target_segment)
                count += 1

        print("%i TUs removed because of high length ratio difference." % count)

    def filter_per_token(self, min, max):
        '''
        Filters out very long and very short segments according to number of tokens.
        '''
        counter = 0
        nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}
        tree = self.tree
        root = tree.getroot()
        body = root.find("body")
        print("Removing untranslated TUs...")

        for tu in root.iter("tu"):
            source_segment = tu.find("./tuv[@xml:lang='it']/seg", namespaces=nsmap).text
            target_segment = tu.find("./tuv[@xml:lang='de']/seg", namespaces=nsmap).text

            if len(source_segment.split()) < min or len(source_segment.split()) > max:
                body.remove(tu)
                counter += 1
                #print(source_segment)
                #print(target_segment)
                #print()

            elif len(target_segment.split()) < min or len(target_segment.split()) > max:
                body.remove(tu)
                counter += 1
                #print(target_segment)
                #print(source_segment)
                #print()
        print("%i segments filtered out because either shorter than %i tokens or longer than %i tokens." % (counter, min, max))

    def write(self):
        '''
        writing filtered and cleaned tmx parallel corpus as a separate file
        '''
        tree = self.tree
        oldFilename = Path(self.parallelCorpus).stem
        newFilename = oldFilename + "_cleaned.tmx"
        tree.write(newFilename, encoding="utf-8", xml_declaration=True)
        print("Done")







if __name__ == '__main__':
    #  defining and processing cmd arguments
    parser = argparse.ArgumentParser(description="Script for parallel corpus (tmx) cleaning and filtering")
    parser.add_argument("parallelCorpus", help="the parallel corpus in TMX format")
    args = parser.parse_args()
    parallelCorpus = args.parallelCorpus

    #  cleaning and filtering operations (order matters)
    corpus = ParallelCorpus(parallelCorpus)
    corpus.remove_untranslated()
    corpus.punct_digit_filter()
    corpus.non_alphabetical_ratio_filter()
    corpus.remove_whitespaces()
    corpus.remove_useless()
    corpus.noise_cleaning()
    cleanable = True  # refers to noise_cleaning(), becomes False when all segments are cleaned by the function
    while cleanable:
        corpus.noise_cleaning()
    corpus.remove_useless()
    corpus.remove_whitespaces()
    corpus.dehyphenation()
    corpus.punct_digit_filter()
    corpus.non_alphabetical_ratio_filter()
    corpus.noise_cleaning()
    corpus.remove_untranslated()
    corpus.remove_blank_units()
    corpus.language_filter()
    corpus.length_ratio_filter()
    corpus.filter_per_token(0, 80)


    #  writing clean corpus
    corpus.write()
