'''
Arguments are a txt file with a newline-separated list of URLs to be scraped and the language code.
'''

import argparse
import os
import urllib3
from bs4 import BeautifulSoup
from urllib3.util import Retry
import regex as re
import pandas as pd
from langdetect import detect
import langid
from xml.sax.saxutils import escape, unescape, quoteattr


def get_soup(url):
    '''
    retries = Retry(connect=10, read=10, redirect=10)  # trying to reconnect to the website in case of error
    http = urllib3.PoolManager(retries=retries)
    html = http.request('GET', url).data
    soup = BeautifulSoup(html, features="lxml")
    '''
    soup = BeautifulSoup(((urllib3.PoolManager(retries=(Retry(connect=10, read=10, redirect=10))))
                          .request('GET', url).data), features="lxml")
    return soup


def get_title(soup):
    '''
    Getting the actual title of the law.
    '''
    title_ = soup.find(class_='descr_doc')  # scraping the subtitle
    if title_ is None:
        title = "NA"
    if title_ is not None:
        title = escape(unescape(title_.get_text(strip=True)))
        title = title.replace("\"", "&quot;")
        # removing notes from the end if preceded by letter and nospace
        remove_note = re.search("^(.+)(?<=\p{L}|\))\d\)$", title)
        if remove_note:
            title = remove_note.group(1)
    return title


def get_title_type(soup):
    '''
    Getting title_type ("Delibera 19 gennaio 2021, n. 19")
    '''
    try:
        titletype_ = (soup.find(class_="mappapercorsosito").find_all("a"))[-1]  # getting the last "a" element in "mappapercorsosito" class
    except IndexError:
        titletype_ = (soup.find(class_="mappapercorsosito").find("a"))  # exception when there is only title in "mappapercorsosito"
    except AttributeError:
        print("mappapercorsosito None?")
        title_type = "NA"
    if titletype_ is None:
        title_type = "NA"
    if titletype_ is not None:
        # escaping XML special characters (& < > ") and trimming whitespaces
        titletype = escape(unescape(titletype_.get_text(strip=True)))
        title_type = titletype.replace("\"", "&quot;")
    return title_type


def get_date(title_type):
    month_convert = {"gennaio": "01", "febbraio": "02", "marzo": "03", "aprile": "04", "maggio": "05", "giugno": "06",
                     "luglio": "07",
                     "agosto": "08", "settembre": "09", "ottobre": 10, "novembre": 11, "dicembre": 12, "Jänner": "01",
                     "Januar": "01", "Februar": "02", "März": "03", "April": "04", "Mai": "05", "Juni": "06",
                     "Juli": "07", "August": "08", "September": "09", "Oktober": 10, "November": 11, "Dezember": 12}
    date_match = re.search(r"(\d\d?)\.?°? ?([Gg]ennaio|[Ff]ebbraio|[Mm]arzo|[Aa]prile|[Mm]aggio|[Gg]iugno|[Ll]uglio|[Aa]gosto|[Ss]ettembre|[Oo]ttobre|[Nn]ovembre|[Dd]icembre|[Jj]änner|[Jj]anuar|[Ff]ebruar|[Mm]ärz|[Aa]pril|[Mm]ai|[Jj]uni|[Jj]uli|[Aa]ugust|[Ss]eptember|[Oo]ktober|[Nn]ovember|[Dd]ezember) (\d{4})", title_type)
    date_match2 = re.search(r"(Delibera)  ? ?N\. \d{1,6}  ?(del|vom)  ?(\d\d?)\.(\d\d)\.(\d{4})$", title_type)

    if date_match2:
        day = date_match2.group(3)
        if len(day) == 1:
            day = "0" + day
        drafting_date = "%s/%s/%s" % (day, date_match2.group(4), date_match2.group(5))

    elif date_match:
        day = date_match.group(1)
        if len(day) == 1:
            day = "0" + day
        month = date_match.group(2)
        year = date_match.group(3)
        for m in month_convert.keys():
            if month.lower() == m.lower():
                month_number = month_convert[m]
        drafting_date = "%s/%s/%s" % (day, month_number, year)

    else:
       drafting_date = "NA"

    return drafting_date


