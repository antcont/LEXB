'''
LexScraper_tm

    Given a list of URLs, for each URL:
        - parsing the HTML
        - extracting law title, subtitle and body and printing it to a .txt file
        - creating a .csv report file.
'''
import argparse
import urllib3
from urllib3.util import Retry
import os
import sys
sys.path.append('../')
from full.LexScraper_full import get_soup, get_title, get_title_type, get_body


retries = Retry(connect=5, read=2, redirect=5)                     # trying to reconnect to the website in case of error
http = urllib3.PoolManager(retries=retries)

#  define cmd arguments
parser = argparse.ArgumentParser(description="Script for scraping text from LexBrowser (without annotation).")
parser.add_argument("urlList", help="a txt file of newline-separated URLs to be scraped")
parser.add_argument("language", help="the language code (it or de)")
args = parser.parse_args()

#  processing arguments
urlList = args.urlList
language = args.language


def scraper_tm(urlList, language):
    # creating a new directory for the scraped texts
    newdir = "./" + language
    try:
        os.mkdir(newdir)
    except:
        print("Directory %s already existing" % newdir)
        exit()
    else:
        print("Successfully created the directory %s " % newdir)

    for id, url in enumerate(urlList):
        soup = get_soup(url)
        title = get_title(soup)
        title_type = get_title_type(soup)
        body, detected_lang, body_len = get_body(soup)
        if language not in detected_lang or not body or not title:
            continue
        else:
            text = "\n".join([title, title_type, body])
            newfile_path = newdir + "\STPLC_%s_%s.txt" % (language, str(id).zfill(4))  # building filename as "STPLC_it_0000"
            with open(newfile_path, "w", encoding="utf-8", newline="\n") as file:
                file.write(text)
                print("\r", "%i / %i (%.2f%%)" % (id + 1, len(urlList), (id + 1) * 100 / len(urlList)),
                      end="")  # printing progress


if __name__ == '__main__':
    with open(urlList, "r") as f:        # URL list is a .txt file with one URL per line
        URL_list = f.read().splitlines()

        scraper_tm(URL_list, language)

    print("\rDone!")
