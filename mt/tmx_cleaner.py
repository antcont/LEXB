'''


todo: creare README dettagliato per tmx_cleaner.py e metterlo nel README.md principale
todo: fix total count of noise_cleaning()?

todo: aggiungere inversione se detected lang è de-it? ma in realtà potrebbe indicare comunque un segmento "sbagliato"... rimando a più avanti

A toolkit for cleaning and filtering the parallel corpus in .tmx format (aligned with LF Aligner) and getting clean sentence-sentence
translation units:
- remove_untranslated():    removes untranslated TUs, i.e. TUs with identical or almost identical source and target
- remove_art_and_co():      a first TU cleaning. Noise at sentence beginning is removed ("Art. 1"). TUs with segments
  containing only non-relevant noise (such as ""Art. 1". "(1)", "1." "1bis.") are removed from the TM.
- remove_punctuation_numeral_segments(): removes TUs with at least one segment containing only punctuation and/or
  numbers.
- noise_cleaning():     further TU cleaning. Noise at sentence beginning is removed: "(1)",
  "1.", "a.", "1)", "a)","1/bis" (even when preceded by apostrophes or quotation marks), parentheses (when both at the
  beginning   and the end of segments), noise at the beginning of law titles [such as "g'') "], "" symbol at the end
  of some segments, "&apos;" is substituted with regular apostrophe, etc.
- remove_blank_units():     removes TUs containing segments with only whitespaces.
- remove_whitespaces():     removes leading and trailing whitespaces.
- select_TUs_with_wrong_lang():     allows manual selection (delete or retain) of TUs containing segments whose detected
  language does not match the default it/de language.
- select_TUs_with_different_lenght():    allows manual selection (delete or retain) of TUs whose length difference ratio
  is higher than a given threshold (indicating possible misalignment).
- filter_per_token():   removing very long and very short segments (according to token number, which can be set manually)
'''

import langid
import regex
import string
from Levenshtein import distance
from collections import Counter
from lxml import etree
from nltk import word_tokenize


tmx_path = r"C:\Users\anton\Dropbox\Eurac_tesi\custom_MT\corpus\stplc_19102020_DeF_cleaned.tmx"  # insert path of the .tmx file
txt_path = r"C:\Users\anton\Documents\Documenti importanti\SSLMIT FORLI M.A. SPECIALIZED TRANSLATION 2019-2021\tesi\corpus\stplc_08022021_raw - test_cleaning14022020.txt"  # insert path to the .txt file (for deduplicate() only)



def remove_untranslated(path):
    '''
    Removing TUs with identical or almost identical source and target.
    Almost identical source-target: sentence pairs with a Levenshtein edit distance < 2.0
    or an edit distance ratio < 0.1 (Lu et al. 2018)
    '''
    counter_untr = 0
    counter_similar = 0
    nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}
    tree = etree.parse(path)                                        # parsing the TMX file
    root = tree.getroot()
    body = root.find("body")
    print("Removing untranslated TUs...")
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
    tree.write(path, encoding="UTF-8", xml_declaration=True)                                                  # overwriting the TM
    print("%i untranslated TUs removed." % counter_untr)
    print("%i highly similar TUs removed." % counter_similar)
    print()


'''A first segment cleaning stage.'''
def remove_art_and_co(path):
    counter_art_mod = 0
    counter_art_rem = 0
    regex_mod = regex.compile(r"^(Art\. \d{1,3}/?(bis|ter|quater|quinquies|sexies|septies|octies|novies|decies|undecies|duodecies)?) ?\-? ?(\(?\p{Lu}.+)")       #segments beginning with "Art. 1" or "Art. 1 - "
    regex_rem = regex.compile(r"^(Art\. \d{1,3}|\(\d{1,3}\)|\d{1,3}(bis|ter|quater|quinquies|sexies|septies|octies|novies|decies|undecies|duodecies)?\.)$")        # TUs where at least one segment is only "Art. 1". "(1)", "1." "1bis."
    tree = etree.parse(path)
    root = tree.getroot()
    body = root.find("body")
    print("Cleaning segments and removing useless TUs...")
    for tu in root.iter("tu"):
        for tuv in tu.iter("tuv"):
            seg = tuv.find("seg")
            seg_t = seg.text
            if regex_mod.search(seg_t):
                print(seg_t)           #for testing purposes
                seg.text = regex_mod.search(seg_t).group(3)
                print(seg.text)        #for testing purposes
                print()
                counter_art_mod += 1
            '''if regex_rem.search(seg_t):
                try:
                    body.remove(tu)
                    counter_art_rem += 1
                except:                 # error usually occurs because the TU has just been eliminated
                    #print("An error occurred. TU was not removed: %s" % seg_t)
                    pass'''
    tree.write(path, encoding="UTF-8", xml_declaration=True)
    print("%i segments cleaned from 'Art. 1' at beginning of the sentence" % counter_art_mod)
    print("%i TUs removed ('Art. ...' or other non-essential segments only)." % counter_art_rem)
    print()