def get_text_type(title_type):
    type_search = re.search(
        r"^([\p{L} ']+) ?(del|vom)? ?(\d\d?°?\.? ([Gg]ennaio|[Ff]ebbraio|[Mm]arzo|[Aa]prile|[Mm]aggio|[Gg]iugno|[Ll]uglio|[Aa]gosto|[Ss]ettembre|[Oo]ttobre|[Nn]ovembre|[Dd]icembre|[Jj]änner|[Jj]anuar|[Ff]ebruar|[Mm]ärz|[Aa]pril|[Mm]ai|[Jj]uni|[Jj]uli|[Aa]ugust|[Ss]eptember|[Oo]ktober|[Nn]ovember|[Dd]ezember))",
        title_type)
    type_search2 = re.search(r"(Delibera|Beschluss)  ? ?Nr?\. ? \d°?\d{0,6}  ?(del|vom) ? (\d\d?\.\d\d\.\d{4})$",
                             title_type)
    type_search3 = re.search(r"^([\p{L} ]+)\d\d?$", title_type)
    if type_search:
        text_type = type_search.group(1).strip()
    elif type_search2:
        text_type = type_search2.group(1).strip()
    elif type_search3:
        text_type = type_search3.group(1).strip()
    else:
        text_type = title_type
    # exceptions for "Decreto del Presidente della Provincia31" and "Testo unico del"
    type_correct = re.search(r"^([\p{L} ]+) ?(del|vom)$", text_type)
    if type_correct:
        text_type = type_correct.group(1).strip()

    temp2type = {
        "Delibera": "Delibera della Giunta Provinciale / Beschluss der Landesregierung",
        "Deliberazione della Giunta Provinciale": "Delibera della Giunta Provinciale / Beschluss der Landesregierung",
        "Beschluss des Landtages": "Delibera della Giunta Provinciale / Beschluss der Landesregierung",
        "Beschluss der Landesregierung": "Delibera della Giunta Provinciale / Beschluss der Landesregierung",
        "Parere": "Parere / Gutachten",
        "Costituzione della Repubblica Italiana": "Costituzione della Repubblica Italiana / Verfassung der Republik Italien",
        "Verfassung der Republik Italien": "Costituzione della Repubblica Italiana / Verfassung der Republik Italien",
        "Circolare": "Circolare / Rundschreiben",
        "Rundschreiben": "Circolare / Rundschreiben",
        "Decreto del Presidente della Repubblica": "Decreto del Presidente della Repubblica / Dekret des Präsidenten der Republik",
        "Dekret des Präsidenten der Republik": "Decreto del Presidente della Repubblica / Dekret des Präsidenten der Republik",
        "Decreto legislativo": "Decreto legislativo / Gesetzesvertretendes Dekret",
        "Legislativdekret": "Decreto legislativo / Gesetzesvertretendes Dekret",
        "Gesetzesvertretendes Dekret": "Decreto legislativo / Gesetzesvertretendes Dekret",
        "Decreto del Presidente della Provincia": "Decreto del Presidente della Provincia / Dekret des Landeshauptmanns",
        "Decreto del Presidente della Giunta Provinciale": "Decreto del Presidente della Provincia / Dekret des Landeshauptmanns",
        "Dekret des Präsidenten des Landesausschusses": "Decreto del Presidente della Provincia / Dekret des Landeshauptmanns",
        "Decreto": "Decreto / Dekret",
        "Dekret": "Decreto / Dekret",
        "Legge provinciale": "Legge Provinciale / Landesgesetz",
        "Landesgesetz": "Legge Provinciale / Landesgesetz",
        "Legge": "Legge statale / Staatsgesetz",
        "Gesetz": "Legge statale / Staatsgesetz",
        "Contratto collettivo": "Contratto collettivo / Kollektivvertrag",
        "Kollektivvertrag": "Contratto collettivo / Kollektivvertrag",
        "Decreto del direttore di Ripartizione": "Decreto del Direttore di Ripartizione / Dekret des Abteilungsdirektors",
        "Dekret des Abteilungsdirektors": "Decreto del Direttore di Ripartizione / Dekret des Abteilungsdirektors",
        "Legge costituzionale": "Legge costituzionale / Verfassungsgesetz",
        "Verfassungsgesetz": "Legge costituzionale / Verfassungsgesetz",
        "Accordo": "Accordo / Vertrag",
        "Vertrag": "Accordo / Vertrag",
        "Contratto di comparto": "Contratto di comparto / Bereichsabkommen",
        "Bereichsabkommen": "Contratto di comparto / Bereichsabkommen",
        "Bereichsvertrag": "Contratto di comparto / Bereichsabkommen",
        "Contratto collettivo intercompartimentale": "Contratto collettivo intercompartimentale / Bereichsübergreifender Kollektivvertrag",
        "Bereichsübergreifender Kollektivvertrag": "Contratto collettivo intercompartimentale / Bereichsübergreifender Kollektivvertrag",
        "Decreto del Direttore dell'Agenzia per la protezione civile": "Decreto del Direttore dell'Agenzia per la protezione civile / Dekret des Direktors der Agentur für Bevölkerungsschutz",
        "Dekret des Direktors der Agentur für Bevölkerungsschutz": "Decreto del Direttore dell'Agenzia per la protezione civile / Dekret des Direktors der Agentur für Bevölkerungsschutz",
        "Deliberazione del consiglio provinciale": "Deliberazione del Consiglio provinciale / Beschluss des Landtages",
        "Decreto dell'Assessore per l'agricoltura e le foreste": "Decreto dell'Assessore per l'agricoltura e le foreste / Dekret des Assessors für Landwirtschaft und Forstwesen",
        "Dekret des Assessors für Landwirtschaft und Forstwesen": "Decreto dell'Assessore per l'agricoltura e le foreste / Dekret des Assessors für Landwirtschaft und Forstwesen",
        "Modifiche del regolamento sull'assistenza economica sociale e sulle tariffe dei servizi sociali 2012": "Decreto del Presidente della Provincia / Dekret des Landeshauptmanns",
        "Änderungen der Verordnung über die finanzielle Sozialhilfe und die Tarife der Sozialdienste 2012": "Decreto del Presidente della Provincia / Dekret des Landeshauptmanns",
        "Dekret des Landeshauptmanns": "Decreto del Presidente della Provincia / Dekret des Landeshauptmanns",
        "Beschluss": "Delibera della Giunta Provinciale / Beschluss der Landesregierung",
        "Accordo di Parigi": "Accordo di Parigi / Pariser Vertrag",
        "Pariser Vertrag": "Accordo di Parigi / Pariser Vertrag",
        "Testo unico": "Testo unico / Einheitstext",
        "Einheitstext": "Testo unico / Einheitstext"
    }

    for temp in temp2type.keys():
        if temp.lower() == text_type.lower():
            text_type = temp2type[temp]

    if not any(text_type.lower() == val.lower() for val in temp2type.values()):
        print("Exception found. Handle it.")
        print(text_type)
        pass

    return text_type


