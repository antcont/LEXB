'''

todo: creare README dettagliato per tmx_cleaner.py e metterlo nel README.md principale
todo: rimuovere segmenti composti da sola punteggiatura

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
from lxml import etree
from difflib import SequenceMatcher

tmx_path = r"C:\Users\anton\Dropbox\Eurac_tesi\custom_MT\corpus\stplc_08022021_cleaned_no-TMop.tmx"  # insert path of the .tmx file

'''Removing TUs with identical or almost identical source and target'''
def remove_untranslated(path):
    counter_untr = 0
    nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}
    tree = etree.parse(path)                                        # parsing the TMX file
    root = tree.getroot()
    body = root.find("body")
    print("Removing untranslated TUs...")
    for tu in root.iter("tu"):
        source_segment = tu.find("./tuv[@xml:lang='IT']/seg", namespaces=nsmap).text
        target_segment = tu.find("./tuv[@xml:lang='DE']/seg", namespaces=nsmap).text
        if source_segment == target_segment:
            try:
                body.remove(tu)
                counter_untr += 1
            except:
                print("An error occurred. TU was not removed: %s \t %s" % (source_segment, target_segment))
                pass
        if len(source_segment) > 15 and len(target_segment) > 15 and SequenceMatcher(None, source_segment, target_segment).ratio() > 0.9:
        # print(source_segment, "\n", target_segment, "\n")
            try:
                body.remove(tu)
                counter_untr += 1
            except:
                print("An error occurred. TU was not removed: %s \t %s" % (source_segment, target_segment))
                pass
    tree.write(path, encoding="UTF-8", xml_declaration=True)                                                  # overwriting the TM
    print("%i untranslated TUs removed." % counter_untr)
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
                counter_art_mod += 1
            if regex_rem.search(seg_t):
                try:
                    body.remove(tu)
                    counter_art_rem += 1
                except:
                    print("An error occurred. TU was not removed: %s" % seg_t)
                    pass
    tree.write(path, encoding="UTF-8", xml_declaration=True)
    print("%i segments cleaned from 'Art. 1' at beginning of the sentence" % counter_art_mod)
    print("%i TUs removed ('Art. ...' or other non-essential segments only)." % counter_art_rem)
    print()

''' Removing translation units whose at least one segment contains punctuation and/or numbers only '''
def remove_punctuation_numeral_segments(path):
    counter_art_rem2 = 0
    nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}
    regex_rem2 = regex.compile(r"^[\d\W\s]+$")
    tree = etree.parse(path)
    root = tree.getroot()
    body = root.find("body")
    print("Removing TUs with at least one segment with punctuation and/or numbers only...")
    for tu in root.iter("tu"):
        source_segment = tu.find("./tuv[@xml:lang='IT']/seg", namespaces=nsmap).text
        target_segment = tu.find("./tuv[@xml:lang='DE']/seg", namespaces=nsmap).text
        if regex_rem2.search(source_segment) or regex_rem2.search(target_segment):
            try:
                body.remove(tu)
                counter_art_rem2 += 1
            except:
                print("An error occurred. TU was not removed: %s" % source_segment, target_segment)
                pass
    tree.write(path, encoding="UTF-8", xml_declaration=True)
    print("%i TUs removed (at least one of the segments has punctuation and/or numbers only)." % counter_art_rem2)
    print()

''' RegEx patterns for noise_cleaning() '''
patterns = [
    regex.compile(r"^((.+))$"),                       # removing strange "" character at the end of some segments
    regex.compile(r"^[“„'\"](([^“„'\"”]+))[“'\"”]$"),     # removing quotes if only at the beginning and end of segments
    regex.compile(r"^(\(\d{1,3}\)|•|\.(?!\.)|\-) ?(.+)$"),       # removing "(1) ", "• ", ". " and "- " from beginning of segment
    regex.compile(r"^[“„'\"]?(\(?[A-Z]\)|[a-z]?\d\d?[\.\)]|[a-m]{1,2}\.|[a-z]\)) ?(?!Jänner|Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)([\p{Lu}\p{Ll}“„'\"”].+)[“„'\"]?$"),      #removing "1.", "a.", "1)", "a)", "(1)", "(a)", "a1)", "a1.", "A)", "(A)" (even when preceded by apostrophes or quotation marks)  # added final square parentheses to eliminate eventual final quotation marks; added exceptions for n. and numbers followed by months
    regex.compile(r"^(((?!\().+(?<! n|Nr|Art|art|\p{Lu}|\d)[\.\)])) ?\(?\d\d?\)$"),       #removing numbers with closed parenthesis at end of segment, like "1)" and "(1)" (if not preceded "Art.", "Nr.", "n.", ")
    regex.compile(r"^(\()(.+)\)$"),                     # removing parentheses when both at beginning and end of segment
    regex.compile(r"^\[ ?((.+)) ?\]?$"),  # removing square brackets both at beginning and end of segments
    regex.compile(r"^[“„'\"]?\d{1,2}/?(bis|ter|quater|quinquies|sexies|septies|octies|novies|decies|undecies|duodecies) (.+)$"), #removing instances like "5/bis " at the beginning of the segment
    regex.compile(r"^(.''?\) )(\p{Lu}.+)$"),              # removing other noise (one/two apostrophes and a closed parenthesis) at the beginning of titles
    regex.compile(r"^((.+(?<! n| Nr| Art| art)\.)) \d\d?\.$"),      # removing numbers (1.) in sentence-final position (except when preceded by Nr. or n. or art)
    regex.compile(r"^(\d\d?\.\d\d?)\)? ?([\p{Lu}\p{Ll}“„'\"”].+)$"),            # removing instances of particular numbers at sentence beginning, like "1.1" and "1.1)"
    regex.compile(r"^\(\d\d?/\w{3,10}\) ((.+))$"), #removing instances of (2/bis) and similar from beginning of segments
    regex.compile(r"^[A-Z] \d\d?\) ((.+))$"),    # removing instances of "A 12) " at the beginning of segments
    regex.compile(r"^(([^“„'\"”]+))[“'\"”]$"),     # removing quotes at the end of segment (if no other quotes in segment)
    regex.compile(r"^[“„'\"](([^“„'\"”]+))$"),     # removing quotes at the beginning of segment (if no other quotes in segment)
    regex.compile(r"^[IVX]{1,4}\.([\p{Lu}]\.|\d\)) (.+)$"), # removing list markers with roman numeral and uppercase letter like "II.D." and "II.2)"
    regex.compile(r"^((.+))(>| \*\))$"), # removing ">" and " *)" from end of segments
    regex.compile(r"^\d\d?\.\d\d?\.\d\d?(\.\d\d?)? ?((\p{Lu}.+))$"),   # removing "1.1.1" and "1.1.1.1" at the beginning of segments (with or without spaces)
    regex.compile(r"^[IVX]{1,4}[\.\)] ?((\p{Lu}.+))$")    # remove uppercase roman numerals like "II." and "II)" from beginning of segments
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
                    #print(seg_t)
                    seg.text = regex_.search(seg_t).group(2)
                    #print(seg.text)
                    break                                               # to prevent regex overwriting on same segment
    tree.write(path, encoding="UTF-8", xml_declaration=True)
    print("Partial cleaning done (%i segments)." % counter_cleaned)
    return counter_cleaned

'''A second segment cleaning stage. Recursive until there's no more uncleaned segments'''
def noise_cleaning(path, regexes):
    total_cleaned = 0
    noise_cleaning_part(path, regexes)
    counter_cleaned = noise_cleaning_part(path, regexes)
    if total_cleaned == 0:
        total_cleaned = counter_cleaned
    if counter_cleaned != 0:
        noise_cleaning_part(path, regexes)
        total_cleaned += counter_cleaned
    print("%i total segments cleaned." % total_cleaned)


