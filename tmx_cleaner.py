'''




#counted number of TUs with wrong language detected (just it-de, and just segments > 8 words) ==

A toolkit for cleaning the parallel corpus in .tmx format (aligned with LF Aligner) and getting clean sentence-sentence
translation units:
- remove_untranslated():    removes untranslated TUs, i.e. TUs with identical source and target
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
'''

from langdetect import detect
import regex
from lxml import etree

tmx_path = r"C:\Users\anton\Desktop\prove_download_scraper\prova19.10\merged_tmx19 - cleaned_20.01.2021.tmx"  # insert path of the .tmx file

'''Removing TUs with identical source and target'''
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
            body.remove(tu)                                                             # removing untranslated TUs
            counter_untr += 1
    tree.write(path, encoding="UTF-8")                                                  # overwriting the TM
    print("%i untranslated TUs removed." % counter_untr)
    print()


'''A first segment cleaning stage.'''
def remove_art_and_co(path):
    counter_art_mod = 0
    counter_art_rem = 0
    regex_mod = regex.compile(r"^(Art\. \d{1,2}/?(bis|ter|quater|quinquies|sexies|septies|octies|novies|decies|undecies|duodecies)?) ?\-? ?(\(?\p{Lu}.+)")       #segments beginning with "Art. 1" or "Art. 1 - "
    regex_rem = regex.compile(r"^(Art\. \d{1,2}|\(\d{1,2}\)|\d{1,2}(bis|ter|quater|quinquies|sexies|septies|octies|novies|decies|undecies|duodecies)?\.)$")        # TUs where at least one segment is only "Art. 1". "(1)", "1." "1bis."
    tree = etree.parse(path)
    root = tree.getroot()
    body = root.find("body")
    print("Cleaning segments and removing useless TUs...")
    for tu in root.iter("tu"):
        for tuv in tu.iter("tuv"):
            seg = tuv.find("seg")
            seg_t = seg.text
            if regex_mod.search(seg_t):
                print(seg_t)
                seg.text = regex_mod.search(seg_t).group(3)
                print(seg.text)
                counter_art_mod += 1
            if regex_rem.search(seg_t):
                try:
                    body.remove(tu)
                    counter_art_rem += 1
                except:
                    print("An error occurred. TU was not removed: %s" % seg_t)
                    pass
    tree.write(path, encoding="UTF-8")
    print("%i segments cleaned from 'Art. 1' at beginning of the sentence" % counter_art_mod)
    print("%i TUs removed ('Art. ...' or other non-essential segments only)." % counter_art_rem)
    print()

''' Removing translation units whose at least one segment contains punctuation and/or numbers only '''
def remove_punctuation_numeral_segments(path):
    counter_art_rem2 = 0
    nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}
    regex_rem2 = regex.compile(r"^[\d\W]+$")
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
    tree.write(path, encoding="UTF-8")
    print("%i TUs removed (at least one of the segments has punctuation and/or numbers only)." % counter_art_rem2)
    print()