def get_topic(soup):
    topic_macro = "NA"
    topic_micro = "NA"
    where_topic = soup.find(class_="mappapercorsosito").find_all("a")
    if len(where_topic) == 2:
        pass
    if len(where_topic) == 3:
        topic_macro = where_topic[1].get_text(strip=True)
    if len(where_topic) == 4:
        topic_macro = where_topic[1].get_text(strip=True)
        topic_micro = where_topic[2].get_text(strip=True)
    if topic_micro.isdigit() or len(topic_micro) <= 2:
        topic_micro = "NA"
    if topic_macro.isdigit() or len(topic_micro) <= 2:
        topic_macro = "NA"
    return topic_macro, topic_micro


def get_year_decade(drafting_date):
    if drafting_date == "NA":
        decade = "NA"
        year = "NA"
    else:
        year = drafting_date[-4:]
        decade = year[:3] + "0"
    return year, decade


def get_body(soup):
    body_list = []
    find_body = soup.find(class_="documentoesteso").find_all(re.compile("(p(?!a)|li|h2)"))  # scraping for the body
    if find_body is not None:
        for p in find_body:
            for br in p.find_all("br"):
                br.replace_with("\n")  # replacing </br> tags with newline
            body_line = p.get_text().strip()  # getting text and stripping whitespaces
            if body_line:
                body_list.append(body_line)
    body_len = len(body_list)
    body = "\n".join(body_list)
    langid.set_languages(['de', 'it'])
    detected_lang = langid.classify(body)  # detecting text language
    return body, detected_lang, body_len