def punct_digit_filter(path):
    '''
    Removing translation units whose at least one segment contains punctuation and/or digits only.
    '''
    counter_art_rem2 = 0
    nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}
    regex_rem2 = regex.compile(r"^[\d\p{Punct}\s]+$")
    tree = etree.parse(path)
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
            except:
                #print("An error occurred. TU was not removed: %s" % source_segment, target_segment)
                pass
    tree.write(path, encoding="UTF-8", xml_declaration=True)
    print("%i TUs removed (at least one of the segments has punctuation and/or numbers only)." % counter_art_rem2)
    print()


def non_alphabetical_ratio_filter(path):
    '''
    Filtering out TUs with segments having a number-punctuation/letters ratio higher than 0.6
    '''
    counter = 0
    tree = etree.parse(path)
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
                except:
                    #print("An error occurred. TU was not removed: %s" % seg_t)
                    pass
    tree.write(path, encoding="UTF-8", xml_declaration=True)
    print("%i TUs removed ((numbers+punctuation)/letters ratio > 0.8)" % counter)
    print()

''' RegEx patterns for noise_cleaning() '''
patterns = [
    regex.compile(r"^((.+))$"),                         # removing strange "" character at the end of some segments
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

def noise_cleaning_part(path, regexes):
    counter_cleaned = 0
    tree = etree.parse(path)
    root = tree.getroot()
    print("Yet another segment cleaning stage...")
    for tu in root.iter("tu"):
        for tuv in tu.iter("tuv"):
            seg = tuv.find("seg")
            seg_t = seg.text
            for regex_ in regexes:                                      # iterating over list of regex patterns
                if regex_.search(seg_t):
                    counter_cleaned += 1
                    print(seg_t)
                    seg.text = regex_.search(seg_t).group(2)
                    print(seg.text)
                    break                                               # to prevent regex overwriting on same segment
    tree.write(path, encoding="UTF-8", xml_declaration=True)
    print("Partial cleaning done (%i segments)." % counter_cleaned)
    return counter_cleaned

def noise_cleaning(path, regexes):
    '''
    A second, Regex-based segment cleaning stage.
    '''
    counter_cleaned = noise_cleaning_part(path, regexes)
    noise_cleaning_part(path, regexes)
    total_cleaned = counter_cleaned
    if counter_cleaned != 0:
        noise_cleaning_part(path, regexes)
        total_cleaned += counter_cleaned
    print("%i total segments cleaned." % total_cleaned)



def dehyphenation(path):
    '''
    It generates vocabularies for each corpus (it and de) and validates whether a hyphenated word is more frequent as
    1) hyphenated or 2) merged. If 2, it converts the word from hyphenated to merged.
    It has to be re-run because it considers only the first instance of hyphenated word in the sentence.
    '''
    #Generating vocabularies
    print("Generating vocabularies...")
    corpus_it = []
    corpus_de = []
    nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}
    tree = etree.parse(path)  # parsing the TMX file
    root = tree.getroot()
    for tu in root.iter("tu"):
        source_segment = tu.find("./tuv[@xml:lang='it']/seg", namespaces=nsmap).text
        target_segment = tu.find("./tuv[@xml:lang='de']/seg", namespaces=nsmap).text
        corpus_it.append(source_segment)
        corpus_de.append(target_segment)
    tokens_it = word_tokenize("\n".join(corpus_it))
    tokens_de = word_tokenize("\n".join(corpus_de))
    vocab_it = Counter(tokens_it)                   # italian vocabulary (dictionary of token:frequency)
    vocab_de = Counter(tokens_de)                   # german vocabulary
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
            elif frequency_it_merged > frequency_it_hyph:
                print(found_it.group(1))
                print(source_text)
                new_it = regex.sub(re, it_merged, source_text, 1)
                source_segment.text = new_it
                print(new_it)
                print()
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
            elif frequency_de_merged > frequency_de_hyph:
                print(found_de.group(1))
                print(target_text)
                new_de = regex.sub(re, de_merged, target_text, 1)
                target_segment.text = new_de
                print(new_de)
                print()
                counter_dehyphen_de += 1
    tree.write(path, encoding="UTF-8", xml_declaration=True)
    print("Dehyphenated (Italian): ", counter_dehyphen_it)
    print("Dehypheanted (German): ", counter_dehyphen_de)


