'''
URLs_collection.py

 Creating a comma-separated file of parallel (German and Italian) URLs of all laws contained in the LexBrowser database;
 exporting two separate (parallel) lists of URLs to be used for scraping.

'''

import urllib3
from bs4 import BeautifulSoup
from urllib3.util import Retry
import pandas as pd

retries = Retry(connect=10, read=10, redirect=10)                  # trying to reconnect to the website in case of error
http = urllib3.PoolManager(retries=retries)

url_domain = "http://lexbrowser.provinz.bz.it"

''' retrieving links of (Italian) law collection for each year '''
html = http.request('GET', "http://lexbrowser.provinz.bz.it/chrono/it/").data    # sending request and getting data
soup = BeautifulSoup(html, features="lxml")                                      # setting up BeautifulSoup
list_years = []                                              # putting URLs of each year's law catalogue in a list
section = soup.find(id="documento")                          # searching in the HTML for the section containing the URLs
for link in section.find_all("a"):
    list_years.append(url_domain + link.get('href'))     # getting absolute links by appending local links to the domain

print("\nCollecting Italian URLs...")

IT_URLs = []                                             # getting URLs for all Italian laws and putting them in a list
for year in list_years:
    html = http.request('GET', year).data
    soup = BeautifulSoup(html, features="lxml")
    section = soup.find(id="documento")
    for link in section.find_all("a"):
        IT_URLs.append(url_domain + link.get('href'))

print("\nGetting German URLs and pairing...")

''' blacklist of terms that identify untranslated text pairs '''
blacklist = ["Corte costituzionale",
             "TAR",
             "T.A.R.",
             "Verwaltungsgericht",
             "Verfassungsgerichtshof",
             "Sentenza",
             "Beschluss"]

''' pairing URLs based on link from one law to another, by changing language (switch to DE) '''
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
    ''' filtering out untranslated laws by strings contained in law title '''
    law_title = soup.title.string                                                                  # getting IT title
    if any(term in law_title for term in blacklist):                        # checking if blacklisted terms in IT title
        print("%s discarded because Italian law title contains blacklisted term (probably untranslated text)" % it_URL)
    else:
        de_URL = url_domain + de_URL_loc + "?view=1"                            # building complete URL of German laws
        paired_URLs[it_URL] = de_URL                                            # adding pair of IT and DE URLs to dict
        print("%(id)i out of %(tot)i URLs processed." % {"id": id+1, "tot": len(IT_URLs)})

print("\nExporting as CSV...")

''' exporting paired list of URLs as .csv file '''
pd.DataFrame.from_dict(data=paired_URLs, orient='index').to_csv('parallel_URLs.csv', sep=";", header=False)

''' exporting the separate lists of URLs as .txt files '''
it_list = []
de_list = []
for it, de in paired_URLs.items():               
    it_list.append(it)
    de_list.append(de)
it_txt = "\n".join(it_list)
de_txt = "\n".join(de_list)

with open("it_URLs.txt", "w", encoding="utf-8", newline="\n") as file:          # writing .txt with IT URLs
    file.write(it_txt)
with open("de_URLs.txt", "w", encoding="utf-8", newline="\n") as file:          # writing .txt with DE URLs
    file.write(de_txt)

print("\nDone!")