def scraper(url_list, lang):
    '''
    "Alexa, play '(sc)rape me' by Nirvana."
    '''
    text_type_set = set()
    columns = ["file", "URL", "title", "download"]
    df_ = pd.DataFrame(columns=columns)

    # creating a new directory for the scraped texts
    newdir = "./" + language
    try:
        os.mkdir(newdir)
    except:
        print("Directory %s already existing" % newdir)
        exit()
    else:
        print("Successfully created the directory %s " % newdir)

    for id, url in enumerate(url_list):
        soup = get_soup(url)
        title = get_title(soup)
        title_type = get_title_type(soup)
        drafting_date = get_date(title_type)
        text_type = get_text_type(title_type)
        text_type_set.add(text_type)
        macro_topic, micro_topic = get_topic(soup)
        year, decade = get_year_decade(drafting_date)
        body, detected_lang, body_len = get_body(soup)
        text_tag = '<text title="%s" title_type="%s" type="%s" drafting_date="%s" year="%s" decade="%s"' \
                   ' macro_topic="%s" micro_topic="%s">' \
                   % (title, title_type, text_type, drafting_date, year, decade, macro_topic, micro_topic)
        ''' 
        discarding text if: 
        wrong detected language; text body absent; text body shorter than 6 lines (abrogated); all metadata "NA" (empty)
        '''
        if lang not in detected_lang or not body or text_tag == '<text title="NA" title_type="NA" type="NA" drafting_date="NA" year="NA" decade="NA" macro_topic="NA" micro_topic="NA">':
            df_.loc[len(df_.index)] = ["ERROR! No text downloaded: STPLC_%s_%s.txt" % (lang, str(id).zfill(4)), url, title_type, "ERROR: empty"]
            continue

        else:
            text = "\n".join([text_tag, title, title_type, escape(unescape(body)), "</text>"])
            filepath = newdir + "/STPLC_%s_%s.txt" % (lang, str(id).zfill(4))            # building filename as "STPLC_it_0000"
            with open(filepath, "w", encoding="utf-8", newline="\n") as file:
                file.write(text)
            df_.loc[len(df_.index)] = ["STPLC_%s_%s.txt" % (lang, str(id).zfill(4)) , url, title_type, "OK"]  # info on report file #reindent under file.write!
        print("\r", "%i / %i (%.2f%%)" % (id+1, len(url_list), (id+1)*100/len(url_list)), end="")     #printing progress

    df_.to_csv("report.csv", sep=";", header=True, index=False)   # export report file as .csv
    print(text_type_set)




if __name__ == "__main__":
    #  define cmd arguments
    parser = argparse.ArgumentParser(
        description="A scraper for texts from the LexBrowser.\nStructural and contextual information are annotated.")
    parser.add_argument("URL_list", help="a newline-separated txt file of URLs to be scraped")
    parser.add_argument("language", help="the language code of the texts (it|de)")
    args = parser.parse_args()

    #  processing arguments
    url_list = args.URL_list
    language = args.language

    with open(url_list, "r") as f:  # URL list is a .txt file with one URL per line
        URL_list = f.read().splitlines()

    scraper(URL_list, language)

    print("Done.")