def remove_blank_units(path):
    '''
    Removing 1:0 TUs. LF aligner actually already eliminates them, but new 1:0 TUs can be generated
    during other cleaning operations.
    '''
    counter_rem = 0
    tree = etree.parse(path)
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
    tree.write(path, encoding="UTF-8", xml_declaration=True)
    print("%i TUs eliminated because half-empty." % counter_rem)
    print()


def remove_whitespaces(path):
    '''
    Removing leading and trailing spaces
    '''
    counter_whi = 0
    tree = etree.parse(path)
    root = tree.getroot()
    print("Removing leading and trailing whitespaces and other noise...")
    for tu in root.iter("tu"):
        for tuv in tu.iter("tuv"):
            seg = tuv.find("seg")
            seg_t = seg.text
            regex_ = regex.compile(r"^\s*(.+)\s*$")        # clean TUs where segments start with whitespaces
            if regex_.search(seg_t):
                seg.text = regex_.search(seg_t).group(1)
                counter_whi += 1
                #print(seg_t)
    tree.write(path, encoding="UTF-8", xml_declaration=True)              # overwriting the old file
    print("\n\n%i segments cleaned from whitespaces and other noise.\n\n" % counter_whi)
    print()


def language_filter(path):
    '''
    Discarding sentence pairs whose detected languages are not it-de.
    Roundabout for unsolved issue of langid (doesn't work with segments with only UPPERCASE characters):
    if all uppercase, convert to lowercase, then run langid.
    '''
    print("Removing TUs with wrong detected language...")
    langid.set_languages(['de', 'it'])
    nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}
    tree = etree.parse(path)
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
    tree.write(path, encoding="UTF-8", xml_declaration=True)
    print("%i TUs removed" % counter)

#reimplement the following to select segments manually (user input)
'''
                print("\n\n", detect_it, detect_de, "\t", source_segment, "\n\t\t", target_segment)
                keep_delete = input("\nDo you want to retain this TU? (y/n) Press 's' to save")
                print(keep_delete)
                if keep_delete == "y":
                    print("\nOk, I will retain this TU.")
                elif keep_delete == "n":
                    print("\nOk, I will delete this TU.")
                    body.remove(tu)
                elif keep_delete == "s":
                    tree.write(path, encoding="UTF-8")
                else:
                    print("\nWrong input. TU has been retained.")
                
    tree.write(path, encoding="UTF-8")
'''


def length_ratio_filter(path):
    '''
    Discarding sentence pairs whose length ratio is higher than a given threshold.
    [(longest_sentence + 15) / (shortest_sentence + 15)] > 1.8
    '''
    print("Removing TUs with highly different length ratio between segments...")
    nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}
    tree = etree.parse(path)
    root = tree.getroot()
    body = root.find("body")
    count = 0
    for tu in root.iter("tu"):
        source_segment = tu.find("./tuv[@xml:lang='it']/seg", namespaces=nsmap).text
        target_segment = tu.find("./tuv[@xml:lang='de']/seg", namespaces=nsmap).text
        li = [(len(source_segment) + 15), (len(target_segment) + 15)]
        li.sort(reverse=True)
        len_ratio = li[0] / li[1]
        if len_ratio > 1.8:
            body.remove(tu)
            print(len_ratio, "\t", source_segment)
            print("\t\t\t", target_segment)
            count += 1
    tree.write(path, encoding="UTF-8", xml_declaration=True)
    print("%i TUs removed because of high length ratio difference." % count)


#reimplement for manual selection (user input)
'''                
                print("\n\n", len(source_segment), " ", len(target_segment), "\t\t", source_segment, "\n", "{0:.3f}".format(len_ratio), "\t\t\t", target_segment)
                keep_delete = input("\nDo you want to retain this TU? (y/n) Press 's' to save")
                print(keep_delete)
                if keep_delete == "y":
                    print("\nOk, I will retain this TU.")
                elif keep_delete == "n":
                    print("\nOk, I will delete this TU.")
                    body.remove(tu)
                    count += 1
                elif keep_delete == "s":
                    tree.write(path, encoding="UTF-8")
                else:
                    print("\nWrong input. TU has been retained.")
    print("%i TUs were eliminated" % count)
    tree.write(path, encoding="UTF-8", xml_declaration=True)              # overwriting the old file
'''