''' RegEx patterns for noise_cleaning() '''
patterns = [
    regex.compile(r"^((.+))$"),                       # removing strange "" character at the end of some segments
    regex.compile(r"^[“„'\"](([^“„'\"”]+))[“'\"”]$"),     # removing quotes if only at the beginning and end of segments
    regex.compile(r"^(\(\d{1,3}\)|•|\.(?!\.)|\-) ?(.+)$"),       # removing "(1) ", "• ", ". " and "- " from beginning of segment
    regex.compile(r"^[“„'\"]?(\d\d?[\.\)]|[a-mo-z]{1,2}\.|[a-z]\)) (?!Jänner|Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)([A-Za-z].+)[“„'\"]?$"),      #removing "1.", "a.", "1)", "a)" (even when preceded by apostrophes or quotation marks)  # added final square parentheses to eliminate eventual final quotation marks; added exceptions for n. and numbers followed by months
    regex.compile(r"^(((?!\().+(?<! n|Nr|Art|art)[\.\)])) ?\d\d?\)$"),       #removing numbers with closed parenthesis at end of segment, like "12)" (if not preceded "Art.", "Nr.", "n.", ")
    regex.compile(r"^(\()(.+)\)$"),                     # removing parentheses when both at beginning and end of segment
    regex.compile(r"^[“„'\"]?\d{1,2}/?(bis|ter|quater|quinquies|sexies|septies|octies|novies|decies|undecies|duodecies) (.+)$"), #removing instances like "5/bis " at the beginning of the segment
    regex.compile(r"^(.''?\) )(\p{Lu}.+)$"),              # removing other noise (one/two apostrophes and a closed parenthesis) at the beginning of titles
    regex.compile(r"^((.+(?<! n| Nr)\.)) \d\.$"),      # removing numbers (1.) in sentence-final position (except when preceded by Nr. or n.)
    regex.compile(r"^(\d\.\d)\)? ?([A-Za-z].+)$"),                  # removing instances of particular numbers at sentence beginning, like "1.1" and "1.1)"
    regex.compile(r"^\[ ?((.+)) ?\]?$"),             # removing square brackets both at beginning and end of segments
    regex.compile(r"^\(\d\d?/\w{3,10}\) ((.+))$"), #removing instances of (2/bis) and similar from beginning of segments
    regex.compile(r"^[A-Z] \d\d?\) ((.+))$"),    # removing instances of "A 12) " at the beginning of segments
    regex.compile(r"^(([^“„'\"”]+))[“'\"”]$"),     # removing quotes at the end of segment (if no other quotes in segment)
    regex.compile(r"^[“„'\"](([^“„'\"”]+))$"),     # removing quotes at the beginning of segment (if no other quotes in segment)
    regex.compile(r"^[IVX]{1,4}\.([A-Z]\.|\d\)) (.+)$"), # removing list markers with roman numeral and uppercase letter like "II.D." and "II.2)"
    regex.compile(r"^((.+))(>| \*\))$"), # removing ">" and " *)" from end of segments
    regex.compile(r"^\d\d?\.\d\d?\.\d\d?(\.\d\d?)? ?(([A-Z].+))$")   # removing "1.1.1" and "1.1.1.1" at the beginning of segments (with or without spaces)
]

'''A second segment cleaning stage.'''      # works
def noise_cleaning(path, regexes):
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
    tree.write(path, encoding="UTF-8")
    print("%i segments cleaned." % counter_cleaned)
    print()


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
    tree.write(path, encoding="UTF-8")
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
    tree.write(path, encoding="UTF-8")              # overwriting the old file
    print("\n\n%i segments cleaned from whitespaces and other noise.\n\n" % counter_whi)
    print()


'''Printing single TUs with wrong detected language; user input to retain or eliminate the TU'''
def select_TUs_with_wrong_lang(path):
    nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}
    tree = etree.parse(path)
    root = tree.getroot()
    body = root.find("body")
    counter = 0  # for testing purposes
    for tu in root.iter("tu"):
        source_segment = tu.find("./tuv[@xml:lang='IT']/seg", namespaces=nsmap).text
        target_segment = tu.find("./tuv[@xml:lang='DE']/seg", namespaces=nsmap).text
        try:
            detect_it = detect(source_segment)
            detect_de = detect(target_segment)
        except:
            continue
        if "de" in detect_it or "it" in detect_de:    # broader alternative (every language other than it or de) => if "it" not in detect_it or "de" not in detect_de:
            if len(source_segment.split()) > 8 and len(target_segment.split()) > 8: # just considering longer segments, shorter ones are more likely to be false positives, and they will be deleted anyway
                counter += 1
                print(counter)
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
    print(counter)

'''Printing single TUs with significant length difference; user input to retain or eliminate the TU'''
def select_TUs_with_different_lenght(path):
    nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}
    tree = etree.parse(path)
    root = tree.getroot()
    body = root.find("body")
    count = 0
    for tu in root.iter("tu"):
        source_segment = tu.find("./tuv[@xml:lang='IT']/seg", namespaces=nsmap).text
        target_segment = tu.find("./tuv[@xml:lang='DE']/seg", namespaces=nsmap).text
        li = [len(source_segment), len(target_segment)]
        li.sort(reverse=True)
        len_ratio = li[0] / li[1]
        if len(source_segment) > 60 and len(target_segment) > 60:       # may be useful to tweak these value and the following
            if len(source_segment) > len(target_segment) and len_ratio > 2:
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
    tree.write(path, encoding="UTF-8")              # overwriting the old file


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





''' LET'S CLEAN! Activate desired cleaning operations (respect this order). Could require more than one re-run 
(at least 3/4 times, until no more cleaning operations are carried out) '''

#remove_untranslated(tmx_path)

#remove_art_and_co(tmx_path)

#remove_punctuation_numeral_segments(tmx_path)

noise_cleaning(tmx_path, patterns)

#remove_whitespaces(tmx_path)

#select_TUs_with_wrong_lang(tmx_path)                # manual selection

#select_TUs_with_different_lenght(tmx_path)         # manual selection

#remove_blank_units(tmx_path)

#segment_counter(tmx_path)

print("Done!")