'''Removing 1:0 TUs'''          # LF aligner actually already eliminates them, but new 1:0 TUs can be generated during other cleaning operations
def remove_blank_units(path):
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
                print(seg_t)
    tree.write(path, encoding="UTF-8", xml_declaration=True)
    print("%i TUs eliminated because half-empty." % counter_rem)
    print()


'''Removing leading and trailing spaces, list symbols, (•,-, etc.)'''
def remove_whitespaces(path):
    counter_whi = 0
    tree = etree.parse(path)
    root = tree.getroot()
    print("Removing leading and trailing whitespaces and other noise...")
    for tu in root.iter("tu"):
        for tuv in tu.iter("tuv"):
            seg = tuv.find("seg")
            seg_t = seg.text
            regex_ = regex.compile(r"^\s+?[•-]?\s*(.+)\s*$")        # clean TUs where segments start with whitespaces or list symbols
            if regex_.search(seg_t):
                seg.text = regex_.search(seg_t).group(1)
                counter_whi += 1
                #print(seg_t)
    tree.write(path, encoding="UTF-8", xml_declaration=True)              # overwriting the old file
    print("\n\n%i segments cleaned from whitespaces and other noise.\n\n" % counter_whi)
    print()


def select_TUs_with_wrong_lang(path):
    '''
    Printing single TUs with wrong detected language; user input to retain or eliminate the TU
    Roundabout for unsolved issue of langid (doesn't work with segments with only UPPERCASE characters)
    '''
    print("Removing TUs with wrong detected language...")
    langid.set_languages(['de', 'it'])
    nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}
    tree = etree.parse(path)
    root = tree.getroot()
    body = root.find("body")
    counter = 0  # for testing purposes
    for tu in root.iter("tu"):
        source_segment = tu.find("./tuv[@xml:lang='IT']/seg", namespaces=nsmap).text
        target_segment = tu.find("./tuv[@xml:lang='DE']/seg", namespaces=nsmap).text
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
                print("\n\n", detect_it, detect_de, "\t", source_segment, "\n\t\t", target_segment)
                body.remove(tu)
                counter += 1
    tree.write(path, encoding="UTF-8", xml_declaration=True)
    print("%i TUs removed" % counter)

