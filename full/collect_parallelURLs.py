'''

 Creating a comma-separated file of parallel (German and Italian) URLs of all laws contained in the LexBrowser database;
 exporting two separate (parallel) txt .lists of URLs to be used for scraping.

 update 23.02.2021: New blacklist-based filtering.

'''

import argparse
import urllib3
from bs4 import BeautifulSoup
from urllib3.util import Retry
import pandas as pd

parser = argparse.ArgumentParser(description="Creating a comma-separated file of parallel (German and Italian) URLs"
                                             " of all laws contained in the LexBrowser database;\nexporting two"
                                             " separate (parallel) txt .lists of URLs to be used for scraping.")
args = parser.parse_args()


retries = Retry(connect=10, read=10, redirect=10)                  # trying to reconnect to the website in case of error
http = urllib3.PoolManager(retries=retries)

url_domain = "http://lexbrowser.provinz.bz.it"

#  retrieving links of (Italian) law collection for each year
html = http.request('GET', "http://lexbrowser.provinz.bz.it/chrono/it/").data    # sending request and getting data
soup = BeautifulSoup(html, features="lxml")                                      # setting up BeautifulSoup
list_years = []                                              # putting URLs of each year's law catalogue in a list
section = soup.find(id="documento")                          # searching in the HTML for the section containing the URLs
for link in section.find_all("a"):
    list_years.append(url_domain + link.get('href'))     # getting absolute links by appending local links to the domain

print("Collecting Italian URLs...")


IT_URLs = []                                             # getting URLs for all Italian laws and putting them in a list
for year in list_years:
    html = http.request('GET', year).data
    soup = BeautifulSoup(html, features="lxml")
    section = soup.find(id="documento")

    for link in section.find_all("a"):
        IT_URLs.append(url_domain + link.get('href'))

print("\nGetting German URLs and filtering out untraslated...")


#  blacklist of terms that identify untranslated text pairs
#  Corte costituzionale: these are almost never translated to German, still, the "German" version (with Italian text)
#  may be on the LexBrowser;
#  Verwaltungsgericht: sometimes they just translate the title, but the text is in Italian
#  Beschluss: actually some of these are in both languages, but the title remained in German
#  (s. http://lexbrowser.provinz.bz.it/doc/it/6337/beschluss_n_2913_del_14_12_2009.aspx)
blacklist_it = ["Corte costituzionale",
             "TAR",
             "T.A.R.",
             "Verwaltungsgericht",
             "Verfassungsgerichtshof",
             "Sentenza",
             "Beschluss"]

blacklist_de = ["Delibera",
                 "Decreto",
                 "Ordinanza",
                 "Legge"]


#  pairing URLs based on link from one law to another, by changing language (switch to DE)
paired_URLs = {}
for id, it_URL in enumerate(IT_URLs):
    if "?view=1" not in it_URL:                       # "?view=1" at the end of the URL indicates the full document view
        it_URL = it_URL + "?view=1"
    html = http.request('GET', it_URL).data                                     # making 'get' request and getting data
    soup = BeautifulSoup(html, features="lxml")                                            # setting up BeautifulSoup
    section = soup.find(id="ContentPlaceHolder1_lnkLangDE", class_="lingua noselezionata")         # switch to German

    if section is None:
        print("%s discarded because no German version is available" % it_URL)
        continue
    de_URL_loc = section.get('href')                                                               # getting DE URL

    #  getting text title for blacklist-based filtering
    law_title_it = soup.title.string                                                                  # getting IT title
    if any(term in law_title_it for term in blacklist_it):                   # checking if blacklisted terms in IT title
        print("%s discarded because Italian law title contains blacklisted term (probably untranslated text)" % it_URL)

    else:
        de_URL = url_domain + de_URL_loc + "?view=1"                            # building complete URL of German laws
        html = http.request('GET', de_URL).data
        soup = BeautifulSoup(html, features="lxml")
        law_title_de = soup.title.string

        if any(term in law_title_de for term in blacklist_de):
            print("%s discarded because German law title contains blacklisted term (probably untranslated text)" %
                  de_URL)

        else:
            paired_URLs[it_URL] = de_URL                                         # adding pair of IT and DE URLs to dict
            print("\r", "%i out of %i URLs processed." % (id+1, len(IT_URLs)), end="")

print("\nExporting as CSV...")

#  exporting paired list of URLs as .csv file
pd.DataFrame.from_dict(data=paired_URLs, orient='index').to_csv('parallel_URLs_stplc_full.csv', sep=";", header=False)

#  exporting the separate lists of URLs as .txt files
it_list = []
de_list = []
for it, de in paired_URLs.items():               
    it_list.append(it)
    de_list.append(de)
it_txt = "\n".join(it_list)
de_txt = "\n".join(de_list)

#  writing URL lists
with open("it_URLs.txt", "w", encoding="utf-8", newline="\n") as file:
    file.write(it_txt)
with open("de_URLs.txt", "w", encoding="utf-8", newline="\n") as file:
    file.write(de_txt)

print("\nDone!")