def segment_counter(path, n):
    '''
    A simple sentence pair counter according to a given length (tokens).
    '''
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
        if len(source_tokens) >= n and len(target_tokens) >= n:
            counter_right_length += 1
    print(counter_total)
    print(counter_right_length)

def filter_per_token(path, min, max):
    '''
    Filters out very long and very short segments according to number of tokens.
    '''
    counter = 0
    nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}
    tree = etree.parse(path)                                        # parsing the TMX file
    root = tree.getroot()
    body = root.find("body")
    print("Removing untranslated TUs...")
    for tu in root.iter("tu"):
        source_segment = tu.find("./tuv[@xml:lang='it']/seg", namespaces=nsmap).text
        target_segment = tu.find("./tuv[@xml:lang='de']/seg", namespaces=nsmap).text
        if len(source_segment.split()) < min or len(source_segment.split()) <= max:
            #body.remove(tu)
            counter += 1
            print(source_segment)
            print(target_segment)
            print()
        if len(target_segment.split()) < min or len(target_segment.split()) <= max:
            #body.remove(tu)
            counter += 1
            print(target_segment)
            print(source_segment)
            print()
    #tree.write(path, encoding="UTF-8", xml_declaration=True)
    print("%i segments filtered out because either shorter than %i tokens or longer than %i tokens." % (counter, min, max))


def remove_longer_than_n(path, n):
    counter = 0
    nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}
    tree = etree.parse(path)  # parsing the TMX file
    root = tree.getroot()
    body = root.find("body")
    print("Removing TU with segments longer than 100 words...")
    for tu in root.iter("tu"):
        source_segment = tu.find("./tuv[@xml:lang='it']/seg", namespaces=nsmap).text
        target_segment = tu.find("./tuv[@xml:lang='de']/seg", namespaces=nsmap).text
        source_tokens = source_segment.split()
        target_tokens = target_segment.split()
        if len(source_tokens) >= n or len(target_tokens) >= n:
            body.remove(tu)
            counter += 1
    tree.write(path, encoding="UTF-8", xml_declaration=True)
    print("%i TUs removed because very long (more than %i words)." % (counter, n))


def deduplicate(path):
    '''
    More sophisticated deduplicator (based on Pinnis 2018)
    In order to do so:
    - whitespaces and punctuation are removed
    - dates are replaced with placeholder
    - numbers are replaced with a placeholder
    - sentence pairs are lowercased
    :param path: path to the tab-separated .txt corpus as input file
    '''
    with open(path, "r", encoding="utf-8") as inputfile:
        input_lines = inputfile.readlines()
    counter_segments_before = len(input_lines)
    print("Deduplicating TUs...")
    tu_dict = {}
    for line in input_lines:
        modified = line.rstrip("\n").lower().replace(" ", "")  # lowercasing and removing simple whitespaces
        punctuation = regex.compile(r"[\\!\"#\$%&'\(\)\*\+,\-\./:;<=>\?@\[\]\^_`\{\|\}~„“”]")
        numbers = regex.compile(r"\d+")
        while regex.search(punctuation, modified):
            modified = regex.sub(punctuation, "", modified)  # removing punctuation
        while regex.search(numbers, modified):
            modified = regex.sub(numbers, "X", modified)  # substituting digits with "X" placeholder
            tu_dict[line.rstrip("\n")] = modified
    new_dict = {}
    for x, y in tu_dict.items():                    #deduplication
        if y not in new_dict.values():
            new_dict[x] = y
        else:
            print(x)
    new_txt_list = ["it-IT\tde-DE"]                               #generating filtered output corpus
    for x, y in new_dict.items():
        new_txt_list.append(x)
    counter_segments_after = len(new_txt_list)
    counter_eliminated = counter_segments_before - counter_segments_after
    deduplicated_corpus = "\n".join(new_txt_list)   # converting to tab-separated txt
    with open(path, "w", encoding="utf-8") as output:
        output.write(deduplicated_corpus)
    print("%i TUs deduplicated." % counter_eliminated)




''' LET'S CLEAN! Activate desired cleaning operations '''

#remove_art_and_co(tmx_path)

noise_cleaning(tmx_path, patterns)

#remove_whitespaces(tmx_path)

#dehyphenation(tmx_path)


#punct_digit_filter(tmx_path)

#non_alphabetical_ratio_filter(tmx_path)

#remove_untranslated(tmx_path)

#remove_blank_units(tmx_path)

#language_filter(tmx_path)

#length_ratio_filter(tmx_path)



#deduplicate(txt_path)

#filter_per_token(tmx_path, 0, 1)

#segment_counter(tmx_path)

#remove_longer_than_n(tmx_path, 100)

print("Done!")