'''
    Given a list of URLs, for each URL:
        - parsing the HTML
        - extracting law title, subtitle and body
            - law title is checked against a blacklist of terms and, if it contains any, the text is discarded
        - printing it to a .txt file
        - creating a .csv report file.
'''

import urllib3
from bs4 import BeautifulSoup
from urllib3.util import Retry
import re
import pandas as pd
from langdetect import detect

retries = Retry(connect=5, read=2, redirect=5)                   # trying to reconnect to the website in case of error
http = urllib3.PoolManager(retries=retries)

url_list = r""
export_folder = r""


with open(url_list, "r") as f:        # URL list is a .txt file with one URL per line
    URL_list = f.read().splitlines()

''' blacklist for terms in DE title (if there, text is not in German) '''
blacklist = ["Delibera",
             "Decreto",
             "Ordinanza",
             "Legge"]

def scraper(URL_list, export_folder):
    columns = ["file", "URL", "title", "detected language", "download"]     # columns for the csv report file
    df_ = pd.DataFrame(columns=columns)                                     # creating a dataframe for the report file
    for id, url in enumerate(URL_list):                     # iterating over URL list; 'id' will be part of the filename
        html = http.request('GET', url).data                                # making 'get' request and getting data
        soup = BeautifulSoup(html, features="lxml")                         # setting up BeautifulSoup
        text_as_list = []                                                   # building the scraped text as a list
        title_ = soup.find(class_='tit_doc')                                # scraping the title
        if title_ is not None:
            title = title_.get_text(strip=True)                             # adding the title and stripping whitespaces
            if any(term in title for term in blacklist):                    # checking if blacklisted term in DE title
                print("ERROR: STPLC_DE_%(text_id)s.txt not downloaded (filtered out). URL: %(url)s " % {"text_id": str(id).zfill(4),
                                                                                         "url": url})
                df_.loc[len(df_.index)] = ["ERROR! No text downloaded: STPLC_DE_%s.txt" % str(id).zfill(4), url, title,
                                           "-", "ERROR: filtered out"]      # info on report file
                continue
            else:
                text_as_list.append(title)                                  # adding law title
        subtitle_ = soup.find(class_='descr_doc')                           # scraping the subtitle
        if subtitle_ is not None:
            text_as_list.append(subtitle_.get_text(strip=True))             # adding the subtitle, if there
        find_body = soup.find(class_="documentoesteso").find_all(re.compile("(p(?!a)|li|h2)"))      # scraping the body
        if find_body is not None:
            for p in find_body:
                for br in p.find_all("br"):
                    br.replace_with("\n")                                   # replacing </br> tags with newline
                body = p.get_text().strip()                                 # getting text and stripping whitespaces
                if body:                                                    # discarding empty lines
                    text_as_list.append(body)                               # adding text from law body
        text_as_string = "\n".join(text_as_list)                            # joining text as list in a string
        if not text_as_string:                                              # raising error message if text is empty
            print("ERROR: STPLC_DE_%(text_id)s.txt not downloaded (empty). URL: %(url)s " % {"text_id": str(id).zfill(4), "url": url})
            df_.loc[len(df_.index)] = ["ERROR! No text downloaded: STPLC_DE_%s.txt" % str(id).zfill(4), url, title,
                                       "-", "ERROR: empty"]                 # adding error info on report file
        else:
            detected_lang = detect(text_as_string)                          # detecting text language
            newfile_path = export_folder + "\STPLC_DE_%s.txt" % str(id).zfill(4)  # building filename as "STPLC_DE_0000"
            with open(newfile_path, "w", encoding="utf-8", newline="\n") as file:
                file.write(text_as_string)                                  # writing .txt file
            print("[%(id)i/%(tot)i] %(url)s downloaded to %(filename)s" % {"id": id+1, "tot": len(URL_list), "url": url, "filename": newfile_path})
            df_.loc[len(df_.index)] = ["STPLC_DE_%s.txt" % str(id).zfill(4), url, title, detected_lang, "OK"] # info on report file
    export_path_report = export_folder + "/report.csv"                      # building filepath for the report file
    df_.to_csv(export_path_report, sep=";", header=True, index=False)       # export report as .csv

scraper(URL_list, export_folder)


print("\nDone!")