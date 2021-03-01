'''
TODO: still have to test it (used LexBrowser_IT and LexBrowser_DE for my corpus)

LexScraper_tm

    Given a list of URLs, for each URL:
        - parsing the HTML
        - extracting law title, subtitle and body and printing it to a .txt file
        - creating a .csv report file.
'''

import urllib3
from bs4 import BeautifulSoup
from urllib3.util import Retry
import re
import pandas as pd
from langdetect import detect
from LexScraper_full import get_soup, get_title, get_title_type, get_body

retries = Retry(connect=5, read=2, redirect=5)                     # trying to reconnect to the website in case of error
http = urllib3.PoolManager(retries=retries)

url_list = r"C:\Users\anton\Desktop\lista_URL_IT.txt"
language = "it"     #it or de
export_folder = r"C:\Users\anton\Dropbox\Eurac_tesi"


def scraper_tm(url_list, lang, export_folder):
    for id, url in enumerate(url_list):
        soup = get_soup(url)
        title = get_title(soup)
        title_type = get_title_type(soup)
        body, detected_lang, body_len = get_body(soup)
        if lang not in detected_lang or not body or not title:
            continue
        else:
            print("ok")
            text = "\n".join([title, title_type, body])
            newfile_path = export_folder + "\STPLC_%s_%s.txt" % (lang, str(id).zfill(4))  # building filename as "STPLC_it_0000"
            #with open(newfile_path, "w", encoding="utf-8", newline="\n") as file:
                #file.write(text)


with open(url_list, "r") as f:        # URL list is a .txt file with one URL per line
    URL_list = f.read().splitlines()
    scraper_tm(URL_list, language, export_folder)


print("\nDone!")