#reimplement the following to select segments manually, even though it is convenient
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


'''
Printing single TUs with significant length difference; user input to retain or eliminate the TU


ModernMT cleaner (ModernMT/DataCollection/baseline/filter_hunalign_bitext.py) uses a similar approach: to solve the 
problem for short segments, they add 15 (words or characters? I think characters...). My current criteria are not as 
strict (discarding only segments with difference higher than 2x, instead MMT higher than 1,5x)

if float((len(source) + 15)) / float(len(target) + 15) > 1.5:
'''
def select_TUs_with_different_lenght(path):
    print("Removing TUs with highly different length ratio between segments...")
    nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}
    tree = etree.parse(path)
    root = tree.getroot()
    body = root.find("body")
    count = 0
    for tu in root.iter("tu"):
        source_segment = tu.find("./tuv[@xml:lang='IT']/seg", namespaces=nsmap).text
        target_segment = tu.find("./tuv[@xml:lang='DE']/seg", namespaces=nsmap).text
        li = [(len(source_segment) + 15), (len(target_segment) + 15)]
        li.sort(reverse=True)
        len_ratio = li[0] / li[1]
        if len_ratio > 2:
            body.remove(tu)
            print(source_segment)
            print("\t", target_segment)
            count += 1
    tree.write(path, encoding="UTF-8", xml_declaration=True)
    print("%i TUs removed because the lenght of one segment is more than double of the other segment" % count)


#reimplement for manual selection
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

'''funzione di prova giusto per contare quante frasi parallele ho che rispettino il criterio di lunghezza di 10-20 parole'''
def segment_counter(path):
    nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}
    tree = etree.parse(path)
    root = tree.getroot()
    counter_total = 0
    counter_right_length = 0
    for tu in root.iter("tu"):
        counter_total += 1
        source_segment = tu.find("./tuv[@xml:lang='IT']/seg", namespaces=nsmap).text
        target_segment = tu.find("./tuv[@xml:lang='DE']/seg", namespaces=nsmap).text
        source_tokens = source_segment.split()
        target_tokens = target_segment.split()
        if 8 <= len(source_tokens) <= 22 and 8 <= len(target_tokens) <= 22:
            counter_right_length += 1
    print(counter_total)
    print(counter_right_length)

def filter_per_token(path, min, max):
    '''
    Filters out very long and very short segments
    according to number of tokens
    '''
    counter = 0
    nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}
    tree = etree.parse(path)                                        # parsing the TMX file
    root = tree.getroot()
    body = root.find("body")
    print("Removing untranslated TUs...")
    for tu in root.iter("tu"):
        source_segment = tu.find("./tuv[@xml:lang='IT']/seg", namespaces=nsmap).text
        target_segment = tu.find("./tuv[@xml:lang='DE']/seg", namespaces=nsmap).text
        if len(source_segment.split()) < min or len(source_segment.split()) > max:
            #body.remove(tu)
            counter += 1
            print(source_segment)
        if len(target_segment.split()) < min or len(target_segment.split()) > max:
            #body.remove(tu)
            counter += 1
            print(target_segment)
    tree.write(path, encoding="UTF-8", xml_declaration=True)
    print("%i segments filtered out because either shorter than %i tokens or longer than %i tokens." % (counter, min, max))


''' LET'S CLEAN! Activate desired cleaning operations '''

remove_untranslated(tmx_path)

remove_art_and_co(tmx_path)

remove_punctuation_numeral_segments(tmx_path)

noise_cleaning(tmx_path, patterns)

remove_whitespaces(tmx_path)

#select_TUs_with_wrong_lang(tmx_path)                # manual selection

select_TUs_with_different_lenght(tmx_path)         # manual selection

remove_blank_units(tmx_path)

#filter_per_token(tmx_path, 3, 80)

#segment_counter(tmx_path)

print("Done!")